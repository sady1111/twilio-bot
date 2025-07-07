from fastapi import FastAPI, Request, Form
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
async def voice_webhook():
    response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Amy" language="en-GB">
        Hello there, this is Sofia calling from Legal Assist. 
        I just wanted to ask if you've had any kind of accident in the past six months that wasn’t your fault. 
        You may be entitled to compensation. May I ask you a couple of quick questions?
    </Say>
    <Gather input="speech" action="/process" method="POST" timeout="6">
        <Say voice="Polly.Amy" language="en-GB">Please say yes or no to begin.</Say>
    </Gather>
    <Say voice="Polly.Amy" language="en-GB">Sorry, I didn’t catch that. Goodbye for now.</Say>
</Response>"""
    return PlainTextResponse(response, media_type="text/xml")

@app.post("/process")
async def process_speech(request: Request):
    form = await request.form()
    speech_result = form.get("SpeechResult", "").strip()

    print(f"User said: {speech_result}")

    if not speech_result:
        return PlainTextResponse("""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Amy" language="en-GB">Sorry, I didn’t catch anything. Goodbye for now.</Say>
</Response>""", media_type="text/xml")

    today = datetime.today().date()

    # Guardrails for future dates
    for word in speech_result.split():
        try:
            date_obj = datetime.strptime(word, "%Y-%m-%d").date()
            if date_obj > today:
                speech_result += " (note: the user may have meant a past date)"
        except:
            continue

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": speech_result}
            ]
        )
        ai_reply = completion.choices[0].message.content.strip()
        print(f"AI response: {ai_reply}")
    
        response = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response>
    <Gather input=\"speech\" action=\"/process\" method=\"POST\" timeout=\"6\">
        <Say voice=\"Polly.Amy\" language=\"en-GB\">{ai_reply}</Say>
    </Gather>
    <Say voice=\"Polly.Amy\" language=\"en-GB\">Thanks for your time today. Goodbye.</Say>
</Response>"""
        return PlainTextResponse(response, media_type="text/xml")

    except Exception as e:
        print("Error generating AI response:", e)
        return PlainTextResponse("""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Amy" language="en-GB">Sorry, something went wrong on my side. Goodbye.</Say>
</Response>""", media_type="text/xml")