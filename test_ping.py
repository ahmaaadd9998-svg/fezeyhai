import requests
try:
    print("Sending ping...")
    response = requests.post("http://127.0.0.1:5000/chat", json={"question": "اختبار"}, timeout=60)
    print("Status:", response.status_code)
    print("Content:", response.text)
except requests.exceptions.Timeout:
    print("Request timed out!")
except Exception as e:
    print("Error:", e)
