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

class HumanInput(BaseModel):
    human_ip: str

sessions_info = {}

@app.get("/")
def home():
    return {"message": "Shadow Board API is running"}

@app.post("/api/session/create")
def session_id_creation(request: SessionRequest):
    session_id = str(uuid.uuid4())
    sessions_info[session_id] = {"question": request.question,"context":request.context}
    return {"session": session_id}

@app.get("/api/{session_id}/download_pdf")
def download_pdf(session_id):
    filepath=f"reports/strategy_brief_{session_id}.pdf"
    return FileResponse(filepath,filename="Shadow_Board_Strategy_Brief.pdf")

@app.get("/api/{session_id}/agents_research")
def agents_research(session_id: str):
    session = sessions_info[session_id]
    question = session["question"]
    context=session.get("context", "")
    full_question=f"{question}\n\n Comapny Context:{context}" if context else question

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

        # ═══ PHASE 2: DEBATE ROUND 2 (one agent at a time) ═══
        yield sse_event("phase", {"phase": "debate", "round": 2})

        yield sse_event("agent_start", {"agent": "CFO", "action": "preparing rebuttal"})
        debate_cfo_2 = run_debate2_cfo(full_question, debate_cfo, debate_cmo, debate_legal, debate_da, human_input)
        yield sse_event("agent_message", {"agent": "CFO", "phase": "debate", "round": 2, "text": debate_cfo_2.output.raw})

        yield sse_event("agent_start", {"agent": "CMO", "action": "preparing rebuttal"})
        debate_cmo_2 = run_debate2_cmo(full_question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, human_input)
        yield sse_event("agent_message", {"agent": "CMO", "phase": "debate", "round": 2, "text": debate_cmo_2.output.raw})

        yield sse_event("agent_start", {"agent": "Legal", "action": "preparing rebuttal"})
        debate_legal_2 = run_debate2_legal(full_question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2, human_input)
        yield sse_event("agent_message", {"agent": "Legal", "phase": "debate", "round": 2, "text": debate_legal_2.output.raw})

        yield sse_event("agent_start", {"agent": "Devils Advocate", "action": "preparing final challenge"})
        debate_da_2 = run_debate2_da(full_question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2, debate_legal_2, human_input)
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

        yield sse_event("complete", {"message": "Shadow Board session complete"})

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/{session_id}/human_input")
def human_input_endpoint(session_id: str, request: HumanInput):
    session_info = sessions_info[session_id]
    session_info["human_input"] = request.human_ip
    return {"status": "received"}