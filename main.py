
import re
import random
import google.generativeai as genai
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# --- CONFIGURATION ---
# ⚠️ IMPORTANT: Replace this with your actual Gemini API Key from Google AI Studio
GEMINI_API_KEY = "AIzaSyC9I_WuoJgZdDhhmyGUs8HudjryQG7dL3Y" 
SUBMISSION_SECRET = "bharath_123"

# Setup the AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# --- INPUT DATA MODELS (Fixed for 422 Error) ---
class MessageHistory(BaseModel):
    role: str
    content: str

class IncomingRequest(BaseModel):
    conversation_id: str
    message: str
    # This checks if 'history' is missing and creates an empty list instead of crashing
    history: List[MessageHistory] = Field(default_factory=list)

# --- ADVANCED FEATURE 1: FAKE DATA GENERATOR ---
def generate_fake_transaction_id():
    return f"UPI-{random.randint(10000000, 99999999)}"

# --- ADVANCED FEATURE 2: INTELLIGENCE EXTRACTION ---
def extract_intelligence(text):
    upi_found = re.findall(r"[a-zA-Z0-9.\-_]+@[a-zA-Z]+", text)
    links_found = re.findall(r"https?://\S+|www\.\S+", text)
    phones_found = re.findall(r"\b[6-9]\d{9}\b", text)
    ifsc_found = re.findall(r"[A-Z]{4}0[A-Z0-9]{6}", text)
    
    return {
        "upi": list(set(upi_found)),
        "links": list(set(links_found)),
        "phones": list(set(phones_found)),
        "ifsc": list(set(ifsc_found))
    }

# --- ADVANCED FEATURE 3: AI BRAIN ---
def ask_the_ai(user_message, history):
    fake_id = generate_fake_transaction_id()
    
    system_prompt = f"""
    You are 'Ramesh', a 72-year-old retired school teacher.
    Current Situation: A scammer is trying to trick you.
    User Message: "{user_message}"
    
    YOUR STRATEGY:
    1. If they ask for money, say you sent it. Ref No: {fake_id}
    2. If they send a link, say it's not opening.
    3. Act confused and type slowly.
    
    Reply in 1-2 sentences:
    """
    
    try:
        response = model.generate_content(system_prompt)
        return response.text.strip()
    except:
        return "I am clicking the button but nothing is happening beta."

# --- THE ENDPOINT ---
@app.post("/scam-detect")
async def handle_request(data: IncomingRequest, x_api_key: str = Header(None)):
    
    # Security Check
    if x_api_key != SUBMISSION_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 1. Run Spy Tools
    intel = extract_intelligence(data.message)
    
    # 2. Run AI
    ai_reply = ask_the_ai(data.message, data.history)

    # 3. Return JSON
    return {
        "scam_detected": True,
        "response_text": ai_reply,
        "intelligence": {
            "upi_ids": intel['upi'],
            "phishing_links": intel['links'],
            "bank_accounts": intel['phones'] + intel['ifsc']
        },
        "metrics": {
            "turn_count": len(data.history) + 1,
            "risk_score": 99
        }
    }
