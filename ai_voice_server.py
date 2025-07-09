from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
app = FastAPI()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define system prompt for AI
SYSTEM_PROMPT = """
You are Sofia, a smart, warm, and professional virtual assistant from Legal Assist. It is currently July 2025.

You are speaking to someone who may have been in an accident and is curious or confused about the claims process.

Your job is to:
- Answer ANY question they ask related to personal injury claims in the UK or Scotland.
- Speak in a human, friendly, and reassuring way.
- Explain things clearly, like no win–no fee, ATE policies, claim timelines, etc.
- Handle confusion, anger, or doubt with calm professionalism.
- Do not ask questions or interview them — just help, clarify, and support.
- When the conversation feels done or winding down, say:

  “Thank you for your time. You’ll receive a call shortly from our solicitor’s firm to take this further.”

Never say anything legally binding. You are not a solicitor — you're a helpful assistant.
"""


# Twilio voice webhook
@app.post("/voice")
async def voice_webhook(request: Request):
    response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Emma" language="en-GB">
        Hello, this is Sofia from Legal Assist. I’m just calling about a possible accident or injury claim.
        May I ask you a couple of quick questions to check if you're eligible for compensation?
    </Say>
    <Gather input="speech" action="/process" method="POST" timeout="6">
        <Say voice="Polly.Emma" language="en-GB">Please say yes or no to begin.</Say>
    </Gather>
    <Say voice="Polly.Emma" language="en-GB">Sorry, I didn’t catch that. Goodbye.</Say>
</Response>"""
    return PlainTextResponse(response, media_type="text/xml")

# Twilio speech response processor
@app.post("/process")
async def process_speech(request: Request):
    form = await request.form()
    user_input = form.get("SpeechResult", "")
    print(f"User said: {user_input}")

    # Handle future date confusion (since it's July 2025)
    today = datetime(2025, 7, 7)
    for word in user_input.split():
        try:
            date_obj = datetime.strptime(word, "%Y-%m-%d").date()
            if date_obj > today.date():
                user_input += " — Note: user might have meant a past date. Please confirm."
        except:
            continue

    # Generate AI response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )
    ai_reply = response.choices[0].message.content
    print(f"AI response: {ai_reply}")

    # Return TwiML
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/process" method="POST" timeout="6">
        <Say voice="Polly.Emma" language="en-GB">{ai_reply}</Say>
    </Gather>
    <Say voice="Polly.Emma" language="en-GB">Sorry, didn’t hear anything. Let’s end it here for now.</Say>
</Response>"""
    return PlainTextResponse(xml, media_type="text/xml")
