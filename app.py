import os
from flask import Flask, render_template, request, jsonify, session
import threading
from watcher import start_watching
from openai_service import ask_question, upload_and_add_to_vector_store, verify_gemini_files
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, session, send_from_directory

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "physics_secret_123")
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'company_docs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('static', 'sw.js')

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('authenticated') and os.getenv("APP_PASSCODE"):
        return jsonify({"error": "Unauthorized"}), 401
        
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        
        # Trigger immediate sync
        try:
            upload_and_add_to_vector_store(save_path)
            return jsonify({"success": True, "filename": filename})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Only PDF files allowed"}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question')
    history = data.get('history', [])
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
        
    try:
        mode = data.get('mode', 'chat')
        answer = ask_question(question, history, mode)
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

def run_watcher():
    observer = start_watching()
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    # Initialize Gemini service and verify files
    print("Initializing Gemini Service...")
    verify_gemini_files()
    
    # Start the background watcher thread ONLY if not in cloud mode
    if os.getenv("CLOUD_MODE") != "true":
        print("Starting local file watcher...")
        watcher_thread = threading.Thread(target=run_watcher, daemon=True)
        watcher_thread.start()
    else:
        print("Cloud mode detected: Skipping file watcher.")
    
    # Run Flask
    app.run(debug=True, port=5000)
