import os
from git import Repo


def clone_repo(repo_url, clone_path='data/repo'):
   if os.path.exists(clone_path):
       print("[✔] Repo already cloned.")
       return
   Repo.clone_from(repo_url, clone_path)
   print("[+] Repo cloned successfully.")


def load_files(base_path='data/repo'):
   all_texts = []
   for root, _, files in os.walk(base_path):
       for file in files:
           if file.endswith(('.py', '.md', '.txt', '.json', '.yaml', '.java')):
               try:
                   with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                       all_texts.append(f.read())
               except:
                   continue
   return all_texts




