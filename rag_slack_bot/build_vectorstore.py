import os
import shutil
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.docstore.document import Document
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from concurrent.futures import ThreadPoolExecutor, as_completed


load_dotenv()


GITHUB_REPO = os.getenv("GITHUB_REPO")
REPO_DIR = "repo_files"
VECTOR_STORE_DIR = "data/faiss_index"


def clone_repo(repo_url: str, repo_dir: str):
   if os.path.exists(repo_dir):
       print("🧹 Removing old repo...")
       shutil.rmtree(repo_dir)
   print(f"🔄 Cloning {repo_url} ...")
   os.system(f"git clone {repo_url} {repo_dir}")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def embed_with_retry(embeddings, texts):
   try:
       return embeddings.embed_documents(texts)
   except Exception as e:
       print(f"Embedding failed, retrying... Error: {str(e)}")
       time.sleep(2)
       raise


def process_batch(embeddings, batch_docs):
   texts = [d.page_content for d in batch_docs]
   embeddings_list = embed_with_retry(embeddings, texts)
   return texts, embeddings_list, [d.metadata for d in batch_docs]


def build_and_save_vectorstore():
   clone_repo(GITHUB_REPO, REPO_DIR)


   print("📂 Loading all repository files...")
   loader = DirectoryLoader(
       REPO_DIR,
       glob="**/*.*",
       loader_cls=TextLoader,
       use_multithreading=True
   )
   documents = loader.load()
   print(f"✅ Loaded {len(documents)} Java files")


   # Load predefined QA file
   print("📂 Loading predefined QA file...")
   qa_loader = TextLoader("predefined_qa.txt")
   qa_documents = qa_loader.load()
   documents.extend(qa_documents)
   print(f"✅ Loaded {len(qa_documents)} QA documents")


   if not documents:
       raise ValueError("No documents found in the repo or QA file.")


   print("✂️ Splitting documents...")
   splitter = RecursiveCharacterTextSplitter(
       chunk_size=300,
       chunk_overlap=100,
       separators=["\n\n", "\n", ".", "?", "!", ";", ":", " ", ""],
       length_function=len
   )
   docs = splitter.split_documents(documents)
  
   for doc in docs:
       doc.metadata["chunk_size"] = len(doc.page_content)
       # Set file type based on source
       if "path" in doc.metadata:
           if doc.metadata["path"].endswith(".java"):
               doc.metadata["file_type"] = "java"
           else:
               doc.metadata["file_type"] = "qa"
           doc.metadata["file_name"] = os.path.basename(doc.metadata["path"])
           doc.metadata["directory"] = os.path.dirname(doc.metadata["path"])
       else:
           # For QA documents
           doc.metadata["file_type"] = "qa"
           doc.metadata["file_name"] = "predefined_qa.txt"
           doc.metadata["directory"] = "."
  
   print(f"✅ Split into {len(docs)} text chunks")


   print("🧠 Generating embeddings using Gemini...")
   embeddings = GoogleGenerativeAIEmbeddings(
       model="models/embedding-001",
       google_api_key=os.getenv("GEMINI_API_KEY"),
       task_type="retrieval_query",
       title="Java Code Analysis"
   )


   print("Building FAISS index with parallel processing...")
   batch_size = 20  # Increased batch size
  
   # Load existing index if it exists
   if os.path.exists(VECTOR_STORE_DIR):
       print("📥 Loading existing FAISS index...")
       faiss_index = FAISS.load_local(
           VECTOR_STORE_DIR,
           embeddings,
           allow_dangerous_deserialization=True
       )
   else:
       faiss_index = None
  
   # Split docs into batches
   batches = [docs[i:i + batch_size] for i in range(0, len(docs), batch_size)]
  
   # Process batches in parallel
   with ThreadPoolExecutor(max_workers=4) as executor:
       future_to_batch = {
           executor.submit(process_batch, embeddings, batch): batch
           for batch in batches
       }


       for future in as_completed(future_to_batch):
           try:
               texts, embeddings_list, metadatas = future.result()
              
               if not faiss_index:
                   faiss_index = FAISS.from_embeddings(
                       text_embeddings=list(zip(texts, embeddings_list)),
                       embedding=embeddings,
                       distance_strategy="COSINE"
                   )
               else:
                   faiss_index.add_embeddings(
                       text_embeddings=list(zip(texts, embeddings_list)),
                       metadatas=metadatas
                   )
                  
               print(f"✓ Processed batch of {len(texts)} documents")
              
           except Exception as e:
               print(f"Error processing batch: {str(e)}")
               continue


   # Create directory if it doesn't exist
   os.makedirs("data", exist_ok=True)
  
   # Save the index
   faiss_index.save_local(VECTOR_STORE_DIR)
   print(f"✅ Vectorstore saved at {VECTOR_STORE_DIR}")


if __name__ == "__main__":
   build_and_save_vectorstore()


