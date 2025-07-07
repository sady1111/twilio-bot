from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System prompt for AI behavior
SYSTEM_PROMPT = """
You are Sofia, a warm and professional claims assistant from Legal Assist. 
You're calling to help with UK and Scottish personal injury claims.
Always speak naturally, never repeat yourself, and don’t sound robotic.

Follow this logical flow:
1. Confirm if they had an accident in the last 6 months.
2. Ask when and where the accident happened.
3. Ask what kind of accident it was (car, workplace, slip, etc.).
4. Ask if someone else was at fault.
5. Ask if they received medical treatment.
6. Ask if it was reported (police, workplace, etc.).
7. Ask if they’re still experiencing any pain or discomfort.
8. Mention no win–no fee and that they may be eligible for compensation.
9. Offer to connect them to a solicitor now.

If user says no, thank them and end politely.
Be clear, concise, and responsive. NEVER say dates are in the future unless it's truly past today.
"""

@app.post("/voice")
async def voice_webhook(request: Request):
    response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Amy" language="en-GB">
        Hello there, this is Sofia calling from Legal Assist. 
        I just wanted to ask if you've had any kind of accident in the past six months that wasn’t your fault. 
        You may be entitled to compensation. May I ask you a couple of quick questions?
    </Say>
    <Gather input="speech" action="/process" method="POST" timeout="5">
        <Say voice="Polly.Amy" language="en-GB">Please say yes or no to get started.</Say>
    </Gather>
    <Say voice="Polly.Amy" language="en-GB">Sorry, I didn’t catch that. Let’s try again.</Say>
</Response>"""
    return PlainTextResponse(response, media_type="text/xml")

@app.post("/process")
async def process_speech(request: Request):
    form = await request.form()
    speech_result = form.get("SpeechResult", "")
    print(f"User said: {speech_result}")

    # Add date handling to fix 'future' error
    today = datetime.today().date()
    if "march 2025" in speech_result.lower():
        speech_result = speech_result.lower().replace("march 2025", "March 1st, 2025")
    # Handle general date errors
    for word in speech_result.split():
        try:
            date_obj = datetime.strptime(word, "%Y-%m-%d").date()
            if date_obj > today:
                speech_result += " — but please note, the user might have misspoken, it's likely a past date."
        except:
            pass

    # Call OpenAI GPT
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": speech_result}
        ]
    )

    ai_reply = completion.choices[0].message.content
    print(f"AI response: {ai_reply}")

    # Continue conversation
    response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/process" method="POST" timeout="6">
        <Say voice="Polly.Amy" language="en-GB">{ai_reply}</Say>
    </Gather>
    <Say voice="Polly.Amy" language="en-GB">Sorry, I didn’t hear anything that time. Let’s move forward.</Say>
</Response>"""
    return PlainTextResponse(response, media_type="text/xml")