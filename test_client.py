import requests
import json

try:
    response = requests.post("http://127.0.0.1:5000/chat", json={"question": "السلام عليكم"})
    print("Status:", response.status_code)
    print("Response JSON:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))
except Exception as e:
    print("Fetch error:", e)
