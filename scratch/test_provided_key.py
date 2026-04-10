import os
from google import genai
from google.genai import types

def test_key(api_key):
    print(f"Testing key: {api_key[:10]}...")
    client = genai.Client(api_key=api_key)
    try:
        # Try to list models to verify key
        models = client.models.list()
        print("Key is valid! Can list models.")
        
        # Try a simple generation
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Say 'Key is fully functional with Billing' if you can, otherwise say 'Free tier detected'."
        )
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test the key the user just sent
    test_key("AIzaSyDqagpX5GmtP2ThCmyx3f1Molys5oUp6K8") 
    # Also test the one from the previous session logs to be sure of the typo
    print("-" * 20)
    test_key("AIzaSyDqagpX5GMtP2ThCmyx3f1MoIyS5oUp6K8")
