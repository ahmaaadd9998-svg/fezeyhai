import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)

def cleanup_and_sync():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("--- STEP 1: DELETING ALL REMOTE FILES ---")
    remote_files = list(client.files.list())
    for f in remote_files:
        print(f"Deleting remote file: {f.name} ({f.display_name})")
        try:
            client.files.delete(name=f.name)
        except Exception as e:
            print(f"Error deleting {f.name}: {e}")

    print("\n--- STEP 2: UPLOADING LOCAL FILES ---")
    state_file = "gemini_state.json"
    file_map = {}
    
    docs_dir = "company_docs"
    if not os.path.exists(docs_dir):
        print(f"Error: {docs_dir} not found.")
        return

    for filename in os.listdir(docs_dir):
        if filename.endswith(".pdf"):
            local_path = os.path.join(docs_dir, filename).replace("\\", "/")
            print(f"Uploading {local_path}...")
            try:
                uploaded_file = client.files.upload(
                    file=local_path,
                    config={'display_name': filename}
                )
                
                import time
                while uploaded_file.state.name == "PROCESSING":
                    print("Processing...")
                    time.sleep(2)
                    uploaded_file = client.files.get(name=uploaded_file.name)
                
                if uploaded_file.state.name == "ACTIVE":
                    file_map[local_path] = uploaded_file.name
                    print(f"Success: {uploaded_file.name}")
                else:
                    print(f"Failed: {uploaded_file.state.name}")
            except Exception as e:
                print(f"Error uploading {filename}: {e}")

    print("\n--- STEP 3: UPDATING STATE FILE ---")
    state = {"file_map": file_map}
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
    print(f"Updated {state_file}")

if __name__ == "__main__":
    cleanup_and_sync()
