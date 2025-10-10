import requests
import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("prompt", help="The prompt to send to the Openrouter API")
parser.add_argument("file_name", help="Name of the file to save Python script")
args = parser.parse_args()

api_endpoint = "https://openrouter.ai/api/v1/chat/completions"
api_key = os.getenv("Openrouter_API_KEY")


request_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://example.com",  # required by OpenRouter
    "X-Title": "TestApp"  # can be any string
}

request_data = {
    "model": "openai/gpt-4",
    "messages": [
         {"role": "system", "content": "You are an expert Python developer. Only respond with valid code — no extra text."},
         {"role": "user", "content":f"Generate a Python script that will {args.prompt}. Output only the code, no extra text or explanation."}
],
    "max_tokens": 350,
    "temperature": 0.2
}

response = requests.post(api_endpoint, headers=request_headers, json=request_data)

if response.status_code == 200:
     response_text = (response.json()["choices"][0]["message"]["content"])
     with open(args.file_name, "w") as file:
          file.write(response_text)
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)