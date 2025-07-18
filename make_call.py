from twilio.rest import Client

# 🔐 Twilio credentials
account_sid = "AC312ed40bc95fecde9f15a8083cc2e257"
auth_token = "9335908ae7c48aaaf35c8621db15362b"

client = Client(account_sid, auth_token)

def make_call(phone_number):
    call = client.calls.create(
        url="https://fastapi-vercel-104lawoxr-saddams-projects-44ca5472.vercel.app/call",  # ✅ Your FastAPI webhook
        to=phone_number,
        from_="+44xxxxxxxxxx"  # ✅ Your verified Twilio number
    )
    print(f"📞 Call initiated to {phone_number}. Call SID: {call.sid}")

# 🔁 Test call
make_call("+447123456789")  # <-- Replace with real client number
