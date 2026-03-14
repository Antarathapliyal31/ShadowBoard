from crewai import Agent, Task, Process, LLM, Crew
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
load_dotenv()
import os

# ═══════════════════════════════════════════════
# SETUP — runs once when this file is imported
# ═══════════════════════════════════════════════

gemini = LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
serper = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

# ═══════════════════════════════════════════════
# AGENT DEFINITIONS — same agents used in all phases
# ═══════════════════════════════════════════════

CFO_agent = Agent(
    role="CFO",
    goal="Provide financial analysis to board members on whether we can afford this decision",
    backstory="""Act as a senior level financial analyst who has 10 years of experience 
    in this field and has worked in many startups. Provide your viewpoint regarding 
    financial analysis (revenue, cost, ROI)""",
    tools=[serper], llm=gemini, verbose=True
)

CMO_agent = Agent(
    role="CMO",
    goal="Provide marketing analysis to board members on whether customers want this",
    backstory="""Act as a senior level marketing analysis expert who has 10 years of 
    experience in this field and has worked in many startups. Provide your viewpoint 
    regarding marketing analysis (customer needs, market demand, competition)""",
    tools=[serper], llm=gemini, verbose=True
)

Legal_agent = Agent(
    role="Legal Counsel",
    goal="Provide legal expert opinion on regulatory risks and compliance issues",
    backstory="""Act as a senior level legal expert who has 10 years of experience 
    and has worked in many high-level firms as legal analyst. Provide your viewpoint 
    regarding legal analysis (regulatory compliance, risk assessment)""",
    tools=[serper], llm=gemini, verbose=True
)

Devils_Advocate_agent = Agent(
    role="Devils Advocate",
    goal="Challenge every other agent's assumptions and provide critical feedback",
    backstory="""Act as a senior level expert in running a global level company who 
    has knowledge of legal, marketing and financial aspects with 10 years of experience""",
    tools=[serper], llm=gemini, verbose=True
)

moderator_agent = Agent(
    role="Board Moderator",
    goal="Synthesize all debate points into a clear, balanced final recommendation",
    backstory="""Act as a senior level expert in running a global level company who 
    has knowledge of legal, marketing and financial aspects with 20 years of experience. 
    You are perfectly neutral and never take sides.""",
    llm=gemini, verbose=True
)


# ═══════════════════════════════════════════════
# PHASE 1: RESEARCH
# ═══════════════════════════════════════════════

def run_research(question):
    task_cfo = Task(
        description=f"""As the CFO, analyze this strategic question from a FINANCIAL perspective:
        
        QUESTION: {question}
        
        Use your search tool to find real financial data.
        Cover:
        1. What will this cost? (capital required, operational expenses)
        2. What's the expected revenue impact?
        3. What's the ROI timeline?
        4. What financial risks exist?
        
        Keep under 300 words. Cite specific numbers.""",
        agent=CFO_agent,
        expected_output="Financial analysis with specific numbers and a clear recommendation"
    )

    task_cmo = Task(
        description=f"""As a CMO, analyze this strategic question from a MARKETING perspective:
        
        QUESTION: {question}
        
        Use your search tool to find real marketing data.
        Cover:
        1. What are the customer needs?
        2. What is the market demand?
        3. Who is the competition?
        4. What is the marketing strategy?
        
        Keep under 300 words. Cite specific numbers.""",
        agent=CMO_agent,
        expected_output="Marketing analysis with specific numbers and a clear recommendation"
    )

    task_legal = Task(
        description=f"""As a Legal expert, analyze this strategic question from a LEGAL perspective:
        
        QUESTION: {question}
        
        Use your search tool to find real legal data.
        Cover:
        1. What are the regulatory requirements?
        2. What are the potential legal risks?
        3. What is the compliance strategy?
        4. What is the risk assessment?
        
        Keep under 300 words. Cite specific numbers.""",
        agent=Legal_agent,
        expected_output="Legal analysis with specific numbers and a clear recommendation"
    )

    crew = Crew(
        agents=[CFO_agent, CMO_agent, Legal_agent],
        tasks=[task_cfo, task_cmo, task_legal],
        process=Process.sequential, verbose=True
    )
    result = crew.kickoff()

    return {
        "result": result,
        "task_cfo": task_cfo,
        "task_cmo": task_cmo,
        "task_legal": task_legal
    }


