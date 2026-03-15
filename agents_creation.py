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

def parse_vote(task):
    text = task.output.raw.upper()
    if "NO-GO" in text or "NO GO" in text:
        return "NO-GO"
    elif "CONDITIONAL" in text:
        return "CONDITIONAL"
    elif "GO" in text:
        return "GO"
    return "UNDECIDED"

BOARD_PRESETS = {
    "tech": {
        "CFO": "10 years experience in tech startups and SaaS companies. Expert in ARR, burn rate, runway, and venture-backed growth metrics.",
        "CMO": "10 years in tech marketing. Expert in product-led growth, developer marketing, viral loops, and SaaS growth strategies.",
        "Legal": "10 years in tech law. Expert in IP protection, data privacy (GDPR/CCPA), antitrust for digital platforms, and open source licensing.",
        "DA": "10 years challenging tech company assumptions. Expert in identifying hype vs reality, bubble risks, and unsustainable growth claims."
    },
    "healthcare": {
        "CFO": "10 years in healthcare finance. Expert in FDA approval costs, insurance reimbursement models, clinical trial economics, and pharmaceutical pricing.",
        "CMO": "10 years in healthcare marketing. Expert in patient acquisition, HCP engagement, regulatory-compliant advertising, and medical device go-to-market.",
        "Legal": "10 years in healthcare law. Expert in HIPAA compliance, FDA regulations, Medicare/Medicaid rules, clinical liability, and pharmaceutical patents.",
        "DA": "10 years challenging healthcare assumptions. Expert in identifying regulatory risks, patient safety concerns, and clinical trial failures."
    },
    "finance": {
        "CFO": "10 years in banking and fintech. Expert in capital requirements, risk-weighted assets, Basel regulations, and financial product economics.",
        "CMO": "10 years in financial services marketing. Expert in trust-building, compliance marketing, B2B financial products, and wealth management client acquisition.",
        "Legal": "10 years in financial law. Expert in SEC regulations, Dodd-Frank compliance, AML/KYC requirements, banking charters, and consumer lending laws.",
        "DA": "10 years challenging financial assumptions. Expert in identifying systemic risks, hidden exposures, regulatory traps, and market manipulation risks."
    },
    "retail": {
        "CFO": "10 years in retail and e-commerce finance. Expert in unit economics, inventory management, omnichannel profitability, and supply chain costs.",
        "CMO": "10 years in retail marketing. Expert in customer acquisition, brand loyalty programs, DTC strategies, seasonal demand planning, and marketplace dynamics.",
        "Legal": "10 years in retail law. Expert in consumer protection, supply chain contracts, labor law, product liability, and international trade regulations.",
        "DA": "10 years challenging retail assumptions. Expert in identifying margin compression, supply chain risks, market saturation, and consumer behavior shifts."
    }
}
def set_board_expertise(board_type):
    preset = BOARD_PRESETS.get(board_type, BOARD_PRESETS["tech"])
    CFO_agent.backstory = preset["CFO"]
    CMO_agent.backstory = preset["CMO"]
    Legal_agent.backstory = preset["Legal"]
    Devils_Advocate_agent.backstory = preset["DA"]
# ═══════════════════════════════════════════════
# PHASE 1: RESEARCH — Individual agent functions
# ═══════════════════════════════════════════════

def run_research_cfo(question):
    task_cfo = Task(
        description=f"""As the CFO, analyze this strategic question from a FINANCIAL perspective:
        
        QUESTION: {question}
        
        Use your search tool to find real financial data.
        Cover:
        1. What will this cost? (capital required, operational expenses)
        2. What's the expected revenue impact?
        3. What's the ROI timeline?
        4. What financial risks exist?
        
        Keep under 300 words. Cite specific numbers.
        IMPORTANT: For every key data point, cite your source. Format: [Source: URL]""",
        agent=CFO_agent,
        expected_output="Financial analysis with specific numbers and a clear recommendation"
    )
    crew = Crew(agents=[CFO_agent], tasks=[task_cfo], process=Process.sequential, verbose=True)
    crew.kickoff()
    return task_cfo


