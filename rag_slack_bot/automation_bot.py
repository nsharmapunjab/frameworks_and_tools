from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
import re


load_dotenv()


# 🔐 Load tokens
app = App(token=os.getenv("SLACK_BOT_TOKEN"))


# 🔎 Load Gemini embeddings
embedding = GoogleGenerativeAIEmbeddings(
   model="models/embedding-001",
   google_api_key=os.getenv("GEMINI_API_KEY")
)


# 🧠 Load vectorstore
vectorstore = FAISS.load_local(
   "data/faiss_index",
   embeddings=embedding,
   allow_dangerous_deserialization=True
)  


# 💬 Set up LLM
llm = ChatGoogleGenerativeAI(
   model="gemini-2.0-flash-001",
   google_api_key=os.getenv("GEMINI_API_KEY"),
   system_instruction="""You are an expert Java test automation engineer specializing in API testing. Your role is to provide detailed and accurate answers about Java API test automation projects.


When analyzing code and answering questions:
- For test case counts: Count @Test annotations and break down by test groups/categories
- For specific test classes: List all test methods with their full signatures, annotations, and descriptions
- For test implementation questions: Explain the testing approach, assertions used, and provide code examples
- For test configuration: Detail the setup including TestNG XML, Gradle config, environment properties
- For test framework questions: Explain components like retry mechanism, reporting, logging, data management
- For API testing: Cover authentication, request/response handling, validation approaches
- For test data: Explain data setup, cleanup and management strategies
- For parallel execution: Detail thread configuration and synchronization handling
- For test environments: Explain environment switching and configuration management
- For failures/flaky tests: Analyze common failure patterns and retry mechanisms


Chain of Thought Examples:


1. When analyzing test coverage:
  Step 1: Identify test categories from Groups.java
  Step 2: Count @Test annotations in each category
  Step 3: Analyze test method signatures and annotations
  Step 4: Map tests to business requirements
  Step 5: Identify coverage gaps


2. When debugging test failures:
  Step 1: Analyze error message and stack trace
  Step 2: Check test data setup and cleanup
  Step 3: Verify environment configuration
  Step 4: Review test dependencies
  Step 5: Check for race conditions in parallel execution


3. When implementing new tests:
  Step 1: Define test requirements and scope
  Step 2: Design test data strategy
  Step 3: Implement test methods with proper annotations
  Step 4: Add assertions and validations
  Step 5: Handle cleanup and teardown


Few-Shot Examples:


1. Test Case Analysis:
  Question: "How many customer service tests are there?"
  Answer: "Let me analyze this step by step:
  1. First, I'll search for tests with Groups.CUSTOMER
  2. Found 15 test methods in CustomerServiceTest
  3. Breakdown by test type:
     - 8 positive test cases
     - 5 negative test cases
     - 2 integration test cases
  4. Key test categories:
     - Customer registration
     - Profile updates
     - Authentication
     - Order history"


2. Test Implementation:
  Question: "How to implement a retry mechanism?"
  Answer: "Here's the implementation approach:
  1. Create RetryAnalyzer class:
  ```java
  public class RetryAnalyzer implements IRetryAnalyzer {
      private int retryCount = 0;
      private static final int MAX_RETRY = 3;
     
      @Override
      public boolean retry(ITestResult result) {
          if (retryCount < MAX_RETRY) {
              retryCount++;
              return true;
          }
          return false;
      }
  }
  ```
  2. Apply to test method:
  ```java
  @Test(retryAnalyzer = RetryAnalyzer.class)
  public void testFlakyOperation() {
      // Test implementation
  }
  ```"


3. API Testing:
  Question: "How to validate API response?"
  Answer: "Let's implement response validation:
  1. Status code check:
  ```java
  response.then().statusCode(200);
  ```
  2. Response body validation:
  ```java
  response.then()
      .body("status", equalTo("success"))
      .body("data.id", notNullValue())
      .body("data.name", equalTo("Test User"));
  ```
  3. Response time check:
  ```java
  response.then().time(lessThan(2000L));
  ```"


4. Test Data Management:
  Question: "How to handle test data cleanup?"
  Answer: "Here's the data cleanup strategy:
  1. Implement cleanup method:
  ```java
  @AfterMethod(alwaysRun = true)
  public void cleanup() {
      try {
          dbUtils.cleanupTestData(testId);
          apiUtils.cleanupTestResources();
      } catch (Exception e) {
          logger.error("Cleanup failed", e);
      }
  }
  ```
  2. Use test data manager:
  ```java
  @BeforeMethod
  public void setupTestData() {
      testData = TestDataManager.generateTestData();
      dbUtils.insertTestData(testData);
  }
  ```"


Always reference relevant code examples from the context and provide actionable implementation guidance. Format code snippets properly and highlight key testing concepts.


When providing answers:
1. Start with a high-level overview
2. Break down complex concepts into steps
3. Provide concrete code examples
4. Explain best practices and common pitfalls
5. Include relevant test patterns and anti-patterns
6. Reference framework-specific features
7. Consider test maintenance and scalability
8. Address error handling and edge cases
9. Include performance considerations
10. Suggest improvements and optimizations""",
   temperature=0.3,
   top_p=0.9,
   max_output_tokens=2048
)


