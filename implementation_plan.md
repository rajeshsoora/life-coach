# 🌳 Zenith Platform — Implementation Plan v4

## The Core Concept: Life Maxing
Zenith is a "Life RPG" where users try to maximize their potential across **5 Core Pillars**: 
🧠 MIND | 💪 BODY | 💰 WEALTH | 🫂 TRIBE | 🌱 GROWTH

---

## 🗺️ The Infinite Rolling Roadmap

Life doesn't end in 30 days. The roadmap shouldn't either. Instead of a fixed 30-day plan, Zenith uses an **Infinite Rolling Roadmap**.

### How it works:
- **The Horizon (Goals):** High-level objectives (e.g., "Run a 10K", "Save $5,000", "Improve sleep"). These stay on the horizon until achieved.
- **The Sprints (14-Day Cycles):** Every two weeks, the Orchestrator works with the user to pick 3-5 specific habits or tasks from the Horizon to focus on. 
- **The Daily Grind:** The active agents generate the daily to-dos required for the current Sprint.

At the end of every 14-day Sprint, there is a **Retrospective**. The user evaluates what worked, what failed, and the Orchestrator adjusts the next Sprint. This creates a continuous loop of improvement that never ends.

---

## 🏛️ The Agent Council (The "Voice of Zenith" UX)

Based on recent decisions, **all 62 agents are available to all users**, but the user *does not* talk to them individually like a chat room. 

Instead, the user interacts with a single, unified entity: **Zenith**. 

**The Paradigm:**
- The user talks to the overarching "Zenith" interface.
- Under the hood, the Orchestrator analyzes the message, identifies the required expertise, and silently pings the relevant specialized agents.
- The UI shows a subtle, premium status indicator while processing: *“Consulting CBT Therapist, Habit Coach, and Sleep Optimizer...”*
- Zenith synthesizes their expert inputs and delivers **one holistic response**.

This prevents the app from feeling like a chaotic group chat with 60 bots. It feels like you are talking to a singular, god-tier AI that has immediate access to a board of specialists.

**Technical execution:** 
- The Orchestrator holds all 62 skill cards. 
- It routes the context to 1-3 relevant agents in parallel.
- A final Synthesis pass merges their advice into a single, cohesive "Voice of Zenith" response.

---

## 💎 The Freemium Model (Energy-Based)

To let users experience the full power of the platform while managing API costs, Zenith will use an **Energy/Request-based** freemium model.

### The "Zenith Energy" System
- **Free Tier:** Users get a daily allowance of "Energy" (e.g., 20 messages/interactions per day).
- **Why this works:**
  - They get to experience the *entire* 62-agent Council.
  - They see the Orchestrator magically swapping agents.
  - They hit the paywall exactly when they are most engaged (mid-conversation or when dealing with a complex issue).
  - High daily usage limits reset every night, encouraging daily return habits.
- **Premium Tier:** Unlimited Energy (messages), advanced analytics, priority model routing (e.g., Claude Opus instead of Gemini Flash).

---

## 🏗️ Proposed Architecture

### Tech Stack
| Layer | Technology |
|:---|:---|
| **Frontend** | Next.js (React) |
| **Styling** | Vanilla CSS + CSS Variables (Dark, premium, glassmorphism) |
| **Auth & DB** | Supabase (PostgreSQL) |
| **AI** | Google Gemini API (Flash for MVP to keep costs low) |
| **Hosting** | Vercel |

### Application Structure
```
zenith/
├── agents/                        
│   ├── skills/                    # All 62 agent JSON skill cards
│   ├── orchestrator.js            # Routes messages and manages the Council
│   └── agentRunner.js             # Executes individual agent prompts
├── app/                           
│   ├── (auth)/                    
│   ├── (dashboard)/               
│   │   ├── pentagon/              # The 5 Pillar assessment visual
│   │   ├── roadmap/               # The Infinite Rolling Roadmap
│   │   ├── council/               # Main chat interface
│   │   └── tree/                  # Visual progress
│   └── api/                       
└── components/                    
```

---

## 🚀 MVP Scope (Phase 1)

### What's IN the MVP
1. **Auth & Setup:** Supabase auth.
2. **The Assessment & Pentagon:** Initial 5-pillar grading and visualization.
3. **The Council Chat:** The core interface where the Orchestrator routes messages to the relevant agents based on the skill cards.
4. **Energy System (Basic logic):** Capping daily messages.

### What's NOT in the MVP (Phase 2+)
- Stripe/Payment integration (we just show "Out of energy - upgrade coming soon").
- The complex 14-day Sprint retrospect logic (start with basic daily to-dos first).
- Complex SVG/Canvas Growth Tree (start with a simpler visual or focus on the Pentagon first).

---

## Next Steps
We are almost ready to start coding. The remaining steps are setting up the Next.js scaffold and writing the first few Agent Skill Cards.