def run_research_cmo(question):
    task_cmo = Task(
        description=f"""As a CMO, analyze this strategic question from a MARKETING perspective:
        
        QUESTION: {question}
        
        Use your search tool to find real marketing data.
        Cover:
        1. What are the customer needs?
        2. What is the market demand?
        3. Who is the competition?
        4. What is the marketing strategy?
        
        Keep under 300 words. Cite specific numbers.
        IMPORTANT: For every key data point, cite your source. Format: [Source: URL]""",
        agent=CMO_agent,
        expected_output="Marketing analysis with specific numbers and a clear recommendation"
    )
    crew = Crew(agents=[CMO_agent], tasks=[task_cmo], process=Process.sequential, verbose=True)
    crew.kickoff()
    return task_cmo


def run_research_legal(question):
    task_legal = Task(
        description=f"""As a Legal expert, analyze this strategic question from a LEGAL perspective:
        
        QUESTION: {question}
        
        Use your search tool to find real legal data.
        Cover:
        1. What are the regulatory requirements?
        2. What are the potential legal risks?
        3. What is the compliance strategy?
        4. What is the risk assessment?
        
        Keep under 300 words. Cite specific numbers.
        IMPORTANT: For every key data point, cite your source. Format: [Source: URL]""",
        agent=Legal_agent,
        expected_output="Legal analysis with specific numbers and a clear recommendation"
    )
    crew = Crew(agents=[Legal_agent], tasks=[task_legal], process=Process.sequential, verbose=True)
    crew.kickoff()
    return task_legal


# ═══════════════════════════════════════════════
# PHASE 2: DEBATE ROUND 1 — Individual agent functions
# ═══════════════════════════════════════════════

