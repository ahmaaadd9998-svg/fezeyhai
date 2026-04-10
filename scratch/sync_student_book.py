import os
import sys
from openai_service import _service

file_path = "company_docs/physics_farst.pdf"
if os.path.exists(file_path):
    print(f"Starting manual sync for: {file_path}")
    try:
        _service.upload_file(file_path)
        print("Sync successful!")
    except Exception as e:
        print(f"Sync failed: {e}")
else:
    print(f"File not found: {file_path}")