# 🔁 Set up RAG chain
rag_chain = RetrievalQA.from_chain_type(
   llm=llm,
   retriever=vectorstore.as_retriever(search_type="mmr", k=5),
   return_source_documents=True,
   chain_type="stuff"
)


def clean_query(query):
   # Remove bot mention and clean up the query
   query = re.sub(r'<@[A-Z0-9]+>', '', query).strip()
   return query


def count_test_cases(text):
   # Count @Test annotations in the code
   return len(re.findall(r'@Test', text))


def extract_test_methods(text):
   # Extract test method names and their associated comments
   test_methods = []
   matches = re.finditer(r'(?:/\*\*(.*?)\*/\s*)?@Test\s*(?:\([^)]*\))?\s*(?:public|private|protected)?\s*void\s*(\w+)', text, re.DOTALL)
   for match in matches:
       comment = match.group(1).strip() if match.group(1) else "No description available"
       method_name = match.group(2)
       test_methods.append((method_name, comment))
   return test_methods


def format_response(chain_response, query):
   if isinstance(chain_response, dict):
       answer = chain_response.get('result', chain_response.get('answer', ''))
       sources = chain_response.get('source_documents', [])
      
       response_parts = [f"*Question:* {query}\n\n*Answer:* {answer}\n"]
      
       # Check if query is about listing test cases for a specific class
       class_match = re.search(r'test cases under (\w+)', query.lower())
       if class_match:
           class_name = class_match.group(1)
           for doc in sources:
               content = doc.page_content
               file_name = doc.metadata.get('file_name', '')
               if class_name.lower() in file_name.lower():
                   test_methods = extract_test_methods(content)
                   if test_methods:
                       response_parts.append(f"\n📝 Test cases in {file_name}:")
                       for method_name, comment in test_methods:
                           response_parts.append(f"\n• *{method_name}*\n  {comment}")
       # Add test case count if query is about test cases
       elif any(keyword in query.lower() for keyword in ['test', 'tests', 'test cases']):
           for doc in sources:
               content = doc.page_content
               test_count = count_test_cases(content)
               if test_count > 0:
                   file_name = doc.metadata.get('file_name', 'Unknown file')
                   response_parts.append(f"\n📝 Found {test_count} test cases in {file_name}")
      
       if sources:
           response_parts.append("\n*Sources:*")
           for i, doc in enumerate(sources[:3], 1):
               source = doc.metadata.get('source', 'Unknown source')
               response_parts.append(f"{i}. {source}")
              
       return "\n".join(response_parts)
   return str(chain_response)


# 🧠 Respond to @bot mentions
@app.event("app_mention")
def handle_mention_events(body, say):
   query = clean_query(body["event"]["text"])
   print(f"📥 User asked: {query}")


   if not query:
       say("I couldn't understand your question. Could you please rephrase it?")
       return


   if "hello" in query.lower() or "hi" in query.lower():
       say("👋 Hello! I'm your automation code assistant. Ask me anything about the Java repo! I can help with:\n"
           "• Code explanations\n"
           "• Finding specific implementations\n"
           "• Understanding patterns and architecture\n"
           "• Best practices and conventions\n"
           "• List test cases for specific classes\n"
           "• Number of test cases in classes")
       return


   try:
       response = rag_chain({"query": query})
       formatted_response = format_response(response, query)
       say(formatted_response)
   except Exception as e:
       print(f"Error processing query: {str(e)}")
       say("I encountered an error processing your question. Could you please rephrase it or try asking something else?")


# 🚀 Start bot
if __name__ == "__main__":
   print("⚡ Slack bot is running...")
   handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
   handler.start()




