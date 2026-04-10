import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai_service import upload_and_add_to_vector_store, remove_file_from_vector_store

FOLDER_TO_WATCH = "company_docs"

class DocHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            # wait a bit for file to finish copying
            time.sleep(1)
            upload_and_add_to_vector_store(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modified: {event.src_path}")
            time.sleep(1)
            upload_and_add_to_vector_store(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")
            remove_file_from_vector_store(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            print(f"File moved from {event.src_path} to {event.dest_path}")
            upload_and_add_to_vector_store(event.dest_path)

def start_watching():
    if not os.path.exists(FOLDER_TO_WATCH):
        os.makedirs(FOLDER_TO_WATCH)
        
    # Verify existing files didn't expire on Gemini (48h policy)
    try:
        from openai_service import verify_gemini_files
        verify_gemini_files()
    except Exception as e:
        print(f"Warning: Could not verify Gemini files: {e}")

    # Initial sync for existing files
    print("Performing initial file sync...")
    try:
        from openai_service import get_file_map
        existing_map = get_file_map()
        for filename in os.listdir(FOLDER_TO_WATCH):
            filepath = os.path.join(FOLDER_TO_WATCH, filename)
            if os.path.isfile(filepath):
                # If file not in map, upload it
                if filepath not in existing_map:
                    print(f"Sycning existing file: {filepath}")
                    upload_and_add_to_vector_store(filepath)
    except Exception as e:
        print(f"Error during initial sync: {e}")

    event_handler = DocHandler()
    observer = Observer()
    observer.schedule(event_handler, path=FOLDER_TO_WATCH, recursive=False)
    observer.start()
    print(f"Started watching '{FOLDER_TO_WATCH}' for changes...")
    
    # We return the observer so the main thread can keep it alive
    return observer
