from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from datetime import datetime
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.twiml.voice_response import VoiceResponse, Gather

app = FastAPI()

# Configure OpenAI
openai.api_key = "YOUR_OPENAI_API_KEY"

# Google Sheets setup
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Injury Claims").sheet1

# Helper function to check eligibility
def is_eligible(accident_date_str):
    try:
        accident_date = datetime.strptime(accident_date_str, "%Y-%m-%d")
        cutoff = datetime(2025, 8, 1)
        return accident_date < cutoff
    except:
        return False

# Helper to save to Google Sheets
def save_to_google_sheet(data):
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("name"),
        data.get("phone"),
        data.get("email"),
        data.get("accident_date"),
        data.get("location"),
        data.get("injury"),
        data.get("treatment"),
        data.get("pain"),
        data.get("scotland"),
        data.get("witness"),
        data.get("previous_claim"),
        data.get("eligible")
    ]
    sheet.append_row(row)

# In-memory storage (should use DB in real world)
session_data = {}

@app.post("/call")
async def call_handler(request: Request):
    form = await request.form()
    from_number = form.get("From")

    # Start new session if needed
    if from_number not in session_data:
        session_data[from_number] = {
            "step": 0,
            "data": {"phone": from_number}
        }

    user_session = session_data[from_number]
    step = user_session["step"]
    data = user_session["data"]
    speech_result = form.get("SpeechResult", "").strip()

    response = VoiceResponse()
    gather = Gather(input="speech", timeout=6)

    # STEP-BY-STEP SCRIPT LOGIC
    if step == 0:
        gather.say("Hello, this is Sofia from Legal Assist. Were you involved in an accident?")
        user_session["step"] += 1

    elif step == 1:
        if "yes" in speech_result.lower():
            gather.say("When did the accident happen? Please say the date like 15th June 2025.")
        else:
            response.say("Okay, thank you. If anything changes, feel free to call us back.")
            return PlainTextResponse(str(response))
        user_session["step"] += 1

    elif step == 2:
        try:
            accident_date = datetime.strptime(speech_result, "%d %B %Y").strftime("%Y-%m-%d")
            data["accident_date"] = accident_date
            data["eligible"] = "Yes" if is_eligible(accident_date) else "No"
            gather.say("Where did the accident happen? For example, road, work, or public place?")
            user_session["step"] += 1
        except:
            gather.say("Sorry, I didn’t get the date. Please say it again like 10th May 2025.")

    elif step == 3:
        data["location"] = speech_result
        gather.say("Was it your fault or someone else’s fault?")
        user_session["step"] += 1

    elif step == 4:
        data["fault"] = speech_result
        gather.say("Did anyone witness the accident?")
        user_session["step"] += 1

    elif step == 5:
        data["witness"] = speech_result
        gather.say("Did you report the accident to the authorities?")
        user_session["step"] += 1

    elif step == 6:
        data["reported"] = speech_result
        gather.say("Did you receive any medical treatment? If yes, where?")
        user_session["step"] += 1

    elif step == 7:
        data["treatment"] = speech_result
        gather.say("What kind of injury did you suffer?")
        user_session["step"] += 1

    elif step == 8:
        data["injury"] = speech_result
        gather.say("Are you still experiencing pain or symptoms?")
        user_session["step"] += 1

    elif step == 9:
        data["pain"] = speech_result
        gather.say("Have you made a claim before for this accident?")
        user_session["step"] += 1

    elif step == 10:
        data["previous_claim"] = speech_result
        gather.say("Are you located in Scotland?")
        user_session["step"] += 1

    elif step == 11:
        data["scotland"] = speech_result
        gather.say("Can I take your full name?")
        user_session["step"] += 1

    elif step == 12:
        data["name"] = speech_result
        gather.say("Can I also take your email address? You can say skip if you prefer not to.")
        user_session["step"] += 1

    elif step == 13:
        if "skip" not in speech_result.lower():
            data["email"] = speech_result
        else:
            data["email"] = ""

        # Save to Google Sheets
        save_to_google_sheet(data)

        response.say("Thank you. Based on what you’ve told me, your claim appears to be potentially valid. Our solicitor team will contact you shortly. Goodbye.")
        session_data.pop(from_number, None)
        return PlainTextResponse(str(response))

    response.append(gather)
    return PlainTextResponse(str(response))
