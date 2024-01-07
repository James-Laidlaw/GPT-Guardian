import base64
import requests


from openai import OpenAI
try:
    import secret_values
except ImportError:
    pass
import os
gpt_key = os.environ.get("GPT_KEY", default=None)
if not gpt_key:
    gpt_key = secret_values.GPT_KEY


def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    print(image_file.read())
    return base64.b64encode(image_file.read()).decode('utf-8')
  
image_path = "test.png"

base64_image = encode_image(image_path)
print(base64_image)
headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {gpt_key}"
}

payload = {
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What’s in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 300
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())