def run_debate1_cfo(question, task_cfo, task_cmo, task_legal):
    debate_cfo = Task(
        description=f"""ROUND 1 — OPENING STATEMENT. You are the CFO.
        Read all research outputs and state your position on: {question}
        
        1. State your position: FOR, AGAINST, or CONDITIONAL
        2. Present your top 3 financial arguments with evidence
        3. Identify the #1 financial risk
        
        Keep under 200 words.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.""",
        agent=CFO_agent,
        context=[task_cfo, task_cmo, task_legal],
        expected_output="CFO's opening position with financial arguments"
    )
    crew = Crew(agents=[CFO_agent], tasks=[debate_cfo], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_cfo


def run_debate1_cmo(question, task_cfo, task_cmo, task_legal, debate_cfo):
    debate_cmo = Task(
        description=f"""ROUND 1 — OPENING STATEMENT. You are the CMO.
        Read all research outputs and the CFO's statement. State your position on: {question}
        
        1. State your position: FOR, AGAINST, or CONDITIONAL
        2. Present your top 3 market arguments with evidence
        3. Respond to CFO if you agree or disagree and why
        
        Keep under 200 words.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL].
        When referencing another agent's argument, name them directly.""",
        agent=CMO_agent,
        context=[task_cfo, task_cmo, task_legal, debate_cfo],
        expected_output="CMO's opening position with market arguments"
    )
    crew = Crew(agents=[CMO_agent], tasks=[debate_cmo], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_cmo


def run_debate1_legal(question, task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo):
    debate_legal = Task(
        description=f"""ROUND 1 — OPENING STATEMENT. You are the Legal Counsel.
        Read all research and CFO + CMO statements. State your position on: {question}
        
        1. State your position: FOR, AGAINST, or CONDITIONAL
        2. Present your top 3 legal arguments with evidence
        3. Respond to CFO and CMO if you agree or disagree and why
        
        Keep under 200 words.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.""",
        agent=Legal_agent,
        context=[task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo],
        expected_output="Legal Counsel's opening position with legal arguments"
    )
    crew = Crew(agents=[Legal_agent], tasks=[debate_legal], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_legal


def run_debate1_da(question, task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo, debate_legal):
    debate_da = Task(
        description=f"""ROUND 1 — OPENING STATEMENT. You are the Devil's Advocate.
        Read ALL research and ALL debate statements. Now challenge everyone on: {question}
        
        1. Quote the CFO's specific numbers and explain why they might be wrong
        2. Quote the CMO's market claims and present counter-evidence
        3. Quote Legal's risk assessment and argue it's understated or overstated
        
        Be specific. Name agents. Quote their claims. Provide counter-evidence.
        Keep under 200 words.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.""",
        agent=Devils_Advocate_agent,
        context=[task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo, debate_legal],
        expected_output="Devil's Advocate challenge with specific counter-arguments"
    )
    crew = Crew(agents=[Devils_Advocate_agent], tasks=[debate_da], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_da


# ═══════════════════════════════════════════════
# PHASE 2: DEBATE ROUND 2 — Individual agent functions
# ═══════════════════════════════════════════════

def run_debate2_cfo(question, debate_cfo, debate_cmo, debate_legal, debate_da, human_input=""):
    human_section = ""
    if human_input.strip():
        human_section = f"\n\nThe human decision-maker has asked: '{human_input}'\nYou MUST address this question in your response."

    debate_cfo_2 = Task(
        description=f"""ROUND 2 — REBUTTAL. You are the CFO.
        You have heard all agents' Round 1 positions. Now:
        1. Respond to at least ONE specific argument from another agent by name
        2. Defend OR update your financial position based on what you heard
        3. If the Devil's Advocate challenged your numbers, address it directly
        {human_section}
        
        Keep under 200 words. Be specific — quote other agents' claims.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.""",
        agent=CFO_agent,
        context=[debate_cfo, debate_cmo, debate_legal, debate_da],
        expected_output="A rebuttal addressing other agents' specific points with financial counter-arguments"
    )
    crew = Crew(agents=[CFO_agent], tasks=[debate_cfo_2], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_cfo_2


def run_debate2_cmo(question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, human_input=""):
    human_section = ""
    if human_input.strip():
        human_section = f"\n\nThe human decision-maker has asked: '{human_input}'\nYou MUST address this question in your response."

    debate_cmo_2 = Task(
        description=f"""ROUND 2 — REBUTTAL. You are the CMO.
        You have heard all agents' Round 1 positions and the CFO's Round 2 rebuttal. Now:
        1. Respond to at least ONE specific argument from another agent by name
        2. Defend OR update your market analysis based on what you heard
        3. If the Devil's Advocate challenged your claims, address it directly
        {human_section}
        
        Keep under 200 words. Be specific — quote other agents' claims.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.""",
        agent=CMO_agent,
        context=[debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2],
        expected_output="A rebuttal addressing other agents' specific points with market counter-arguments"
    )
    crew = Crew(agents=[CMO_agent], tasks=[debate_cmo_2], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_cmo_2


def run_debate2_legal(question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2, human_input=""):
    human_section = ""
    if human_input.strip():
        human_section = f"\n\nThe human decision-maker has asked: '{human_input}'\nYou MUST address this question in your response."

    debate_legal_2 = Task(
        description=f"""ROUND 2 — REBUTTAL. You are the Legal Counsel.
        You have heard all Round 1 positions and CFO and CMO Round 2 rebuttals. Now:
        1. Respond to at least ONE specific argument from another agent by name
        2. Defend OR update your legal position based on what you heard
        3. If CFO or CMO dismissed your legal risks, push back with evidence
        {human_section}
        
        Keep under 200 words. Be specific — quote other agents' claims.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.""",
        agent=Legal_agent,
        context=[debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2],
        expected_output="A rebuttal addressing other agents' specific points with legal counter-arguments"
    )
    crew = Crew(agents=[Legal_agent], tasks=[debate_legal_2], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_legal_2


def run_debate2_da(question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2, debate_legal_2, human_input=""):
    human_section = ""
    if human_input.strip():
        human_section = f"\n\nThe human decision-maker has asked: '{human_input}'\nYou MUST address this question in your response."

    debate_da_2 = Task(
        description=f"""ROUND 2 — REBUTTAL. You are the Devil's Advocate.
        You have heard everyone's Round 1 positions AND their Round 2 rebuttals. Now:
        1. Identify who changed their position and whether the change is justified
        2. Find the WEAKEST argument that survived Round 1 unchallenged
        3. Quote specific numbers or claims from other agents and explain why they are wrong
        {human_section}
        
        Keep under 200 words. Be ruthless but fair — attack arguments, not agents.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.""",
        agent=Devils_Advocate_agent,
        context=[debate_cfo, debate_cmo, debate_legal, debate_da,
                 debate_cfo_2, debate_cmo_2, debate_legal_2],
        expected_output="A sharp rebuttal challenging the weakest surviving arguments"
    )
    crew = Crew(agents=[Devils_Advocate_agent], tasks=[debate_da_2], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_da_2


# ═══════════════════════════════════════════════
# PHASE 2: DEBATE ROUND 3 — Individual agent functions
# ═══════════════════════════════════════════════

def run_debate3_cfo(question, all_context):
    debate_cfo_3 = Task(
        description=f"""FINAL ROUND. You are the CFO. One paragraph only.
        State: GO / NO-GO / CONDITIONAL on: {question}
        Your single strongest financial argument. Quote specific numbers.
        One financial risk that must be monitored.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.
        State your confidence level (0-100%) in your position and explain why.""",
        agent=CFO_agent,
        context=all_context,
        expected_output="Final CFO position: GO/NO-GO/CONDITIONAL with one reason and one risk"
    )
    crew = Crew(agents=[CFO_agent], tasks=[debate_cfo_3], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_cfo_3


def run_debate3_cmo(question, all_context):
    debate_cmo_3 = Task(
        description=f"""FINAL ROUND. You are the CMO. One paragraph only.
        State: GO / NO-GO / CONDITIONAL on: {question}
        Your single strongest market argument. Quote specific numbers.
        One market risk that must be monitored.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.
        State your confidence level (0-100%) in your position and explain why.""",
        agent=CMO_agent,
        context=all_context,
        expected_output="Final CMO position: GO/NO-GO/CONDITIONAL with one reason and one risk"
    )
    crew = Crew(agents=[CMO_agent], tasks=[debate_cmo_3], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_cmo_3


def run_debate3_legal(question, all_context):
    debate_legal_3 = Task(
        description=f"""FINAL ROUND. You are the Legal Counsel. One paragraph only.
        State: GO / NO-GO / CONDITIONAL on: {question}
        Your single strongest legal argument. Quote specific numbers.
        One legal risk that must be monitored.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.
        State your confidence level (0-100%) in your position and explain why.""",
        agent=Legal_agent,
        context=all_context,
        expected_output="Final Legal position: GO/NO-GO/CONDITIONAL with one reason and one risk"
    )
    crew = Crew(agents=[Legal_agent], tasks=[debate_legal_3], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_legal_3


def run_debate3_da(question, all_context):
    debate_da_3 = Task(
        description=f"""FINAL ROUND. You are the Devil's Advocate. One paragraph only.
        State: GO / NO-GO / CONDITIONAL on: {question}
        Your single strongest challenge. Quote specific numbers.
        The one risk everyone else is underestimating.
        IMPORTANT: If you cite external data, include the source. Format: [Source: URL]. 
        When referencing another agent's argument, name them directly.
        State your confidence level (0-100%) in your position and explain why.""",
        agent=Devils_Advocate_agent,
        context=all_context,
        expected_output="Final Devil's Advocate position with the strongest remaining challenge"
    )
    crew = Crew(agents=[Devils_Advocate_agent], tasks=[debate_da_3], process=Process.sequential, verbose=True)
    crew.kickoff()
    return debate_da_3


# ═══════════════════════════════════════════════
# PHASE 3: MODERATOR SYNTHESIS
# ═══════════════════════════════════════════════

def run_moderator(question, all_context):
    moderator_task = Task(
        description=f"""You are the Board Moderator. Synthesize the ENTIRE debate on: {question}
        
        You MUST produce a Strategy Brief using EXACTLY this format. Do not skip any section.

        ## EXECUTIVE SUMMARY
        (Exactly 2 sentences summarizing the debate outcome)

        ## BOARD VOTE
        - CFO: [GO/NO-GO/CONDITIONAL]
        - CMO: [GO/NO-GO/CONDITIONAL]
        - Legal Counsel: [GO/NO-GO/CONDITIONAL]
        - Devil's Advocate: [GO/NO-GO/CONDITIONAL]
        - Overall: X for GO, Y for NO-GO, Z for CONDITIONAL

        ## CONSENSUS POINTS
        - (What all agents agreed on, bullet points)

        ## KEY DISAGREEMENTS
        - (Where agents differed, name the agents and their positions)

        ## RISK MATRIX
        | Risk | Severity | Probability | Flagged By |
        |------|----------|-------------|------------|
        | (risk 1) | HIGH/MED/LOW | HIGH/MED/LOW | (agent name) |
        | (risk 2) | HIGH/MED/LOW | HIGH/MED/LOW | (agent name) |
        | (risk 3) | HIGH/MED/LOW | HIGH/MED/LOW | (agent name) |

        ## OPTIONS & TRADE-OFFS
        **Option A:** (describe) → Pros: ... | Cons: ...
        **Option B:** (describe) → Pros: ... | Cons: ...
        **Option C:** (describe) → Pros: ... | Cons: ...

        ## RECOMMENDED NEXT STEPS
        1. (Immediate action regardless of decision)
        2. (Second step)
        3. (Third step)

        Be neutral. Do not take sides. Base everything on what agents actually said in the debate.
        Keep under 400 words.""",
        agent=moderator_agent,
        context=all_context,
        expected_output="A structured strategy brief synthesizing the entire debate"
    )
    crew = Crew(agents=[moderator_agent], tasks=[moderator_task], process=Process.sequential, verbose=True)
    crew.kickoff()
    return moderator_task


# ═══════════════════════════════════════════════
# RUN FULL DEBATE — for terminal testing
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    question = input("What is the strategic question? ")

    print("\n🔬 PHASE 1: RESEARCH")
    print("=" * 60)
    task_cfo = run_research_cfo(question)
    print("✅ CFO research done")
    task_cmo = run_research_cmo(question)
    print("✅ CMO research done")
    task_legal = run_research_legal(question)
    print("✅ Legal research done")

    print("\n🏛️ PHASE 2: DEBATE — ROUND 1")
    print("=" * 60)
    debate_cfo = run_debate1_cfo(question, task_cfo, task_cmo, task_legal)
    print("✅ CFO Round 1 done")
    debate_cmo = run_debate1_cmo(question, task_cfo, task_cmo, task_legal, debate_cfo)
    print("✅ CMO Round 1 done")
    debate_legal = run_debate1_legal(question, task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo)
    print("✅ Legal Round 1 done")
    debate_da = run_debate1_da(question, task_cfo, task_cmo, task_legal, debate_cfo, debate_cmo, debate_legal)
    print("✅ Devil's Advocate Round 1 done")

    human_input = input("\n💬 Ask the board a question (or press Enter to skip): ")

    print("\n🏛️ PHASE 2: DEBATE — ROUND 2 (REBUTTAL)")
    print("=" * 60)
    debate_cfo_2 = run_debate2_cfo(question, debate_cfo, debate_cmo, debate_legal, debate_da, human_input)
    print("✅ CFO Round 2 done")
    debate_cmo_2 = run_debate2_cmo(question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, human_input)
    print("✅ CMO Round 2 done")
    debate_legal_2 = run_debate2_legal(question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2, human_input)
    print("✅ Legal Round 2 done")
    debate_da_2 = run_debate2_da(question, debate_cfo, debate_cmo, debate_legal, debate_da, debate_cfo_2, debate_cmo_2, debate_legal_2, human_input)
    print("✅ Devil's Advocate Round 2 done")

    print("\n🏛️ PHASE 2: DEBATE — ROUND 3 (FINAL POSITIONS)")
    print("=" * 60)
    all_context_r3 = [debate_cfo, debate_cmo, debate_legal, debate_da,
                      debate_cfo_2, debate_cmo_2, debate_legal_2, debate_da_2]
    debate_cfo_3 = run_debate3_cfo(question, all_context_r3)
    print("✅ CFO Round 3 done")
    debate_cmo_3 = run_debate3_cmo(question, all_context_r3 + [debate_cfo_3])
    print("✅ CMO Round 3 done")
    debate_legal_3 = run_debate3_legal(question, all_context_r3 + [debate_cfo_3, debate_cmo_3])
    print("✅ Legal Round 3 done")
    debate_da_3 = run_debate3_da(question, all_context_r3 + [debate_cfo_3, debate_cmo_3, debate_legal_3])
    print("✅ Devil's Advocate Round 3 done")

    print("\n📋 PHASE 3: MODERATOR SYNTHESIS")
    print("=" * 60)
    all_context_mod = [debate_cfo, debate_cmo, debate_legal, debate_da,
                       debate_cfo_2, debate_cmo_2, debate_legal_2, debate_da_2,
                       debate_cfo_3, debate_cmo_3, debate_legal_3, debate_da_3]
    moderator_task = run_moderator(question, all_context_mod)
    
    print("\n" + "=" * 60)
    print("🏛️ SHADOW BOARD — FINAL STRATEGY BRIEF")
    print("=" * 60)
    print(moderator_task.output.raw)