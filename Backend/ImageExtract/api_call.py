from google import genai
from google.genai import types
import os

from prompt import (
    AGENT_MESSAGE,
)

with open('/home/hoanganh04/Projects/data4life/ImageExtract/data/lam-giay-ket-hon-gia1.jpg', 'rb') as f:
    image_bytes = f.read()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
model='gemini-2.5-flash',
contents=[
    types.Part.from_bytes(
    data=image_bytes,
    mime_type='image/jpeg',
    ),
    AGENT_MESSAGE
]
)

print(response.text)