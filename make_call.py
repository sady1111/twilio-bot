from twilio.rest import Client

# 🔐 Enter your real Twilio credentials here
account_sid = "AC312ed40bc95fecde9f15a8083cc2e257"      # Your Twilio Account SID
auth_token = "9335908ae7c48aaaf35c8621db15362b"                 # Your Twilio Auth Token

client = Client(account_sid, auth_token)

def make_call(phone_number):
    call = client.calls.create(
        url="https://your-vercel-app-name.vercel.app/call",  # Replace with your deployed endpoint
        to=phone_number,
        from_="+44xxxxxxxxxx"  # Your Twilio UK phone number (must be a verified number)
    )
    print(f"📞 Call initiated to {phone_number}. Call SID: {call.sid}")

# 🔁 Test call
make_call("+447123456789")  # <-- Change to the client's number