# ═══════════════════════════════════════════════
# PHASE 2: DEBATE ROUND 1
# ═══════════════════════════════════════════════

def run_debate_round1(question, research_tasks):
    task_cfo = research_tasks["task_cfo"]
    task_cmo = research_tasks["task_cmo"]
    task_legal = research_tasks["task_legal"]

    debate_cfo = Task(
        description=f"""ROUND 1 — OPENING STATEMENT. You are the CFO.
        Read all research outputs and state your position on: {question}
        
        1. State your position: FOR, AGAINST, or CONDITIONAL
        2. Present your top 3 financial arguments with evidence
        3. Identify the #1 financial risk
        
        Keep under 200 words.""",
        agent=CFO_agent,
        context=[task_cfo, task_cmo, task_legal],
        expected_output="CFO's opening position with financial arguments"
    )

    debate_cmo = Task(
        description=f"""ROUND 1 — OPENING STATEMENT. You are the CMO.
        Read all research outputs and the CFO's statement. State your position on: {question}
        
        1. State your position: FOR, AGAINST, or CONDITIONAL
        2. Present your top 3 market arguments with evidence
        3. Respond to CFO if you agree or disagree and why
        
        Keep under 200 words.""",
        agent=CMO_agent,
        context=[task_cfo, task_cmo, task_legal, debate_cfo],
        expected_output="CMO's opening position with market arguments"
    )

    debate_legal = Task(
        description=f"""ROUND 1 — OPENING STATEMENT. You are the Legal Counsel.
        Read all research and CFO + CMO statements. State your position on: {question}
        
        1. State your position: FOR, AGAINST, or CONDITIONAL
        2. Present your top 3 legal arguments with evidence
        3. Respond to CFO and CMO if you agree or disagree and why
        
        Keep under 200 words.""",
        agent=Legal_agent,
        context=[task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo],
        expected_output="Legal Counsel's opening position with legal arguments"
    )

    debate_da = Task(
        description=f"""ROUND 1 — OPENING STATEMENT. You are the Devil's Advocate.
        Read ALL research and ALL debate statements. Now challenge everyone on: {question}
        
        1. Quote the CFO's specific numbers and explain why they might be wrong
        2. Quote the CMO's market claims and present counter-evidence
        3. Quote Legal's risk assessment and argue it's understated or overstated
        
        Be specific. Name agents. Quote their claims. Provide counter-evidence.
        Keep under 200 words.""",
        agent=Devils_Advocate_agent,
        context=[task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo, debate_legal],
        expected_output="Devil's Advocate challenge with specific counter-arguments"
    )

    crew = Crew(
        agents=[CFO_agent, CMO_agent, Legal_agent, Devils_Advocate_agent],
        tasks=[debate_cfo, debate_cmo, debate_legal, debate_da],
        process=Process.sequential, verbose=True
    )
    result = crew.kickoff()

    return {
        "result": result,
        "debate_cfo": debate_cfo,
        "debate_cmo": debate_cmo,
        "debate_legal": debate_legal,
        "debate_da": debate_da
    }


# ═══════════════════════════════════════════════
# PHASE 2: DEBATE ROUND 2 (REBUTTAL + HITL)
# ═══════════════════════════════════════════════

