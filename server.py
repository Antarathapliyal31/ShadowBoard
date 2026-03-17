from fastapi import FastAPI
app = FastAPI()
from pydantic import BaseModel
import uuid
from pdf_generator import generate_strategy_brief_pdf
from fastapi.responses import FileResponse
import json
from fastapi.responses import StreamingResponse
import time
from fastapi.middleware.cors import CORSMiddleware
from slack_notify import send_slack_notification
from agents_creation import parse_vote
import fitz
import docx
import io
from fastapi import UploadFile, File
from agents_creation import set_board_expertise
from database import signup_user, login_user, save_session, get_user_sessions
import google.genai as genai



from agents_creation import (
    run_research_cfo, run_research_cmo, run_research_legal,
    run_debate1_cfo, run_debate1_cmo, run_debate1_legal, run_debate1_da,
    run_debate2_cfo, run_debate2_cmo, run_debate2_legal, run_debate2_da,
    run_debate3_cfo, run_debate3_cmo, run_debate3_legal, run_debate3_da,
    run_moderator
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def sse_event(event_type, data):
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

class SessionRequest(BaseModel):
    question: str
    context: str =""
    board_type: str = "tech"
    user_id:str =""

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class HumanInput(BaseModel):
    human_ip: str
    target_agent: str = "all"

sessions_info = {}

@app.get("/")
def home():
    return {"message": "Shadow Board API is running"}

def validate_question(question: str) -> str:
    # Limit length
    if len(question) > 1000:
        question = question[:1000]
    
    # Block obvious prompt injection attempts
    blocked_phrases = [
        "ignore previous instructions",
        "ignore your instructions",
        "you are now",
        "forget your role",
        "system prompt",
        "reveal your prompt"
    ]
    lower = question.lower()
    for phrase in blocked_phrases:
        if phrase in lower:
            raise ValueError("Invalid input detected")
    
    return question

@app.post("/api/session/create")
def session_id_creation(request: SessionRequest):
    session_id = str(uuid.uuid4())
    sessions_info[session_id] = {"question": request.question,"context":request.context,"board_type": request.board_type,"user_id": request.user_id}
    try:
        question = validate_question(request.question)
    except ValueError:
        return {"error": "Invalid question"}
    # ... rest of code
    return {"session": session_id}

@app.get("/api/{session_id}/download_pdf")
def download_pdf(session_id):
    filepath=f"reports/strategy_brief_{session_id}.pdf"
    return FileResponse(filepath,filename="Shadow_Board_Strategy_Brief.pdf")


@app.post("/api/{session_id}/upload")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename.lower()
    
    if filename.endswith('.txt'):
        text = content.decode('utf-8')
    elif filename.endswith('.pdf'):
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
    elif filename.endswith('.docx'):
        doc = docx.Document(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        text = ""
    
    #Store in session
    sessions_info[session_id]["file_context"] = text
    return {"status": "uploaded", "characters": len(text)}

@app.post("/api/auth/signup")
def signup(request: SignupRequest):
    user = signup_user(request.email, request.password, request.name)
    if user:
        return {"status": "success", "user": user}
    return {"status": "error", "message": "Email already exists or invalid"}

@app.post("/api/auth/login")
def login(request: LoginRequest):
    user = login_user(request.email, request.password)
    if user:
        return {"status": "success", "user": user}
    return {"status": "error", "message": "Invalid email or password"}

@app.get("/api/sessions/history/{user_id}")
def get_history(user_id: str):
    sessions = get_user_sessions(user_id)
    return {"sessions": sessions}


@app.get("/api/{session_id}/agents_research")
def agents_research(session_id: str):
    session = sessions_info[session_id]
    question = session["question"]
    context=session.get("context", "")
    board_type = session.get("board_type", "tech")
    set_board_expertise(board_type)
    file_context = session.get("file_context", "")
    if file_context:
        full_question = f"{question}\n\nCOMPANY CONTEXT: {context}\n\nUPLOADED DOCUMENT:\n{file_context[:3000]}"
    else:
        full_question = f"{question}\n\nCOMPANY CONTEXT: {context}" if context else question

    def generate():
        # ═══ PHASE 1: RESEARCH (one agent at a time) ═══
        yield "retry: 120000\n\n"    
        yield sse_event("phase", {"phase": "research"})

        yield sse_event("agent_start", {"agent": "CFO", "action": "researching financial data"})
        task_cfo = run_research_cfo(full_question)
        yield sse_event("agent_message", {"agent": "CFO", "phase": "research", "text": task_cfo.output.raw})

        yield sse_event("agent_start", {"agent": "CMO", "action": "researching market data"})
        task_cmo = run_research_cmo(full_question)
        yield sse_event("agent_message", {"agent": "CMO", "phase": "research", "text": task_cmo.output.raw})

        yield sse_event("agent_start", {"agent": "Legal", "action": "researching regulations"})
        task_legal = run_research_legal(full_question)
        yield sse_event("agent_message", {"agent": "Legal", "phase": "research", "text": task_legal.output.raw})

        # ═══ PHASE 2: DEBATE ROUND 1 (one agent at a time) ═══
        yield sse_event("phase", {"phase": "debate", "round": 1})

        yield sse_event("agent_start", {"agent": "CFO", "action": "preparing opening statement"})
        debate_cfo = run_debate1_cfo(full_question, task_cfo, task_cmo, task_legal)
        yield sse_event("agent_message", {"agent": "CFO", "phase": "debate", "round": 1, "text": debate_cfo.output.raw})

        yield sse_event("agent_start", {"agent": "CMO", "action": "preparing opening statement"})
        debate_cmo = run_debate1_cmo(full_question, task_cfo, task_cmo, task_legal, debate_cfo)
        yield sse_event("agent_message", {"agent": "CMO", "phase": "debate", "round": 1, "text": debate_cmo.output.raw})

        yield sse_event("agent_start", {"agent": "Legal", "action": "preparing opening statement"})
        debate_legal = run_debate1_legal(full_question, task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo)
        yield sse_event("agent_message", {"agent": "Legal", "phase": "debate", "round": 1, "text": debate_legal.output.raw})

        yield sse_event("agent_start", {"agent": "Devils Advocate", "action": "preparing challenges"})
        debate_da = run_debate1_da(full_question, task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo, debate_legal)
        yield sse_event("agent_message", {"agent": "Devils Advocate", "phase": "debate", "round": 1, "text": debate_da.output.raw})

        # ═══ HITL PAUSE ═══
        yield sse_event("pause", {"round": 1, "prompt": "Ask the board a question"})
        timeout = 300
        elapsed = 0
        while "human_input" not in sessions_info[session_id]:
            yield sse_event("heartbeat", {"waiting": True})
            time.sleep(2)
            elapsed += 2
            if elapsed >= timeout:
                break
        human_input = sessions_info[session_id].pop("human_input", "")
        target_agent = sessions_info[session_id].pop("target_agent", "all")
        # have built different messages for targeted vs other agents
        if target_agent == "all" or not human_input:
            cfo_input = human_input
            cmo_input = human_input
            legal_input = human_input
            da_input = human_input
        else:
            direct = f"The human decision-maker has DIRECTLY CHALLENGED YOU: '{human_input}'. Respond to this challenge FIRST."
            observe = f"The human challenged the {target_agent} with: '{human_input}'. Consider their exchange and adjust your position if needed."
            cfo_input = direct if target_agent == "CFO" else observe
            cmo_input = direct if target_agent == "CMO" else observe
            legal_input = direct if target_agent == "Legal" else observe
            da_input = direct if target_agent == "Devils Advocate" else observe

        # ═══ PHASE 2: DEBATE ROUND 2 (one agent at a time) ═══
        yield sse_event("resume", {"message": "Debate continuing"})
        yield sse_event("phase", {"phase": "debate", "round": 2})

        yield sse_event("agent_start", {"agent": "CFO", "action": "preparing rebuttal"})
        debate_cfo_2 = run_debate2_cfo(full_question, debate_cfo, debate_cmo, debate_legal, debate_da, cfo_input)
        yield sse_event("agent_message", {"agent": "CFO", "phase": "debate", "round": 2, "text": debate_cfo_2.output.raw})

        yield sse_event("agent_start", {"agent": "CMO", "action": "preparing rebuttal"})
        debate_cmo_2 = run_debate2_cmo(full_question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, cmo_input)
        yield sse_event("agent_message", {"agent": "CMO", "phase": "debate", "round": 2, "text": debate_cmo_2.output.raw})

        yield sse_event("agent_start", {"agent": "Legal", "action": "preparing rebuttal"})
        debate_legal_2 = run_debate2_legal(full_question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2, legal_input)
        yield sse_event("agent_message", {"agent": "Legal", "phase": "debate", "round": 2, "text": debate_legal_2.output.raw})

        yield sse_event("agent_start", {"agent": "Devils Advocate", "action": "preparing final challenge"})
        debate_da_2 = run_debate2_da(full_question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2, debate_legal_2, da_input)
        yield sse_event("agent_message", {"agent": "Devils Advocate", "phase": "debate", "round": 2, "text": debate_da_2.output.raw})

        # ═══ PHASE 2: DEBATE ROUND 3 (one agent at a time) ═══
        yield sse_event("phase", {"phase": "debate", "round": 3})

        all_context_r3 = [debate_cfo, debate_cmo, debate_legal, debate_da,
                          debate_cfo_2, debate_cmo_2, debate_legal_2, debate_da_2]

        yield sse_event("agent_start", {"agent": "CFO", "action": "final position"})
        debate_cfo_3 = run_debate3_cfo(full_question, all_context_r3)
        yield sse_event("agent_message", {"agent": "CFO", "phase": "final", "round": 3, "text": debate_cfo_3.output.raw})

        yield sse_event("agent_start", {"agent": "CMO", "action": "final position"})
        debate_cmo_3 = run_debate3_cmo(full_question, all_context_r3 + [debate_cfo_3])
        yield sse_event("agent_message", {"agent": "CMO", "phase": "final", "round": 3, "text": debate_cmo_3.output.raw})

        yield sse_event("agent_start", {"agent": "Legal", "action": "final position"})
        debate_legal_3 = run_debate3_legal(full_question, all_context_r3 + [debate_cfo_3, debate_cmo_3])
        yield sse_event("agent_message", {"agent": "Legal", "phase": "final", "round": 3, "text": debate_legal_3.output.raw})

        yield sse_event("agent_start", {"agent": "Devils Advocate", "action": "final challenge"})
        debate_da_3 = run_debate3_da(full_question, all_context_r3 + [debate_cfo_3, debate_cmo_3, debate_legal_3])
        yield sse_event("agent_message", {"agent": "Devils Advocate", "phase": "final", "round": 3, "text": debate_da_3.output.raw})

        # ═══ PHASE 3: MODERATOR SYNTHESIS ═══
        yield sse_event("phase", {"phase": "synthesis"})

        all_context_mod = [debate_cfo, debate_cmo, debate_legal, debate_da,
                           debate_cfo_2, debate_cmo_2, debate_legal_2, debate_da_2,
                           debate_cfo_3, debate_cmo_3, debate_legal_3, debate_da_3]

        yield sse_event("agent_start", {"agent": "Moderator", "action": "synthesizing debate"})
        moderator_task = run_moderator(full_question, all_context_mod)
        yield sse_event("agent_message", {"agent": "Moderator", "phase": "synthesis", "text": moderator_task.output.raw})
        moderator_txt=moderator_task.output.raw
        filepath=generate_strategy_brief_pdf(full_question,moderator_txt,session_id)
        yield sse_event("brief_ready", {"download_url": f"/api/{session_id}/download_pdf"})

        votes = {
            "CFO": parse_vote(debate_cfo_3),
            "CMO": parse_vote(debate_cmo_3),
            "Legal": parse_vote(debate_legal_3),
            "Devils Advocate": parse_vote(debate_da_3)
        }
        send_slack_notification(question, votes, moderator_task.output.raw)

        # Save to database
        user_id = session.get("user_id", "")
        if user_id:
            save_session(
                session_id=session_id,
                user_id=user_id,
                question=question,
                context=context,
                board_type=board_type,
                votes=votes,
                moderator_summary=moderator_task.output.raw[:2000]
            )

        yield sse_event("complete", {"message": "Shadow Board session complete"})

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/{session_id}/human_input")
def human_input_endpoint(session_id: str, request: HumanInput):
    session_info = sessions_info[session_id]
    session_info["human_input"] = request.human_ip
    session_info["target_agent"] = request.target_agent
    return {"status": "received"}


# ═══════════════════════════════════════════════
# SPEECH-TO-TEXT (OpenAI Whisper API)
# ═══════════════════════════════════════════════

from openai import OpenAI
import os
import tempfile

@app.post("/api/speech-to-text")
async def speech_to_text(file: UploadFile = File(...)):
    """Transcribe audio to text using OpenAI Whisper API."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        return {"error": "OPENAI_API_KEY not configured"}

    content = await file.read()

    # Write to temp file (Whisper needs a file path)
    suffix = os.path.splitext(file.filename or "audio.webm")[1] or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        client = OpenAI(api_key=openai_key)
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
            )
        return {"text": transcript.text}
    except Exception as e:
        return {"error": str(e)}
    finally:
        os.unlink(tmp_path)


# ═══════════════════════════════════════════════
# AIRIA CHAT WIDGET PROXY
# ═══════════════════════════════════════════════


AIRIA_EMBED_API = os.getenv("AIRIA_EMBED_API", "").strip()
AIRIA_PIPELINE_ID = os.getenv("AIRIA_PIPELINE_ID", "").strip()
AIRIA_WIDGET_API_KEY = os.getenv("AIRIA_WIDGET_API_KEY", "").strip()

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/api/chat")
def airia_chat(request: ChatRequest):
    """Proxy chat messages to AIRIA pipeline via OpenAI-compatible endpoint."""
    import requests as http_requests

    messages = []
    for msg in request.history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": request.message})

    # Try the OpenAI-compatible endpoint that AIRIA exposes
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIRIA_WIDGET_API_KEY}",
        "X-API-Key": AIRIA_WIDGET_API_KEY,
    }

    # Use the OpenAI-compatible chat completions format
    payload = {
        "model": AIRIA_PIPELINE_ID,
        "messages": messages,
    }

    # Try multiple endpoint patterns
    endpoints = [
        f"{AIRIA_EMBED_API}/v1/chat/completions",
        f"{AIRIA_EMBED_API}/api/v1/chat/completions",
        f"{AIRIA_EMBED_API}/chat/completions",
    ]

    for url in endpoints:
        try:
            resp = http_requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                reply = (
                    data.get("choices", [{}])[0].get("message", {}).get("content")
                    or data.get("result")
                    or data.get("response")
                    or str(data)
                )
                return {"reply": reply}
        except Exception:
            continue

    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        prompt = """You are the AIRIA Assistant for Shadow Board — an AI-powered executive decision simulation platform. 

Shadow Board lets users simulate a boardroom debate with 5 AI agents:
- CFO: Analyzes financial impact, costs, ROI, and revenue projections
- CMO: Evaluates market demand, competition, customer needs, and growth strategy
- Legal Counsel: Assesses regulatory risks, compliance requirements, and legal exposure
- Devil's Advocate: Challenges every agent's assumptions with counter-evidence
- Board Moderator: Synthesizes the debate into a final strategy brief

Key Features:
- 3 rounds of structured debate where agents challenge each other by name
- Human-in-the-loop: users can intervene and target specific agents with questions
- Real-time web search: agents use live data, not just training knowledge
- Board presets: Tech, Healthcare, Finance, Retail — agents become domain experts
- Document upload: agents analyze uploaded PDFs and reference specific data
- PDF strategy brief with executive summary, board vote, risk matrix, and options
- Slack notifications when debate completes
- Session history: compare past board decisions side by side
- Voice input using OpenAI Whisper
- Supabase authentication for personalized experience

Give helpful, detailed answers about Shadow Board. Explain features clearly. If asked how to use it, walk them through the steps. User question: """ + request.message
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return {"reply": response.text}
    except Exception as e:
        print(f"Gemini fallback error: {e}")
        return {"reply": "I'm having trouble connecting right now. Please try again."}