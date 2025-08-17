from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Enable CORS for GitHub frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Rule-based responses
health_responses = {
    "fever": "🤒 For fever, stay hydrated and take paracetamol if needed. If it persists, consult a doctor.",
    "headache": "💊 For headaches, rest well, drink water, and avoid screen time. If severe, consult a doctor.",
    "cough": "🤧 For cough, try warm fluids and rest. If it lasts more than a week, consult a physician.",
    "covid": "🦠 If you suspect COVID-19, isolate, wear a mask, and get tested immediately.",
    "cold": "❄️ Common cold can be relieved with rest, hydration, and steam inhalation.",
}

# HuggingFace API (lightweight AI fallback)
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
HF_HEADERS = {"Authorization": "Bearer YOUR_HF_API_KEY"}  # 🔑 Replace with your HuggingFace API key

@app.post("/chat")
def chat(request: ChatRequest):
    user_msg = request.message.lower()

    # Rule-based match
    for key in health_responses:
        if key in user_msg:
            return {"reply": health_responses[key]}

    # AI fallback (only if no rule matched)
    try:
        response = requests.post(
            HF_API_URL,
            headers=HF_HEADERS,
            json={"inputs": request.message},
            timeout=10
        )
        if response.status_code == 200:
            ai_reply = response.json()[0]["generated_text"]
            return {"reply": ai_reply}
        else:
            return {"reply": "⚠️ AI service not available. Please try again later."}
    except Exception as e:
        return {"reply": f"⚠️ Error contacting AI service: {str(e)}"}

