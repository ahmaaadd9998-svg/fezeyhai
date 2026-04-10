import os
import json
import time
from openai_service import _service

def total_reset():
    print("--- Starting Total Reset ---")
    
    # 1. Clear Gemini files
    print("Deleting all files on Gemini...")
    try:
        files = _service.client.files.list()
        for f in files:
            print(f"Deleting: {f.display_name} ({f.name})")
            _service.client.files.delete(name=f.name)
    except Exception as e:
        print(f"Error listing/deleting files: {e}")

    # 2. Clear local state
    print("Clearing local state file...")
    if os.path.exists("gemini_state.json"):
        os.remove("gemini_state.json")
    
    # 3. Re-upload everything from company_docs
    docs_dir = "company_docs"
    if os.path.exists(docs_dir):
        for filename in os.listdir(docs_dir):
            if filename.endswith(".pdf"):
                filepath = os.path.join(docs_dir, filename)
                print(f"Re-uploading: {filepath}")
                try:
                    _service.upload_file(filepath)
                    print(f"Successfully uploaded: {filename}")
                except Exception as e:
                    print(f"Failed to upload {filename}: {e}")
    
    print("--- Reset and Sync Complete ---")

if __name__ == "__main__":
    total_reset()
