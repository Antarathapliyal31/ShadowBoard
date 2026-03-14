from fastapi import FastAPI
app=FastAPI()
from pydantic import BaseModel
import uuid
from agents_creation import run_research, run_debate_round1,run_debate_round2,run_debate_round3,run_moderator
import json
from fastapi.responses import StreamingResponse
import time
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def sse_event(event_type, data):
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

class SessionRequest(BaseModel):
    question:str

sessions_info={}

@app.post("/api/session/create")
def session_id_creation(request:SessionRequest):
    session_id=str(uuid.uuid4())
    sessions_info[session_id]={"question":request.question}
    return {"session": session_id}

@app.get("/api/{session_id}/agents_research")
def agents_research(session_id:str):
    session=sessions_info[session_id]
    question=session["question"]
    
    def generate():
        yield sse_event("phase",{"phase":"research"})
        research1=run_research(question)

        yield sse_event("agent_message",
                        {"agent":"CFO_agent",
                        "phase":"research", 
                        "text":research1["task_cfo"].output.raw })
        
        yield sse_event("agent_message",
                        {"agent":"CMO_agent",
                        "phase":"research", 
                        "text":research1["task_cmo"].output.raw })
        
        yield sse_event("agent_message",
                        {"agent":"legal_agent",
                        "phase":"research", 
                        "text":research1["task_legal"].output.raw })
        
    
        yield sse_event("phase",{"phase":"debate","round":1})

        debate1=run_debate_round1(question,research1)
        yield sse_event("agent_message",
            {"agent":"CFO",
            "phase":"debate_round1",
            "text":debate1["debate_cfo"].output.raw
        })
        yield sse_event("agent_message",
            {"agent":"CMO",
            "phase":"debate_round1",
            "text":debate1["debate_cmo"].output.raw
        })
        yield sse_event("agent_message",
            {"agent":"legal",
            "phase":"debate_round1",
            "text":debate1["debate_legal"].output.raw
        })
        yield sse_event("agent_message",
            {"agent":"devils_advocate",
            "phase":"debate_round1",
            "text":debate1["debate_da"].output.raw
        })
        yield sse_event("pause",{"phase":"ask the board agents any question"})
        while "human_input" not in sessions_info[session_id]:
            time.sleep(1)
        human_input=sessions_info[session_id]["human_input"]
        sessions_info[session_id].pop("human_input")

        yield sse_event("phase",{"phase":"debate","round":2})
        debate2=run_debate_round2(question,debate1,human_input)
        yield sse_event("agent_message",
            {"agent":"CFO",
            "phase":"debate_round2",
            "text":debate2["debate_cfo_2"].output.raw
        })
        yield sse_event("agent_message",
            {"agent":"CMO",
            "phase":"debate_round2",
            "text":debate2["debate_cmo_2"].output.raw
        })
        yield sse_event("agent_message",
            {"agent":"legal",
            "phase":"debate_round2",
            "text":debate2["debate_legal_2"].output.raw
        })
        yield sse_event("agent_message",
            {"agent":"devils_advocate",
            "phase":"debate_round2",
            "text":debate2["debate_da_2"].output.raw
        })

        yield sse_event("phase",{"phase":"debate","round":3})
        debate3=run_debate_round3(question,debate1,debate2)
        yield sse_event("agent_message",
            {"agent":"CFO",
            "phase":"debate_round3",
            "text":debate3["debate_cfo_3"].output.raw
        })
        yield sse_event("agent_message",
            {"agent":"CMO",
            "phase":"debate_round3",
            "text":debate3["debate_cmo_3"].output.raw
        })
        yield sse_event("agent_message",
            {"agent":"legal",
            "phase":"debate_round3",
            "text":debate3["debate_legal_3"].output.raw
        })
        yield sse_event("agent_message",
            {"agent":"devils_advocate",
            "phase":"debate_round3",
            "text":debate3["debate_da_3"].output.raw
        })

        yield sse_event("phase",{"phase":"final_result"})
        final_result=run_moderator(question,debate1, debate2,debate3)
        yield sse_event("agent_message",{"phase":"final_response",
                                     "agent":"moderator",
                                     "text":final_result["result"]})
        
    return StreamingResponse(generate(), media_type="text/event-stream")


class HumanInput(BaseModel):
    human_ip:str

@app.post("/api/{session_id}/human_input")
def human_input(session_id:str,request:HumanInput):
    session_info=sessions_info[session_id]
    session_info["human_input"]=request.human_ip
    return {"status":"received"}



        

