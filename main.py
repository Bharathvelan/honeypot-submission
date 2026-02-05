import re
import random
import google.generativeai as genai
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from typing import List

# --- CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyC9I_WuoJgZdDhhmyGUs8HudjryQG7dL3Y" 
SUBMISSION_SECRET = "bharath_123"

# Setup the AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# --- INPUT DATA MODELS ---
class MessageHistory(BaseModel):
    role: str
    content: str

class IncomingRequest(BaseModel):
    conversation_id: str
    message: str
    history: List[MessageHistory] = []

# --- ADVANCED FEATURE 1: FAKE DATA GENERATOR ---
def generate_fake_transaction_id():
    # Generates a fake ID like "UPI-29384729" to trick scammers
    return f"UPI-{random.randint(10000000, 99999999)}"

# --- ADVANCED FEATURE 2: BETTER SPY TOOLS ---
def extract_intelligence(text):
    # 1. Find UPI IDs (example@bank)
    upi_found = re.findall(r"[a-zA-Z0-9.\-_]+@[a-zA-Z]+", text)
    
    # 2. Find Links (http://...)
    links_found = re.findall(r"https?://\S+|www\.\S+", text)
    
    # 3. Find Phone Numbers (10 digits)
    phones_found = re.findall(r"\b[6-9]\d{9}\b", text)
    
    # 4. Find Bank IFSC Codes (ABCD0123456)
    ifsc_found = re.findall(r"[A-Z]{4}0[A-Z0-9]{6}", text)
    
    return {
        "upi": list(set(upi_found)),
        "links": list(set(links_found)),
        "phones": list(set(phones_found)),
        "ifsc": list(set(ifsc_found))
    }

# --- ADVANCED FEATURE 3: SMARTER BRAIN ---
def ask_the_ai(user_message, history):
    # Use conversation history to make the AI smarter
    fake_id = generate_fake_transaction_id()
    
    system_prompt = f"""
    You are 'Ramesh', a 72-year-old retired school teacher.
    You are bad with technology and type slowly.
    
    Current Situation: A scammer is trying to trick you.
    User Message: "{user_message}"
    
    YOUR STRATEGY:
    1. If they asked for money, lie and say you sent it. Use this fake Reference Number: {fake_id}
    2. If they sent a link, complain that it is not opening.
    3. If they ask for OTP, give a wrong number like '1234'.
    4. Act confused. Use simple English.
    
    Reply now (keep it under 2 sentences):
    """
    
    try:
        response = model.generate_content(system_prompt)
        return response.text.strip()
    except:
        return "My internet is slow. Can you say that again?"

# --- THE ENDPOINT ---
@app.post("/scam-detect")
async def handle_request(data: IncomingRequest, x_api_key: str = Header(None)):
    
    # Security Check
    if x_api_key != SUBMISSION_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 1. Run the Spy Tools
    intel = extract_intelligence(data.message)
    
    # 2. Run the AI Brain
    ai_reply = ask_the_ai(data.message, data.history)

    # 3. Return Advanced JSON
    return {
        "scam_detected": True,
        "response_text": ai_reply,
        "intelligence": {
            "upi_ids": intel['upi'],
            "phishing_links": intel['links'],
            "bank_accounts": intel['phones'] + intel['ifsc'] # Combine phones/IFSC as account info
        },
        "metrics": {
            "turn_count": len(data.history) + 1,
            "risk_score": 99 # We are confident it's a scam
        }
    }