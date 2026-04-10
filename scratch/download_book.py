import requests
import os

file_id = '1CZQolc6os4adRID834mRX_7TfkAUjqud'
url = f'https://drive.google.com/uc?export=download&id={file_id}'
output = 'company_docs/physics_book.pdf'

os.makedirs('company_docs', exist_ok=True)

print(f"Downloading from {url}...")
response = requests.get(url, stream=True)
if response.status_code == 200:
    with open(output, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded: {output}")
else:
    print(f"Failed to download. Status code: {response.status_code}")
