import os
import time
import operator
from typing import Annotated, Sequence, TypedDict, List
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

def llm_call_with_retry(llm_instance, messages, max_retries=3):
    """Wrapper that auto-retries LLM calls on rate limit (429) errors."""
    for attempt in range(max_retries):
        try:
            return llm_instance.invoke(messages)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = 60 * (attempt + 1)  # 60s, 120s, 180s
                print(f"   ⏳ Rate limited. Waiting {wait_time}s before retry ({attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Max retries exhausted. Try again in a few minutes.")

# Load environment variables (API keys)
# Use the script's own directory to find the .env file, regardless of where you run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(SCRIPT_DIR, ".env")
load_dotenv(dotenv_path)

# Debug: show what we loaded
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print(f"❌ No API key found! Looked for .env at: {dotenv_path}")
    print("   Make sure your .env file has: GEMINI_API_KEY=AIzaSy...")
    exit(1)
else:
    print(f"🔑 API key loaded (starts with: {api_key[:8]}..., length: {len(api_key)})")

# We use Gemini 1.5 Pro for this POC.
# High temperature for agents (creative debate), low for the router (deterministic).
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.7, google_api_key=api_key)
    router_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.1, google_api_key=api_key)
except Exception as e:
    print(f"Failed to initialize LLM. Error: {e}")
    exit(1)

# ----------------------------------------------------------------------
# 1. PERSONAS (The 62 agents reduced to 4 for the PoC)
# ----------------------------------------------------------------------
AGENT_PROMPTS = {
    "Therapist": "You are a CBT Therapist. Use Cognitive Behavioral Therapy to reframe anxiety. Keep it brief. Prioritize mental peace.",
    "Sleep Optimizer": "You are a Sleep Optimizer. You analyze habits and build sleep protocols. Prioritize 8 hours of sleep over EVERYTHING. Veto advice that ruins sleep. Keep it punchy.",
    "Career Strategist": "You are a Career Strategist. You prioritize professional growth, performing well, and doing whatever it takes to succeed at work. Keep it brief and direct.",
    "Nutritionist": "You are a Nutritionist. You manage dietary planning for focus and energy. You recommend specific diet tweaks to avoid crashes. Keep it actionable."
}

# ----------------------------------------------------------------------
# 2. STATE DEFINITION
# ----------------------------------------------------------------------
class SimState(TypedDict):
    user_query: str
    active_agents: List[str]
    # operator.add ensures that messages appended to history are concatenated, not overwritten
    debate_history: Annotated[List[BaseMessage], operator.add]
    final_plan: str

class RouterOutput(BaseModel):
    selected_agents: List[str] = Field(description="List of agent names to activate. Only select from: Therapist, Sleep Optimizer, Career Strategist, Nutritionist. Pick at least 2.")

# ----------------------------------------------------------------------
# 3. GRAPH NODES
# ----------------------------------------------------------------------
def router_node(state: SimState):
    """The Chief of Staff routes the query to the correct subset of agents."""
    query = state["user_query"]
    prompt = f"User Query: '{query}'\n\nAvailable Agents: {', '.join(AGENT_PROMPTS.keys())}\nSelect the most relevant agents to debate this specific query based on their expertise."
    
    # Use Structured Output to guarantee the LLM returns our Pydantic model
    structured_llm = router_llm.with_structured_output(RouterOutput)
    result = llm_call_with_retry(structured_llm, [HumanMessage(content=prompt)])
    
    selected = [agent for agent in result.selected_agents if agent in AGENT_PROMPTS]
    if not selected:
        selected = ["Career Strategist", "Sleep Optimizer"] # Fallback safely
    
    print(f"👔 Chief of Staff activated: {selected}")
    return {"active_agents": selected}

def debate_node(state: SimState):
    """The Chamber where selected agents give their advice sequentially, building on each other."""
    query = state["user_query"]
    agents = state["active_agents"]
    
    new_messages = []
    
    for agent_name in agents:
        system_prompt = AGENT_PROMPTS[agent_name]
        
        # Construct the context window for the agent
        agent_context = f"User Query: '{query}'\n\n"
        if new_messages:
            agent_context += "What other agents have suggested so far (you may agree, compromise, or heavily debate them):\n"
            for msg in new_messages:
                agent_context += f"- {msg.name}: {msg.content}\n"
        
        agent_context += "\nNow provide your advice. Be in-character."
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=agent_context)
        ]
        
        response = llm_call_with_retry(llm, messages)
        # Store as AIMessage but tagged with the agent's name
        msg_name = agent_name.replace(" ", "_")
        msg = AIMessage(content=response.content, name=msg_name)
        
        new_messages.append(msg)
        print(f"\n🗣️  [{agent_name}]:\n  {response.content}")
        
    return {"debate_history": new_messages}

def synthesizer_node(state: SimState):
    """Synthesizes the messy debate into a beautiful, actionable plan."""
    query = state["user_query"]
    history = state["debate_history"]
    
    debate_str = ""
    for msg in history:
        debate_str += f"{msg.name}: {msg.content}\n\n"
        
    prompt = f"""
You are the Chief Synthesis Officer. The user has a problem, and your expert agents have debated the solution.

User Problem: '{query}'

Agent Debate History:
{debate_str}

Your job is to synthesize their advice into a single, cohesive, frictionless 1-2-3 step actionable list for the user. 
Resolve any conflicting advice (e.g. if Career says stay up, but Sleep says go to bed, find a realistic compromise).
Return ONLY the synthesized markdown plan. Make it punchy and empathetic.
"""
    response = llm_call_with_retry(llm, [HumanMessage(content=prompt)])
    print(f"\n✅ Synthesized Plan Generated.")
    return {"final_plan": response.content}

# ----------------------------------------------------------------------
# 4. BUILD & COMPILE GRAPH
# ----------------------------------------------------------------------
workflow = StateGraph(SimState)

# Add nodes
workflow.add_node("router", router_node)
workflow.add_node("debate", debate_node)
workflow.add_node("synthesizer", synthesizer_node)

# Define exact deterministic flow: Router -> Debate -> Synthesizer -> END
workflow.set_entry_point("router")
workflow.add_edge("router", "debate")
workflow.add_edge("debate", "synthesizer")
workflow.add_edge("synthesizer", END)

app = workflow.compile()

if __name__ == "__main__":
    # Test our Mirofish simulation!
    test_query = "I'm exhausted today, but I have a big presentation tomorrow and I haven't practiced enough."
    
    print("\n" + "="*50)
    print(f"👤 USER PROBLEM: {test_query}")
    print("="*50 + "\n")
    print("🚀 Running Miro-Coach Simulation...\n")
    
    final_state = app.invoke({
        "user_query": test_query, 
        "debate_history": []
    })
    
    print("\n" + "="*50)
    print("📋 FINAL UNIFIED PLAN")
    print("="*50)
    print(final_state["final_plan"])
    print("="*50 + "\n")
