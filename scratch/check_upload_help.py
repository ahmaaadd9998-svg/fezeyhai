from google import genai
import os

client = genai.Client(api_key="dummy")
print(help(client.files.upload))
