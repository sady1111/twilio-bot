from fastapi import FastAPI
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse

app = FastAPI()

@app.post("/voice")
async def voice():
    twiml = VoiceResponse()
    twiml.say("Hi, this is Sofia from Legal Assist. Can I ask you about a recent accident?", voice="Polly.Salli")
    twiml.gather(input='speech', action='/voice', method='POST', timeout=5)
    return Response(content=str(twiml), media_type="application/xml")
