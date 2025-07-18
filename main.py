from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

@app.post("/call")
async def handle_call(request: Request):
    twiml = """
    <Response>
        <Say>Hello, this is Legal Assist calling about your personal injury claim. One of our solicitors will contact you shortly. Thank you.</Say>
    </Response>
    """
    return Response(content=twiml, media_type="application/xml")
