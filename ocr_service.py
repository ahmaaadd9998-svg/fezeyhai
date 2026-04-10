import fitz
import easyocr
import os

_reader = None

def get_reader():
    global _reader
    if _reader is None:
        print("Loading EasyOCR models (this may take a moment)...")
        _reader = easyocr.Reader(['ar', 'en'], verbose=False)
    return _reader

def extract_text_from_file(filepath, cached_txt_path=None):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(filepath, cached_txt_path)
    elif ext in ['.png', '.jpg', '.jpeg']:
        return extract_text_from_image(filepath)
    return None

def extract_text_from_pdf(filepath, cached_txt_path=None):
    print(f"Starting OCR extraction for PDF: {filepath}")
    doc = fitz.open(filepath)
    reader = get_reader()
    full_text = []
    
    total_pages = len(doc)
    start_page = 0
    
    # Check if partial progress exists
    progress_file = cached_txt_path + ".progress" if cached_txt_path else None
    if progress_file and os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line.startswith("PROCESSED_PAGE:"):
                        start_page = int(last_line.split(":")[1]) + 1
                        print(f"Resuming from page {start_page + 1}...")
        except Exception as e:
            print(f"Could not load progress: {e}")
            
    # Load previously extracted text if resuming
    if start_page > 0 and cached_txt_path and os.path.exists(cached_txt_path):
        with open(cached_txt_path, "r", encoding="utf-8") as f:
            full_text = [f.read().replace("\n\n---\n\n", "")] # Simplified reload, but actually letting it append to file is better.

    # Better approach: open append mode if resuming
    mode = "a" if start_page > 0 else "w"
    
    for i in range(start_page, total_pages):
        print(f"Processing page {i+1} of {total_pages}...")
        page = doc.load_page(i)
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        result = reader.readtext(img_bytes, detail=0)
        
        page_text = "\n".join(result)
        
        if cached_txt_path:
            with open(cached_txt_path, mode, encoding="utf-8") as f:
                f.write(page_text + "\n\n---\n\n")
            mode = "a" # Switch to append for subsequent pages
            if progress_file:
                with open(progress_file, "a", encoding="utf-8") as f:
                    f.write(f"PROCESSED_PAGE:{i}\n")
        else:
            full_text.append(page_text)
            
    if cached_txt_path and progress_file and os.path.exists(progress_file):
        os.remove(progress_file) # Clean up progress File when done
        
    if not cached_txt_path:
        return "\n\n---\n\n".join(full_text)
    
    # If cached_txt_path was provided, we wrote it directly to disk so we can return empty or reread
    with open(cached_txt_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text_from_image(filepath):
    print(f"Starting OCR extraction for Image: {filepath}")
    reader = get_reader()
    result = reader.readtext(filepath, detail=0)
    return "\n".join(result)
