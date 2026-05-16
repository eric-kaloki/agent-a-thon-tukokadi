import os
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.agents import root_agent
from app.state import state_manager

app = FastAPI(title="TukoKadi AI")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

class ChatRequest(BaseModel):
    message: str
    user_id: str = None  # Mock phone number or session ID

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: ChatRequest):
    user_id = request.user_id or str(uuid.uuid4())
    user_state = state_manager.get_user(user_id)
    
    # In a real scenario, we might pass the state to the agent via context
    # For now, we call the agent and get the response
    try:
        # Note: google-adk run() usually returns an object or string
        # We assume root_agent.run() is the entry point
        response = root_agent.run(request.message)
        
        # Simple heuristic to update XP if the response looks like a success from Mwalimu
        # In a production app, the agent would use a Tool to update state
        if "XP" in str(response):
             # Parse XP if possible, or just increment
             state_manager.update_user(user_id, {"xp": user_state["xp"] + 10})
        
        updated_state = state_manager.get_user(user_id)
        
        return {
            "response": str(response),
            "state": updated_state,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    # Plug-and-play structure for WhatsApp (Twilio/Meta)
    # 1. Parse incoming message
    form_data = await request.form()
    incoming_msg = form_data.get("Body") or form_data.get("text")
    sender = form_data.get("From") or form_data.get("sender")
    
    if not incoming_msg or not sender:
        return JSONResponse({"status": "ignored"})

    # 2. Call the agent
    user_state = state_manager.get_user(sender)
    response = root_agent.run(incoming_msg)
    
    # 3. Handle state updates
    if "XP" in str(response):
        state_manager.update_user(sender, {"xp": user_state["xp"] + 10})

    # 4. Return response (Twilio format example)
    # In production, you would call the WhatsApp API here
    # For Twilio, you return TwiML:
    # return Response(content=f"<Response><Message>{response}</Message></Response>", media_type="application/xml")
    
    return {
        "status": "success",
        "response": str(response),
        "to": sender
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
