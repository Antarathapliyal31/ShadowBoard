from multiprocessing import process

from crewai import Agent, Task, Process,LLM, Crew
from crewai.tools import tool
from crewai_tools import SerperDevTool
search = SerperDevTool()
from dotenv import load_dotenv
load_dotenv()
import os

gemini=LLM(model="gemini/gemini-2.5-flash",api_key=os.getenv("GEMINI_API_KEY"))
serper = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))
question=input("What is the strategic question you want to ask your board of directors agents? ")

CFO_agent=Agent(role="CFO",goal="provide your financial analysis to the board members on whether we can afford thie decision or not",backstory="""Act as a senior level financial analyst who has 10 years of experience in this field and has worked in many startups. Provide your viewpoint regarding financial analysis (revenue, cost, ROI)""", tools=[serper],llm=gemini,verbose=True)
CMO_agent=Agent(role="CMO",goal="provides your  marketing analysis to board members on whether the customers really want this product in their market ",backstory="""Act as a senior level marketing analysis expert in market analysis who has 10 years of experience in thsi field and has worked in many startups. Provide your viewpoint regarding marketing analysis (customer needs, market demand, competition)""", tools=[serper],llm=gemini,verbose=True)

Legal_agent=Agent(role="Legal",goal="provides your legal expert opinion to board members on whether they should extend their market or will there be any legal issue which they can encounter",backstory="""Act as a senior level legal expert in market analysis who has 10 years of experience in thsi field and has worked in many high-level firms as legal analyst. Provide your viewpoint regarding legal analysis (regulatory compliance, risk assessment)""", tools=[serper],llm=gemini,verbose=True)

