from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

def test_file_uri():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("Listing all uploaded files on Gemini...")
    for f in client.files.list():
        print(f"- {f.name} ({f.display_name}): {f.state.name}")

    with open("gemini_state.json", "r") as f:
        state = json.load(f)
        file_map = state.get("file_map", {})
    
    selected_model = "gemini-2.5-flash"
    print(f"\nUsing model: {selected_model}")

    for local_path, file_name in file_map.items():
        print(f"Testing file: {file_name} for {local_path}")
        print(f"Verifying file name: {file_name}")
        try:
            # Method 1: FileData with full URI (as currently in code)
            print("Trying Method 1 (Full URI)...")
            content_v1 = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            file_data=types.FileData(
                                file_uri=f"https://generativelanguage.googleapis.com/v1beta/{file_name}",
                                mime_type="application/pdf"
                            )
                        ),
                        types.Part.from_text(text="ما هو عنوان هذا الكتاب؟")
                    ]
                )
            ]
            response = client.models.generate_content(
                model=selected_model,
                contents=content_v1
            )
            print("Method 1 Success!")
            print(response.text[:100])
            
        except Exception as e:
            print(f"Method 1 Failed: {e}")
            
        try:
            # Method 2: FileData with just the name or gs:// style if name starts with files/
            print("\nTrying Method 2 (Short URI or name)...")
            # The SDK might expect just the file name/path
            content_v2 = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            file_data=types.FileData(
                                file_uri=file_name, # Try passing 'files/...' directly
                                mime_type="application/pdf"
                            )
                        ),
                        types.Part.from_text(text="ما هو عنوان هذا الكتاب؟")
                    ]
                )
            ]
            response = client.models.generate_content(
                model=selected_model,
                contents=content_v2
            )
            print("Method 2 Success!")
            print(response.text[:100])
        except Exception as e:
            print(f"Method 2 Failed: {e}")

if __name__ == "__main__":
    test_file_uri()
