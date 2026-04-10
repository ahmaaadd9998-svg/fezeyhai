import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Ensure we have the latest environment variables
load_dotenv(override=True)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.state_file = "gemini_state.json"
        self.cloud_mode = os.getenv("CLOUD_MODE", "false").lower() == "true"

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_state(self, state):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)

    def get_file_map(self):
        state = self.load_state()
        return state.get("file_map", {})

    def update_file_map(self, local_path, file_name):
        local_path = os.path.normpath(local_path).replace("\\", "/")
        state = self.load_state()
        if "file_map" not in state:
            state["file_map"] = {}
        state["file_map"][local_path] = file_name
        self.save_state(state)

    def remove_from_file_map(self, local_path):
        local_path = os.path.normpath(local_path).replace("\\", "/")
        state = self.load_state()
        if "file_map" in state and local_path in state["file_map"]:
            del state["file_map"][local_path]
            self.save_state(state)

    def verify_files(self):
        """Cleanup expired files from the state."""
        print("Verifying Gemini files...")
        file_map = self.get_file_map()
        to_remove = []
        for local_path, file_name in file_map.items():
            try:
                self.client.files.get(name=file_name)
            except Exception:
                print(f"Warning: File {file_name} expired or missing. Unmapping {local_path}.")
                to_remove.append(local_path)
        
        for local_path in to_remove:
            self.remove_from_file_map(local_path)

    def upload_file(self, file_path):
        """Uploads a file to Gemini and tracks it."""
        try:
            file_path = os.path.normpath(file_path).replace("\\", "/")
            file_map = self.get_file_map()
            
            # Clean up old version if it exists
            if file_path in file_map:
                old_name = file_map[file_path]
                try:
                    self.client.files.delete(name=old_name)
                except:
                    pass

            upload_path = file_path
            # In Local Mode, we use OCR text (legacy logic)
            if not self.cloud_mode:
                cache_dir = "ocr_cache"
                os.makedirs(cache_dir, exist_ok=True)
                base_name = os.path.basename(file_path)
                cached_txt_path = os.path.join(cache_dir, base_name + ".txt")
                
                if os.path.exists(cached_txt_path) and os.path.getmtime(cached_txt_path) >= os.path.getmtime(file_path):
                    upload_path = cached_txt_path
                else:
                    from ocr_service import extract_text_from_file
                    extract_text_from_file(file_path, cached_txt_path)
                    upload_path = cached_txt_path

            print(f"Uploading {upload_path} to Gemini...")
            display_name = os.path.basename(file_path)
            uploaded_file = self.client.files.upload(file=upload_path, config={'display_name': display_name})
            
            # Wait for processing
            while uploaded_file.state.name == "PROCESSING":
                print("Processing file...")
                time.sleep(3)
                uploaded_file = self.client.files.get(name=uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception(f"File processing failed: {uploaded_file.name}")

            print(f"Synced: {file_path}")
            self.update_file_map(file_path, uploaded_file.name)
            return uploaded_file
        except Exception as e:
            print(f"Upload Error: {e}")
            raise

    def ask(self, question, history=None, mode='chat'):
        if history is None: history = []
        
        file_map = self.get_file_map()
        content_parts = []
        
        # Add files to query context
        for file_name in file_map.values():
            # Standard way to pass Gemini-hosted files in google-genai SDK
            content_parts.append(types.Part(
                file_data=types.FileData(
                    file_uri=f"https://generativelanguage.googleapis.com/v1beta/{file_name}", 
                    mime_type="application/pdf"
                )
            ))

        # Build message context
        messages = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            messages.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.get("content", ""))]))
        
        # Current question with files
        current_parts = content_parts + [types.Part.from_text(text=question)]
        messages.append(types.Content(role="user", parts=current_parts))

        # Dynamic System Instruction based on mode
        system_instruction_text = (
            "أنت مساعد فيزياء خبير يعتمد على المنهج المعتمد. "
        )

        if mode == 'chat':
            system_instruction_text += (
                "الوضع الحالي هو 'مناقشة ودردشة'. "
                "أجب على أسئلة المستخدم بأسلوب علمي مباشر وشيق. "
                "ممنوع تماماً ذكر أي شيء يتعلق بإعداد الدروس أو الخطط أو التمهيد أو الأهداف السلوكية إلا إذا طلب المستخدم ذلك صراحة. "
                "كن مفيداً ومختصراً في الشرح العلمي."
            )
        elif mode == 'lesson_plan':
            system_instruction_text += (
                "الوضع الحالي هو 'إعداد خطة درس تفاعلية'. "
                "التزم بالهيكل التالي بدقة: أهداف سلوكية، تمهيد (5 دق)، سير الدرس (أنشطة: استكشاف، بناء مفهوم، تطبيق)، وتقييم ختامي. "
                "استخدم لغة تربوية رصينة وتوزيع زمن دقيق."
            )
        elif mode == 'questions':
            system_instruction_text += (
                "الوضع الحالي هو 'توليد أسئلة'. "
                "لا تذكر أي تفاصيل عن خطة الدرس أو التمهيد. "
                "نفذ الطلب (صح وخطأ، اختيار، مقالي، إلخ) بالعدد والنوع المطلوب بدقة. "
                "وضح مستويات بلوم (Bloom's Taxonomy) لكل سؤال. ابدأ مباشرة بذكر الأسئلة."
            )
        elif mode == 'remedial':
            system_instruction_text += (
                "الوضع الحالي هو 'خطة علاجية أو إثرائية'. "
                "ركز على استراتيجيات معالجة الضعف أو تعزيز الموهبة للموضوع المذكور بناءً على المنهج."
            )

        system_instruction_text += (
            "\n\nتعليمات عامة لجميع المهام:\n"
            "- اعتمد فقط على المعلومات العلمية من الكتب المرفقة.\n"
            "- استخدم لغة عربية سليمة وواضحة.\n"
            "- لا تخرج عن سياق الفيزياء والمنهج التعليمي."
        )

        models_to_try = ["gemini-2.5-flash", "gemini-flash-latest"]
        last_err = ""
        
        for model_name in models_to_try:
            try:
                print(f"DEBUG: Calling {model_name} in mode: {mode}...")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=messages,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction_text
                    )
                )
                return response.text
            except Exception as e:
                last_err = str(e)
                print(f"DEBUG: {model_name} failed: {last_err}")
                continue
        
        return f"عذراً، فشل الاتصال بالموديلات المتاحة. آخر خطأ: {last_err}"
        
        return f"عذراً، جميع المحاولات فشلت.\n\nآخر خطأ سجلناه هو:\n{last_error}"

# Initialize Singleton Service
_service = GeminiService()

# Export functions for app.py
def upload_and_add_to_vector_store(file_path):
    return _service.upload_file(file_path)

def remove_file_from_vector_store(file_path):
    return _service.remove_from_file_map(file_path)

def ask_question(question, history=None, mode='chat'):
    return _service.ask(question, history, mode)

def get_file_map():
    return _service.get_file_map()

def verify_gemini_files():
    return _service.verify_files()
