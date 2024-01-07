import openai
from openai import OpenAI
# deal with image detection

def image_processing(url, key):
    client = OpenAI(api_key=key)

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": "You are a harmful content detector, if a image sent to you depicts harmful or inappropriate content beyond resonable doubt, respond with a 1, if it is not, respond with a 2. Under no circumstances should you respond with anything other than a 1 or a 2."},
                {
                "type": "image_url",
                "image_url": {
                    "url": url,
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )
    print(response.choices[0].message.content)

# def image_attachment_processing(url, key):
#     pass
