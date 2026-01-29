import os
import requests
from dotenv import load_dotenv

# Load private key from env
load_dotenv()

nvapi_key = os.getenv("NVIDIA_API_KEY")
if not nvapi_key:
    print("Failed to obtain")
    exit(1)

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
stream = False

headers = {
    "Authorization": f"Bearer {nvapi_key}",
    "Accept": "text/event-stream" if stream else "application/json"
}

payload = {
    "model": "meta/llama-4-maverick-17b-128e-instruct",
    "messages": [{"role": "user", "content": "Hello"}],  # 添加了测试内容
    "max_tokens": 512,
    "temperature": 1.00,
    "top_p": 1.00,
    "frequency_penalty": 0.00,
    "presence_penalty": 0.00,
    "stream": stream
}

try:
    response = requests.post(invoke_url, headers=headers, json=payload)

    if stream:
        for line in response.iter_lines():
            if line:
                print(line.decode("utf-8"))
    else:
        print("API call successful！")
        result = response.json()
        print(f"Model response: {result['choices'][0]['message']['content']}")

except Exception as e:
    print(f"ERROR: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response.text}")