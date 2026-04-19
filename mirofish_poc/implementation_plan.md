# Miro-Coach LangGraph PoC Implementation Plan

This plan details the steps to build a working prototype of the multi-agent life coach debate chamber using Python. 

## Framework Selection: LangGraph
For this architecture, the best framework is **LangGraph** (built by the LangChain team). 

*Why LangGraph and not AutoGen or CrewAI?*
While AutoGen is great for generic multi-agent chats, and CrewAI is excellent for rigid sequential tasks, **LangGraph** gives us complete deterministic control over the flow of information. It allows us to explicitly define our specific architecture: `Router ➡️ Parallel Agent Execution ➡️ Synthesizer`. It also manages the "State" (the Debate History) perfectly.

## Proposed Changes

We will create a foundational script and environment for the user.

### 1. Requirements and Setup
#### [NEW] poc/requirements.txt
We'll define the requirements needed to run the LangGraph application:
```text
langgraph
langchain
langchain-google-genai # Let's use Gemini by default, but it can be swapped for OpenAI
pydantic
python-dotenv
```

#### [NEW] poc/.env.example
An environment file to securely load API keys (`GEMINI_API_KEY` or `OPENAI_API_KEY`).

### 2. The LangGraph Script
#### [NEW] poc/miro_coach_sim.py
We will implement the following flow using LangGraph:

1. **State Definition (`State` Dictionary)**
   - `user_input`: The original query.
   - `active_agents`: A list of strings determining which agents should respond.
   - `debate_history`: A list of messages (the actual simulation).
   - `final_plan`: The synthesized output.
2. **Nodes (The Functions)**
   - **`router_node`**: Uses an LLM to read the user input, looks at our available roster of agents (we'll implement 4 for the PoC: `Career Strategist`, `Sleep Optimizer`, `Therapist`, `Nutritionist`), and returns which ones should speak.
   - **`agent_node`**: A dynamic node. For each active agent in `active_agents`, we'll spawn an LLM call infused with their specific persona prompt from your markdown file. They will read the `user_input` and `debate_history` and add their advice.
   - **`synthesizer_node`**: The Chief of Staff reads the entire `debate_history` and turns it into a bulleted 1-2-3 action plan.
3. **Graph Compilation**
   - We will define the edges so the execution flows exactly as planned, compiling it into an executable app.

### 3. Execution Example
We will include a `if __name__ == "__main__":` block to run the exact scenario we discussed: *"I am exhausted today, but I have a big presentation tomorrow and I haven't practiced enough."*
