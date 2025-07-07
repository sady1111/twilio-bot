from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")

client = Client(account_sid, auth_token)

call = client.calls.create(
    to="+441612437480",  # Replace with the recipient number
    from_=twilio_number,
    url="https://twilio-voice-bot-6vst.onrender.com/voice"  # Replace with your bot's public URL
)

print(f"📞 Call placed! SID: {call.sid}")