task_cfo = Task(
    description=f"""As the CFO, analyze this strategic question from a 
    FINANCIAL perspective:
    
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
task_cmo=Task(
    description=f"""As a CMO, analyze the strategic question based on the marketing perspective:
    
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
task_legal=Task(
    description=f"""As a Legal expert, analyze the strategic question based on the legal perspective:
    
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
#task4=Task(description="""provide critical analysis on whether we should extend our agentic ai company to china. We are a US based agentic ai firm who has started 2 years ago and has strated getting good profits. Provide your response that are reasonable and understood by board of directors of our company. """,agent=Devils_Advocate_agent,expected_output="a detailed response of your market analysis and your recommendation on whether we should extend our market to china")
crew=Crew(agents=[CFO_agent,CMO_agent,Legal_agent],tasks=[task_cfo,task_cmo,task_legal],process=Process.sequential,verbose=True)
result=crew.kickoff()
print(result)

Devils_Advocate_agent=Agent(role="Devils Advocate",goal="you have to challenge every other agent's assumptions and provide critical feedback and analysis",
                            backstory="""Act as a senior level eexpert in running in a global level company who has knowledge of legal, marketing and financial aspects who has 10 years of experience in this field""",
                              tools=[serper],llm=gemini,verbose=True)

debate_cfo=Task(description="""As a CFO, read the reserach output analysis of other agents and then provide your analysis on financial perspective.""",
                agent=CFO_agent,context=[task_cfo,task_cmo,task_legal],
                expected_output=f"a detailed response of your financial analysis and your recommendation on whether we should do what the {question} wants us to do or not based on financial perspective")

debate_cmo=Task(description="""As a CMO, read the reaserach analysis output of all agents and also read the CFO debate points and then provide your annalysis on market analysis for the question the users asked and also provide your analysis on whether you agree with CFO or not and why? """,
                agent=CMO_agent,context=[task_cfo,task_cmo,task_legal,debate_cfo],
                expected_output=f"a detailed response of your market analysis and your recommendation on whether we should do what the {question} wants us to do or not based on market perspective and also whether you agree with CFO or not and why?")

debate_legal=Task(description="""As a legal expert, read the reaserach analysis output of all agents and also read the CFO and CMO debate points and then provide your annalysis on legal perspective for the question the users asked and also provide your analysis on whether you agree with CFO and CMO or not and why? """,
                  agent=Legal_agent,context=[task_cfo,task_cmo,task_legal,debate_cfo,debate_cmo],
                  expected_output=f"a detailed response of your legal analysis and your recommendation on whether we should do what the {question} wants us to do or not based on legal perspective and also whether you agree with CFO and CMO or not and why?")

debate_devils_advocate=Task(description="""As a devils advocate, read the reaserach analysis output of all agents and also read the CFO, CMO and legal debate points and then provide your critical analysis on the question the users asked and also provide your analysis on whether you agree with CFO, CMO and legal expert or not and why? Try to challenge the weak points of CFO,CMO and legal agents """,
                            agent=Devils_Advocate_agent,context=[task_cfo,task_cmo,task_legal,debate_cfo,debate_cmo,debate_legal],
                            expected_output=f"a detailed response of your critical analysis and your recommendation on whether we should do what the {question} wants us to do or not based on your critical analysis perspective and also whether you agree with CFO, CMO and legal expert or not and why?")
debate_crew=Crew(agents=[CFO_agent,CMO_agent,Legal_agent,Devils_Advocate_agent],tasks=[debate_cfo,debate_cmo,debate_legal,debate_devils_advocate],process=Process.sequential,verbose=True)
debate_result=debate_crew.kickoff()
print(debate_result)

human_section=input("As a board member, do you have any specific questions or points you want the agents to address in their rebuttals? If yes, please list them here. If not, just press Enter: ")
debate_cfo_2 = Task(
    description=f"""ROUND 2 — REBUTTAL. You are the CFO.

    You have heard all agents' Round 1 positions. Now:
    1. Respond to at least ONE specific argument from another agent by name
       (e.g. "The Legal counsel raised antitrust risk, but I believe...")
    2. Defend OR update your financial position based on what you heard
    3. If the Devil's Advocate challenged your numbers, address it directly
    {human_section}
    
    Keep under 200 words. Be specific — quote other agents' claims.""",
    agent=CFO_agent,
    context=[debate_cfo, debate_cmo, debate_legal, debate_devils_advocate],
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
    context=[debate_cfo, debate_cmo, debate_legal, debate_devils_advocate, debate_cfo_2],
    expected_output="A rebuttal addressing other agents' specific points with market analysis counter-arguments"
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
    context=[debate_cfo, debate_cmo, debate_legal, debate_devils_advocate, debate_cfo_2, debate_cmo_2],
    expected_output="A rebuttal addressing other agents' specific points with legal counter-arguments"
)

debate_devils_advocate_2 = Task(
    description=f"""ROUND 2 — REBUTTAL. You are the Devil's Advocate.

    You have heard everyone's Round 1 positions AND their Round 2 rebuttals. Now:
    1. Identify who changed their position and whether the change is justified
    2. Find the WEAKEST argument that survived Round 1 unchallenged
    3. Quote specific numbers or claims from other agents and explain why they are wrong
    {human_section}
    
    Keep under 200 words. Be ruthless but fair — attack arguments, not agents.""",
    agent=Devils_Advocate_agent,
    context=[debate_cfo, debate_cmo, debate_legal, debate_devils_advocate, 
             debate_cfo_2, debate_cmo_2, debate_legal_2],
    expected_output="A sharp rebuttal challenging the weakest surviving arguments with specific counter-evidence"
)

debate_crew_2=Crew(agents=[CFO_agent,CMO_agent,Legal_agent,Devils_Advocate_agent],tasks=[debate_cfo_2,debate_cmo_2,debate_legal_2,debate_devils_advocate_2],process=Process.sequential,verbose=True)
debate_result_2=debate_crew_2.kickoff()
print(debate_result_2)

debate_cfo_3=Task(description="""Final Round- Act as a CFO.One paragraph only
                  State:GO/NO-GO/CONDITIONAL.
                  Your single strongest argument for your position. Quote specific numbers.
                  One risk that should be monitored""",agent=CFO_agent,context=[debate_cfo, debate_cmo, debate_legal, debate_devils_advocate, debate_cfo_2, debate_cmo_2, debate_legal_2, debate_devils_advocate_2],
                  expected_output=f"Your final recommendation on whether we should do what the {question} wants us to do or not based on financial perspective.")

debate_cmo_3=Task(description="""Final Round- Act as a CMO.One paragraph only
                  State:GO/NO-GO/CONDITIONAL.
                  Your single strongest argument for your position. Quote specific numbers.
                  One risk that should be monitored""",agent=CMO_agent,context=[debate_cfo, debate_cmo, debate_legal, debate_devils_advocate, debate_cfo_2, debate_cmo_2, debate_legal_2, debate_devils_advocate_2,debate_cfo_3],
                  expected_output=f"Your final recommendation on whether we should do what the {question} wants us to do or not based on marketing perspective.")

debate_legal_3=Task(description="""Final Round- Act as a Legal Expert.One paragraph only
                  State:GO/NO-GO/CONDITIONAL.
                  Your single strongest argument for your position. Quote specific numbers.
                  One risk that should be monitored""",agent=Legal_agent,context=[debate_cfo, debate_cmo, debate_legal, debate_devils_advocate, debate_cfo_2, debate_cmo_2, debate_legal_2, debate_devils_advocate_2,debate_cfo_3,debate_cmo_3],
                  expected_output=f"Your final recommendation on whether we should do what the {question} wants us to do or not based on legal perspective.")

debate_devils_advocate_3=Task(description="""Final Round- Act as a Devils Advocate.One paragraph only
                  State:GO/NO-GO/CONDITIONAL.
                  Your single strongest argument for your position. Quote specific numbers.
                  One risk that should be monitored""",agent=Devils_Advocate_agent,context=[debate_cfo, debate_cmo, debate_legal, debate_devils_advocate, debate_cfo_2, debate_cmo_2, debate_legal_2, debate_devils_advocate_2,debate_cfo_3,debate_cmo_3,debate_legal_3],
                  expected_output=f"Your final recommendation on whether we should do what the {question} wants us to do or not based on Devils Advocate perspective.")

crew_final_debate=Crew(agents=[CFO_agent,CMO_agent,Legal_agent,Devils_Advocate_agent],tasks=[debate_cfo_3,debate_cmo_3,debate_legal_3,debate_devils_advocate_3],process=Process.sequential,verbose=True)
final_debate_result=crew_final_debate.kickoff()
print(final_debate_result)

moderator_agent=Agent(role="act as a mdoerator who has read all the debate points of all four agents and then you have to provide a final analysis and recommnedation to the board pf directors on whether we should do what the {question} wants us to do or not based on your analysis of all the debate points and also provide a final recommendation on whether you agree with CFO, CMO, legal expert and devils advocate or not and why?",goal="provide a final analysis and recommendation to the board of directors on whether we should do what the {question} wants us to do or not based on your analysis of all the debate points and also provide a final recommendation on whether you agree with CFO, CMO, legal expert and devils advocate or not and why?",backstory="""Act as a senior level expert in running in a global level company who has knowledge of legal, marketing and financial aspects who has 20 years of experience in this field""", tools=[serper],llm=gemini,verbose=True)
moderator_task=Task(description="""Act as a moderator and provide your annalysis and final recommendation to the board of directors , donot exceed more than 250 words and be crisp and to the point.""", agent=moderator_agent,context=[debate_cfo,debate_cmo,debate_legal,debate_devils_advocate,debate_cfo_2,debate_cmo_2,debate_legal_2,debate_devils_advocate_2],expected_output=f"a detailed response of your critical analysis and your recommendation on whether we should do what the {question} wants us to do or not based on your critical analysis perspective and also whether you agree with CFO, CMO and legal expert or not and why?")
moderator_crew=Crew(agents=[moderator_agent],tasks=[moderator_task],process=Process.sequential,verbose=True)
result_final=moderator_crew.kickoff()
print(result_final)