def run_debate_round2(question, round1_tasks, human_input=""):
    debate_cfo = round1_tasks["debate_cfo"]
    debate_cmo = round1_tasks["debate_cmo"]
    debate_legal = round1_tasks["debate_legal"]
    debate_da = round1_tasks["debate_da"]

    human_section = ""
    if human_input.strip():
        human_section = f"""
        
        The human decision-maker has asked: '{human_input}'
        You MUST address this question in your response."""

    debate_cfo_2 = Task(
        description=f"""ROUND 2 — REBUTTAL. You are the CFO.
        You have heard all agents' Round 1 positions. Now:
        1. Respond to at least ONE specific argument from another agent by name
        2. Defend OR update your financial position based on what you heard
        3. If the Devil's Advocate challenged your numbers, address it directly
        {human_section}
        
        Keep under 200 words. Be specific — quote other agents' claims.""",
        agent=CFO_agent,
        context=[debate_cfo, debate_cmo, debate_legal, debate_da],
        expected_output="A rebuttal addressing other agents' specific points with financial counter-arguments"
    )

    debate_cmo_2 = Task(
        description=f"""ROUND 2 — REBUTTAL. You are the CMO.
        You have heard all agents' Round 1 positions and the CFO's Round 2 rebuttal. Now:
        1. Respond to at least ONE specific argument from another agent by name
        2. Defend OR update your market analysis based on what you heard
        3. If the Devil's Advocate challenged your claims, address it directly
        {human_section}
        
        Keep under 200 words. Be specific — quote other agents' claims.""",
        agent=CMO_agent,
        context=[debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2],
        expected_output="A rebuttal addressing other agents' specific points with market counter-arguments"
    )

    debate_legal_2 = Task(
        description=f"""ROUND 2 — REBUTTAL. You are the Legal Counsel.
        You have heard all Round 1 positions and CFO and CMO Round 2 rebuttals. Now:
        1. Respond to at least ONE specific argument from another agent by name
        2. Defend OR update your legal position based on what you heard
        3. If CFO or CMO dismissed your legal risks, push back with evidence
        {human_section}
        
        Keep under 200 words. Be specific — quote other agents' claims.""",
        agent=Legal_agent,
        context=[debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2],
        expected_output="A rebuttal addressing other agents' specific points with legal counter-arguments"
    )

    debate_da_2 = Task(
        description=f"""ROUND 2 — REBUTTAL. You are the Devil's Advocate.
        You have heard everyone's Round 1 positions AND their Round 2 rebuttals. Now:
        1. Identify who changed their position and whether the change is justified
        2. Find the WEAKEST argument that survived Round 1 unchallenged
        3. Quote specific numbers or claims from other agents and explain why they are wrong
        {human_section}
        
        Keep under 200 words. Be ruthless but fair — attack arguments, not agents.""",
        agent=Devils_Advocate_agent,
        context=[debate_cfo, debate_cmo, debate_legal, debate_da,
                 debate_cfo_2, debate_cmo_2, debate_legal_2],
        expected_output="A sharp rebuttal challenging the weakest surviving arguments"
    )

    crew = Crew(
        agents=[CFO_agent, CMO_agent, Legal_agent, Devils_Advocate_agent],
        tasks=[debate_cfo_2, debate_cmo_2, debate_legal_2, debate_da_2],
        process=Process.sequential, verbose=True
    )
    result = crew.kickoff()

    return {
        "result": result,
        "debate_cfo_2": debate_cfo_2,
        "debate_cmo_2": debate_cmo_2,
        "debate_legal_2": debate_legal_2,
        "debate_da_2": debate_da_2
    }


# ═══════════════════════════════════════════════
# PHASE 2: DEBATE ROUND 3 (FINAL POSITIONS)
# ═══════════════════════════════════════════════

def run_debate_round3(question, round1_tasks, round2_tasks):
    all_context = [
        round1_tasks["debate_cfo"], round1_tasks["debate_cmo"],
        round1_tasks["debate_legal"], round1_tasks["debate_da"],
        round2_tasks["debate_cfo_2"], round2_tasks["debate_cmo_2"],
        round2_tasks["debate_legal_2"], round2_tasks["debate_da_2"]
    ]

    debate_cfo_3 = Task(
        description=f"""FINAL ROUND. You are the CFO. One paragraph only.
        State: GO / NO-GO / CONDITIONAL on: {question}
        Your single strongest financial argument. Quote specific numbers.
        One financial risk that must be monitored.""",
        agent=CFO_agent,
        context=all_context,
        expected_output="Final CFO position: GO/NO-GO/CONDITIONAL with one reason and one risk"
    )

    debate_cmo_3 = Task(
        description=f"""FINAL ROUND. You are the CMO. One paragraph only.
        State: GO / NO-GO / CONDITIONAL on: {question}
        Your single strongest market argument. Quote specific numbers.
        One market risk that must be monitored.""",
        agent=CMO_agent,
        context=all_context + [debate_cfo_3],
        expected_output="Final CMO position: GO/NO-GO/CONDITIONAL with one reason and one risk"
    )

    debate_legal_3 = Task(
        description=f"""FINAL ROUND. You are the Legal Counsel. One paragraph only.
        State: GO / NO-GO / CONDITIONAL on: {question}
        Your single strongest legal argument. Quote specific numbers.
        One legal risk that must be monitored.""",
        agent=Legal_agent,
        context=all_context + [debate_cfo_3, debate_cmo_3],
        expected_output="Final Legal position: GO/NO-GO/CONDITIONAL with one reason and one risk"
    )

    debate_da_3 = Task(
        description=f"""FINAL ROUND. You are the Devil's Advocate. One paragraph only.
        State: GO / NO-GO / CONDITIONAL on: {question}
        Your single strongest challenge. Quote specific numbers.
        The one risk everyone else is underestimating.""",
        agent=Devils_Advocate_agent,
        context=all_context + [debate_cfo_3, debate_cmo_3, debate_legal_3],
        expected_output="Final Devil's Advocate position with the strongest remaining challenge"
    )

    crew = Crew(
        agents=[CFO_agent, CMO_agent, Legal_agent, Devils_Advocate_agent],
        tasks=[debate_cfo_3, debate_cmo_3, debate_legal_3, debate_da_3],
        process=Process.sequential, verbose=True
    )
    result = crew.kickoff()

    return {
        "result": result,
        "debate_cfo_3": debate_cfo_3,
        "debate_cmo_3": debate_cmo_3,
        "debate_legal_3": debate_legal_3,
        "debate_da_3": debate_da_3
    }


