from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()

@app.post("/voice")
def voice_response():
    twiml = """
    <Response>
        <Say voice="alice">Hi, this is Sofia from the injury claims department. Can I ask you a few questions about your recent accident?</Say>
    </Response>
    """
    return Response(content=twiml, media_type="text/xml")
