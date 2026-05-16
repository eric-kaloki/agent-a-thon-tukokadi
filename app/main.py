import os
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.agents import agent_runner
from app.state import state_manager
from google.genai import types

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
    
    try:
        full_response = ""
        
        # 1. Check if the session exists in the ADK runner; if not, create it
        try:
            await agent_runner.session_service.create_session(
                app_name="tukokadi_civic_app",
                session_id=user_id, 
                user_id=user_id
            )
        except Exception as e:
            print(f"Session creation error: {repr(e)}")
            
        # 2. FIX: Explicitly package the raw text into an ADK content schema
        formatted_message = types.Content(
            role='user',
            parts=[types.Part(text=request.message)]
        )
        
        # 2. Execute the formatted model packet via the Runner
        async for chunk in agent_runner.run_async(user_id=user_id, session_id=user_id, new_message=formatted_message):
            # Safe text extraction loop based on your ADK iteration scheme
            if hasattr(chunk, 'content') and chunk.content.parts:
                for part in chunk.content.parts:
                    if part.text:
                        full_response += part.text
            elif hasattr(chunk, 'text'):
                full_response += str(chunk.text)
            else:
                full_response += str(chunk)
                
        response = full_response
        
        # Simple heuristic to update XP if the response looks like a success from Mwalimu
        if "XP" in str(response):
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
    form_data = await request.form()
    incoming_msg = form_data.get("Body") or form_data.get("text")
    sender = form_data.get("From") or form_data.get("sender")
    
    if not incoming_msg or not sender:
        return JSONResponse({"status": "ignored"})

    user_state = state_manager.get_user(sender)
    full_response = ""
    
    # Check/Create the user session mapping for incoming WhatsApp interactions
    try:
        await agent_runner.session_service.create_session(
            app_name="tukokadi_civic_app",
            session_id=sender, 
            user_id=sender
        )
    except Exception as e:
        print(f"Session creation error: {repr(e)}")
        
    # FIX: Enforce the explicit Content format structure
    formatted_whatsapp_msg = types.Content(
        role='user',
        parts=[types.Part(text=incoming_msg)]
    )
    
    async for chunk in agent_runner.run_async(user_id=sender, session_id=sender, new_message=formatted_whatsapp_msg):
        if hasattr(chunk, 'content') and chunk.content.parts:
            for part in chunk.content.parts:
                if part.text:
                    full_response += part.text
        elif hasattr(chunk, 'text'):
            full_response += str(chunk.text)
        else:
            full_response += str(chunk)
            
    response = full_response
    
    if "XP" in str(response):
        state_manager.update_user(sender, {"xp": user_state["xp"] + 10})
    
    return {
        "status": "success",
        "response": str(response),
        "to": sender
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
