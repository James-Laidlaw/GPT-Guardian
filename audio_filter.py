import assemblyai as aai
from detect_hate import *

try:
    import secret_values
except ImportError:
    pass
import os


audio_key = os.environ.get("AUDIO_KEY", default=None)
if not audio_key:
    audio_key = secret_values.AUDIO_KEY

aai.settings.api_key = audio_key

gpt_key = os.environ.get("GPT_KEY", default=None)
if not gpt_key:
    gpt_key = secret_values.GPT_KEY


def get_text(url):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(url)
    text = transcript.text
    print(text)
    return text


def process_info(text, role):
    result = call_gpt(text, gpt_key, role)
    return result
