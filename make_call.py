from twilio.rest import Client

# ✅ Twilio credentials
account_sid = "AC312ed40bc95fecde9f15a8083cc2e257"
auth_token = "9335908ae7c48aaaf35c8621db15362b"

# ✅ Create Twilio client
client = Client(account_sid, auth_token)

# ✅ Call function
def make_call(phone_number):
    try:
        call = client.calls.create(
            url="https://fastapi-vercel-104lawoxr-saddams-projects-44ca5472.vercel.app/api/call",  # ✅ FIXED API endpoint
            to=phone_number,
            from_="+447123456789"  # ✅ Replace with your Twilio verified UK number
        )
        print(f"✅ Call initiated to {phone_number}. Call SID: {call.sid}")
    except Exception as e:
        print(f"❌ Error calling {phone_number}: {e}")

# ✅ Example call
make_call("+447412403311")