# ═══════════════════════════════════════════════
# PHASE 3: MODERATOR SYNTHESIS
# ═══════════════════════════════════════════════

def run_moderator(question, round1_tasks, round2_tasks, round3_tasks):
    all_context = [
        round1_tasks["debate_cfo"], round1_tasks["debate_cmo"],
        round1_tasks["debate_legal"], round1_tasks["debate_da"],
        round2_tasks["debate_cfo_2"], round2_tasks["debate_cmo_2"],
        round2_tasks["debate_legal_2"], round2_tasks["debate_da_2"],
        round3_tasks["debate_cfo_3"], round3_tasks["debate_cmo_3"],
        round3_tasks["debate_legal_3"], round3_tasks["debate_da_3"]
    ]

    moderator_task = Task(
        description=f"""You are the Board Moderator. Synthesize the ENTIRE debate on: {question}
        
        Produce a Strategy Brief with these sections:
        1. EXECUTIVE SUMMARY (2-3 sentences)
        2. BOARD SENTIMENT (X for GO, Y for NO-GO, Z for CONDITIONAL)
        3. CONSENSUS POINTS (what all agents agreed on)
        4. KEY DISAGREEMENTS (where agents differed and why)
        5. RISK MATRIX (risk | severity HIGH/MED/LOW | flagged by which agent)
        6. RECOMMENDATION (your balanced recommendation with trade-offs)
        
        Keep under 300 words. Be neutral. Do not take sides.""",
        agent=moderator_agent,
        context=all_context,
        expected_output="A structured strategy brief synthesizing the entire debate"
    )

    crew = Crew(
        agents=[moderator_agent],
        tasks=[moderator_task],
        process=Process.sequential, verbose=True
    )
    result = crew.kickoff()

    return {"result": result}


# ═══════════════════════════════════════════════
# RUN FULL DEBATE — for terminal testing
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    question = input("What is the strategic question? ")

    print("\n🔬 PHASE 1: RESEARCH")
    print("=" * 60)
    research = run_research(question)

    print("\n PHASE 2: DEBATE — ROUND 1")
    print("=" * 60)
    round1 = run_debate_round1(question, research)

    human_input = input("\n💬 Ask the board a question (or press Enter to skip): ")

    print("\n PHASE 2: DEBATE — ROUND 2 (REBUTTAL)")
    print("=" * 60)
    round2 = run_debate_round2(question, round1, human_input)

    print("\n PHASE 2: DEBATE — ROUND 3 (FINAL POSITIONS)")
    print("=" * 60)
    round3 = run_debate_round3(question, round1, round2)

    print("\n PHASE 3: MODERATOR SYNTHESIS")
    print("=" * 60)
    final = run_moderator(question, round1, round2, round3)

    print("\n" + "=" * 60)
    print("SHADOW BOARD — FINAL STRATEGY BRIEF")
    print("=" * 60)
    print(final["result"])