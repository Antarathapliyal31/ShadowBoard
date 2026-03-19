<p align="center">
  <img src="https://img.shields.io/badge/Shadow%20Board-AI%20Powered-gold?style=for-the-badge&logo=sparkles" alt="Shadow Board"/>
  <img src="https://img.shields.io/badge/Built%20With-CrewAI-blue?style=for-the-badge" alt="CrewAI"/>
  <img src="https://img.shields.io/badge/LLM-Google%20Gemini-4285F4?style=for-the-badge&logo=google" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Frontend-React%20+%20TypeScript-61DAFB?style=for-the-badge&logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
</p>

<h1 align="center">Shadow Board</h1>
<h3 align="center">AI-Powered Executive Decision Simulation Platform</h3>

<p align="center">
  <i>Simulate a boardroom of AI executives debating your strategic questions in real-time.</i>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=Eq9tkcItfrM">
    <img src="https://img.shields.io/badge/Full%20Demo-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Full Demo"/>
  </a>
  &nbsp;
  <a href="https://youtu.be/t4cJPGrKRw8">
    <img src="https://img.shields.io/badge/Catalogue%20Demo-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Catalogue Demo"/>
  </a>
</p>

---

## Demos

### Full Application Demo

<p align="center">
  <a href="https://www.youtube.com/watch?v=Eq9tkcItfrM">
    <img src="https://img.youtube.com/vi/Eq9tkcItfrM/maxresdefault.jpg" alt="Shadow Board Full Demo" width="700"/>
  </a>
  <br/>
  <em>Click to watch the full Shadow Board application demo on YouTube</em>
</p>

### AIRIA Catalogue Interface Demo

<p align="center">
  <a href="https://youtu.be/t4cJPGrKRw8">
    <img src="https://img.youtube.com/vi/t4cJPGrKRw8/maxresdefault.jpg" alt="AIRIA Catalogue Interface Demo" width="700"/>
  </a>
  <br/>
  <em>Click to watch the AIRIA Catalogue Interface Demo on YouTube</em>
</p>

---

## What is Shadow Board?

**Shadow Board** is an intelligent boardroom simulation platform that assembles a panel of AI executive agents — each with distinct expertise, perspectives, and debate styles — to rigorously analyze your strategic business questions from every angle.

Instead of relying on a single AI response, Shadow Board orchestrates a **multi-agent debate** across research, argumentation, and synthesis phases, producing a comprehensive **Strategy Brief PDF** with actionable recommendations.

### The Problem It Solves

| Traditional Approach | Shadow Board Approach |
|---|---|
| Single-perspective AI answers | Multi-agent debate from 5 expert viewpoints |
| No structured analysis | 3-phase research + debate + synthesis pipeline |
| Static one-shot responses | Real-time streaming with human intervention |
| No institutional memory | Learns from past decisions via Supermemory |
| Generic advice | Domain-specific boards (Tech, Healthcare, Finance, Retail) |

---

## Key Features

- **Multi-Agent Debate Engine** — 5 AI executives (CFO, CMO, Legal Counsel, Devil's Advocate, Moderator) powered by Google Gemini debate your question through 3 structured rounds
- **Human-In-The-Loop (HITL)** — Pause the debate mid-round to challenge agents, ask follow-ups, or redirect the discussion with text or voice input
- **Real-Time Streaming** — Watch the debate unfold live via Server-Sent Events (SSE) with agent-by-agent responses
- **Domain-Specific Boards** — Choose from Tech, Healthcare, Finance, or Retail presets that customize each agent's expertise
- **Strategy Brief PDF** — Auto-generated executive summary with board votes (GO / NO-GO / CONDITIONAL), risk matrix, and recommendations
- **Institutional Memory** — Past debate outcomes are stored and retrieved via Supermemory, so the board references prior decisions
- **Document Upload** — Feed the board PDF, DOCX, or TXT files for data-driven analysis
- **Voice Input** — Speech-to-text via OpenAI Whisper for hands-free human intervention
- **Session History** — Review, compare, and re-run past boardroom sessions
- **Slack Notifications** — Get notified in Slack when a debate completes with vote results
- **AIRIA Chat Widget** — Embedded AI assistant to explain features and answer questions

---

## System Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'fontFamily': 'Segoe UI, Arial', 'primaryTextColor': '#1e293b', 'lineColor': '#475569', 'edgeLabelBackground': '#f8fafc' }}}%%
graph TB
    subgraph Frontend["Frontend · React + TypeScript + Vite"]
        direction LR
        Auth["Auth Screen"]:::feNode
        Landing["Landing Page"]:::feNode
        Debate["Debate View"]:::feNode
        History["Session History"]:::feNode
        Auth --> Landing --> Debate --> History
    end

    subgraph Backend["Backend · FastAPI + Python"]
        direction LR
        AuthRoutes["Auth Routes"]:::beNode
        SessionMgr["Session Manager"]:::beNode
        DebateEngine["Debate Engine"]:::beNode
        PDFGen["PDF Generator"]:::beNode
    end

    subgraph Orchestration["Agent Orchestration · CrewAI"]
        Agents["AI Agent Crew"]:::orchNode
        Memory["Memory Engine"]:::orchNode
    end

    Frontend -->|"HTTP / SSE"| Backend
    DebateEngine --> Agents
    DebateEngine --> Memory

    subgraph External["External Services"]
        Gemini["Google Gemini\n(LLM)"]:::gemNode
        Serper["Serper\n(Web Search)"]:::serpNode
        Supabase["Supabase\n(DB + Auth)"]:::supaNode
        SuperMem["Supermemory\n(Institutional Memory)"]:::smemNode
        Whisper["OpenAI Whisper\n(Speech-to-Text)"]:::whisNode
        Slack["Slack\n(Notifications)"]:::slackNode
    end

    Agents -->|"LLM Calls"| Gemini
    Agents -->|"Research"| Serper
    AuthRoutes --> Supabase
    SessionMgr --> Supabase
    Memory --> SuperMem
    PDFGen -->|"Notify"| Slack
    Frontend -->|"Voice Input"| Whisper

    classDef feNode fill:#dbeafe,stroke:#2563eb,color:#1e3a8a,font-weight:bold,stroke-width:2px
    classDef beNode fill:#dcfce7,stroke:#16a34a,color:#14532d,font-weight:bold,stroke-width:2px
    classDef orchNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold,stroke-width:2px
    classDef gemNode fill:#bfdbfe,stroke:#2563eb,color:#1e3a8a,font-weight:bold,stroke-width:2.5px
    classDef serpNode fill:#bbf7d0,stroke:#16a34a,color:#14532d,font-weight:bold,stroke-width:2.5px
    classDef supaNode fill:#a7f3d0,stroke:#059669,color:#064e3b,font-weight:bold,stroke-width:2.5px
    classDef smemNode fill:#ddd6fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold,stroke-width:2.5px
    classDef whisNode fill:#c7d2fe,stroke:#4f46e5,color:#312e81,font-weight:bold,stroke-width:2.5px
    classDef slackNode fill:#fecaca,stroke:#dc2626,color:#7f1d1d,font-weight:bold,stroke-width:2.5px

    style Frontend fill:#eff6ff,stroke:#2563eb,color:#1e3a8a,font-weight:bold,stroke-width:3px
    style Backend fill:#f0fdf4,stroke:#16a34a,color:#14532d,font-weight:bold,stroke-width:3px
    style Orchestration fill:#fffbeb,stroke:#d97706,color:#78350f,font-weight:bold,stroke-width:3px
    style External fill:#f5f3ff,stroke:#7c3aed,color:#4c1d95,font-weight:bold,stroke-width:3px
```

---

## Agent Architecture — Example

> **Scenario:** *"Should Spotify acquire a podcast analytics company?"*

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '18px', 'fontFamily': 'Segoe UI, Arial', 'primaryTextColor': '#1e293b', 'lineColor': '#475569', 'edgeLabelBackground': '#f8fafc' }}}%%
flowchart LR
    Q(["Should Spotify acquire\na podcast analytics company?"]):::qClass

    Q --> CFO["CFO\n$4.2B cash · $150-400M target\nROI & margin impact"]:::cfoClass
    Q --> CMO["CMO\n30% market share · YouTube threat\nAd revenue growth"]:::cmoClass
    Q --> LEG["Legal\nAntitrust risk · data privacy\nPast acquisition scrutiny"]:::legClass

    CFO --> DA["Devil's Advocate\n$1B spent on podcasts already\nROI questioned since 2022"]:::daClass
    CMO --> DA
    LEG --> DA

    DA --> MOD["Moderator\nSynthesizes all positions\nStrategy Brief PDF"]:::modClass

    MOD --> V{"BOARD VOTE"}:::voteClass
    V -->|"CFO"| GO["GO"]:::goClass
    V -->|"CMO"| COND["CONDITIONAL"]:::condClass
    V -->|"Legal"| NOGO["NO-GO"]:::nogoClass

    classDef qClass fill:#fef3c7,stroke:#b45309,color:#78350f,font-weight:bold,font-size:17px,stroke-width:3px
    classDef cfoClass fill:#dbeafe,stroke:#2563eb,color:#1e3a8a,font-weight:bold,font-size:16px,stroke-width:3px
    classDef cmoClass fill:#dcfce7,stroke:#16a34a,color:#14532d,font-weight:bold,font-size:16px,stroke-width:3px
    classDef legClass fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold,font-size:16px,stroke-width:3px
    classDef daClass fill:#fee2e2,stroke:#dc2626,color:#7f1d1d,font-weight:bold,font-size:16px,stroke-width:3px
    classDef modClass fill:#fef9c3,stroke:#ca8a04,color:#713f12,font-weight:bold,font-size:16px,stroke-width:3px
    classDef voteClass fill:#e0e7ff,stroke:#4f46e5,color:#312e81,font-weight:bold,font-size:17px,stroke-width:3px
    classDef goClass fill:#bbf7d0,stroke:#15803d,color:#14532d,font-weight:bold,font-size:18px,stroke-width:4px
    classDef condClass fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold,font-size:18px,stroke-width:4px
    classDef nogoClass fill:#fecaca,stroke:#dc2626,color:#7f1d1d,font-weight:bold,font-size:18px,stroke-width:4px
```

---

## Debate Flow & Phases

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '16px', 'fontFamily': 'Segoe UI, Arial', 'primaryTextColor': '#1e293b', 'lineColor': '#475569', 'edgeLabelBackground': '#f8fafc' }}}%%
flowchart TD
    Start(["User Submits Question"]):::startClass
    Start --> Upload["Upload Documents\n(PDF / DOCX / TXT)"]:::inputClass
    Upload --> Board["Select Board Type\n(Tech / Healthcare / Finance / Retail)"]:::inputClass

    Board --> P1

    subgraph P1["PHASE 1 · RESEARCH"]
        direction LR
        R1["CFO Research\n(Web Search)"]:::researchNode
        R2["CMO Research\n(Web Search)"]:::researchNode
        R3["Legal Research\n(Web Search)"]:::researchNode
    end

    P1 --> P2R1

    subgraph P2R1["PHASE 2 · ROUND 1 · OPENING STATEMENTS"]
        direction LR
        S1["CFO\nPosition"]:::debateNode
        S2["CMO\nPosition"]:::debateNode
        S3["Legal\nPosition"]:::debateNode
        S4["Devil's Advocate\nChallenges"]:::challengeNode
    end

    P2R1 --> HITL

    subgraph HITL["HUMAN-IN-THE-LOOP PAUSE"]
        direction TB
        H1["Challenge a specific agent"]:::hitlNode
        H2["Ask follow-up questions"]:::hitlNode
        H3["Provide additional context"]:::hitlNode
        H4["Voice input via Whisper"]:::hitlNode
        H5["Skip to continue"]:::hitlNode
    end

    HITL --> P2R2

    subgraph P2R2["PHASE 2 · ROUND 2 · REBUTTALS"]
        direction LR
        RB1["CFO\nRebuttal"]:::rebuttalNode
        RB2["CMO\nRebuttal"]:::rebuttalNode
        RB3["Legal\nRebuttal"]:::rebuttalNode
        RB4["Devil's Advocate\nRebuttal"]:::challengeNode
    end

    P2R2 --> P2R3

    subgraph P2R3["PHASE 2 · ROUND 3 · FINAL POSITIONS"]
        direction LR
        F1["CFO\nFinal Vote"]:::finalNode
        F2["CMO\nFinal Vote"]:::finalNode
        F3["Legal\nFinal Vote"]:::finalNode
        F4["Devil's Advocate\nFinal Position"]:::challengeNode
    end

    P2R3 --> P3

    subgraph P3["PHASE 3 · MODERATOR SYNTHESIS"]
        Mod["Reviews all 3 rounds\nWeighs positions & evidence\nGenerates executive recommendation"]:::modNode
    end

    P3 --> Output

    subgraph Output["OUTPUTS"]
        direction LR
        PDF["PDF Strategy\nBrief"]:::pdfNode
        DB["Supabase\nSession Saved"]:::dbNode
        SL["Slack\nNotification"]:::slkNode
        MEM["Supermemory\nStored"]:::memNode
    end

    classDef startClass fill:#fef3c7,stroke:#b45309,color:#78350f,font-weight:bold,font-size:17px,stroke-width:3px
    classDef inputClass fill:#f1f5f9,stroke:#475569,color:#1e293b,font-weight:bold,stroke-width:2px
    classDef researchNode fill:#dbeafe,stroke:#2563eb,color:#1e3a8a,font-weight:bold,stroke-width:2px
    classDef debateNode fill:#dcfce7,stroke:#16a34a,color:#14532d,font-weight:bold,stroke-width:2px
    classDef challengeNode fill:#fee2e2,stroke:#dc2626,color:#7f1d1d,font-weight:bold,stroke-width:2px
    classDef hitlNode fill:#fce7f3,stroke:#db2777,color:#831843,font-weight:bold,stroke-width:2px
    classDef rebuttalNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold,stroke-width:2px
    classDef finalNode fill:#fee2e2,stroke:#dc2626,color:#7f1d1d,font-weight:bold,stroke-width:2px
    classDef modNode fill:#fef9c3,stroke:#ca8a04,color:#713f12,font-weight:bold,stroke-width:3px
    classDef pdfNode fill:#dbeafe,stroke:#2563eb,color:#1e3a8a,font-weight:bold,stroke-width:2.5px
    classDef dbNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold,stroke-width:2.5px
    classDef slkNode fill:#fecaca,stroke:#dc2626,color:#7f1d1d,font-weight:bold,stroke-width:2.5px
    classDef memNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold,stroke-width:2.5px

    style P1 fill:#eff6ff,stroke:#2563eb,color:#1e3a8a,font-weight:bold,stroke-width:3px
    style P2R1 fill:#f0fdf4,stroke:#16a34a,color:#14532d,font-weight:bold,stroke-width:3px
    style HITL fill:#fdf2f8,stroke:#db2777,color:#831843,font-weight:bold,stroke-width:3px
    style P2R2 fill:#fffbeb,stroke:#d97706,color:#78350f,font-weight:bold,stroke-width:3px
    style P2R3 fill:#fef2f2,stroke:#dc2626,color:#7f1d1d,font-weight:bold,stroke-width:3px
    style P3 fill:#fefce8,stroke:#ca8a04,color:#713f12,font-weight:bold,stroke-width:3px
    style Output fill:#f0fdf4,stroke:#16a34a,color:#14532d,font-weight:bold,stroke-width:3px
```

---

## Data Flow Diagram

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'fontSize': '18px', 'fontFamily': 'Segoe UI, Arial', 'primaryTextColor': '#1e293b', 'lineColor': '#475569', 'edgeLabelBackground': '#f8fafc' }}}%%
flowchart TD
    User(["USER BROWSER"]):::userClass

    User -->|"Login / Signup"| AuthAPI["AUTH API"]:::apiClass
    User -->|"Submit Question"| SessionAPI["SESSION API"]:::apiClass
    User -->|"Upload Documents"| UploadAPI["UPLOAD API"]:::apiClass
    User -->|"Voice Input"| SpeechAPI["SPEECH-TO-TEXT"]:::apiClass

    AuthAPI --> SupaDB[("SUPABASE\nPOSTGRESQL")]:::supaClass
    SessionAPI --> Store["SESSION STORE"]:::storeClass

    Store --> Valid{"INPUT VALIDATION\n& INJECTION CHECK"}:::validateClass

    Valid -->|"PASS"| MemCheck["RETRIEVE PAST\nDECISIONS"]:::memClass
    Valid -->|"FAIL"| Denied["REJECTED"]:::rejectClass

    MemCheck -->|"Query"| SMem[("SUPERMEMORY")]:::smemClass
    SMem -->|"Past Decisions"| MemCheck

    MemCheck --> Stream["SSE STREAM\nENDPOINT"]:::streamClass
    Stream --> Crew["CREWAI AGENT\nEXECUTION"]:::crewClass

    Crew -->|"LLM Calls"| Gem["GOOGLE GEMINI\n2.5 FLASH"]:::gemClass
    Gem -->|"Response"| Crew
    Crew -->|"Web Search"| Srp["SERPER\nSEARCH"]:::srpClass
    Srp -->|"Results"| Crew

    Crew -->|"Real-time Messages"| FE["FRONTEND\nLIVE DEBATE UI"]:::feClass

    Crew --> Post["POST-DEBATE\nPIPELINE"]:::postClass

    Post --> Votes["PARSE VOTES\nGO / NO-GO / CONDITIONAL"]:::outClass
    Post --> GenPDF["GENERATE PDF\nSTRATEGY BRIEF"]:::outPdfClass
    Post --> SaveDB["SAVE TO\nSUPABASE"]:::outSupaClass
    Post --> SaveMem["SAVE TO\nSUPERMEMORY"]:::outMemClass
    Post --> NotifySlk["NOTIFY VIA\nSLACK"]:::outSlackClass

    SpeechAPI --> OAI["OPENAI\nWHISPER"]:::oaiClass
    OAI -->|"Transcription"| FE

    SaveDB --> SupaDB
    SaveMem --> SMem
    NotifySlk --> SlkHook["SLACK\nWEBHOOK"]:::slackClass

    FE -->|"Human Feedback"| HInput["HUMAN-IN-THE-LOOP\nAPI"]:::humanClass
    HInput --> Store

    classDef userClass fill:#fef3c7,stroke:#b45309,color:#78350f,font-weight:bold,font-size:18px,stroke-width:3px
    classDef apiClass fill:#dbeafe,stroke:#2563eb,color:#1e3a8a,font-weight:bold,font-size:16px,stroke-width:2.5px
    classDef supaClass fill:#a7f3d0,stroke:#059669,color:#064e3b,font-weight:bold,font-size:16px,stroke-width:3px
    classDef storeClass fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e,font-weight:bold,font-size:16px,stroke-width:2.5px
    classDef validateClass fill:#fef9c3,stroke:#ca8a04,color:#713f12,font-weight:bold,font-size:16px,stroke-width:3px
    classDef memClass fill:#e0e7ff,stroke:#4f46e5,color:#312e81,font-weight:bold,font-size:16px,stroke-width:2.5px
    classDef rejectClass fill:#fecaca,stroke:#dc2626,color:#7f1d1d,font-weight:bold,font-size:16px,stroke-width:3px
    classDef smemClass fill:#ddd6fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold,font-size:16px,stroke-width:3px
    classDef streamClass fill:#c7d2fe,stroke:#4f46e5,color:#312e81,font-weight:bold,font-size:16px,stroke-width:2.5px
    classDef crewClass fill:#fef3c7,stroke:#b45309,color:#78350f,font-weight:bold,font-size:18px,stroke-width:3px
    classDef gemClass fill:#bfdbfe,stroke:#2563eb,color:#1e3a8a,font-weight:bold,font-size:16px,stroke-width:3px
    classDef srpClass fill:#bbf7d0,stroke:#16a34a,color:#14532d,font-weight:bold,font-size:16px,stroke-width:3px
    classDef feClass fill:#fef3c7,stroke:#b45309,color:#78350f,font-weight:bold,font-size:18px,stroke-width:3px
    classDef postClass fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold,font-size:16px,stroke-width:3px
    classDef outClass fill:#dcfce7,stroke:#16a34a,color:#14532d,font-weight:bold,font-size:15px,stroke-width:2.5px
    classDef outPdfClass fill:#dbeafe,stroke:#2563eb,color:#1e3a8a,font-weight:bold,font-size:15px,stroke-width:2.5px
    classDef outSupaClass fill:#a7f3d0,stroke:#059669,color:#064e3b,font-weight:bold,font-size:15px,stroke-width:2.5px
    classDef outMemClass fill:#ddd6fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold,font-size:15px,stroke-width:2.5px
    classDef outSlackClass fill:#fecaca,stroke:#dc2626,color:#7f1d1d,font-weight:bold,font-size:15px,stroke-width:2.5px
    classDef oaiClass fill:#c7d2fe,stroke:#4f46e5,color:#312e81,font-weight:bold,font-size:16px,stroke-width:3px
    classDef slackClass fill:#fecaca,stroke:#dc2626,color:#7f1d1d,font-weight:bold,font-size:16px,stroke-width:3px
    classDef humanClass fill:#fce7f3,stroke:#db2777,color:#831843,font-weight:bold,font-size:16px,stroke-width:3px
```

---

## Tech Stack

### Frontend

| Technology | Purpose |
|---|---|
| **React 18** | UI framework |
| **TypeScript** | Type safety |
| **Vite** | Build tool & dev server |
| **Tailwind CSS** | Utility-first styling |
| **shadcn/ui** | Component library (45+ components) |
| **Framer Motion** | Animations & transitions |
| **React Router** | Client-side routing |
| **TanStack Query** | Server state management |
| **React Hook Form + Zod** | Form validation |
| **React Markdown** | Render agent responses |
| **Recharts** | Data visualization |
| **Lucide Icons** | Icon system |

### Backend

| Technology | Purpose |
|---|---|
| **FastAPI** | High-performance async API framework |
| **CrewAI** | Multi-agent orchestration framework |
| **Google Gemini 2.5 Flash** | LLM powering all agents |
| **SerperDev** | Real-time web search for research phase |
| **Supabase** | PostgreSQL database + authentication |
| **Supermemory** | Institutional memory for past decisions |
| **OpenAI Whisper** | Speech-to-text for voice input |
| **fpdf2** | PDF strategy brief generation |
| **PyMuPDF + python-docx** | Document parsing (PDF, DOCX) |
| **Uvicorn** | ASGI server |

### Infrastructure

| Technology | Purpose |
|---|---|
| **Render** | Cloud deployment |
| **Supabase** | Managed PostgreSQL + Auth |
| **Slack Webhooks** | Completion notifications |
| **AIRIA Platform** | Optional chat widget integration |

---

## Project Structure

```
airia-ai/
├── frontend/                      # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/
│   │   │   └── Index.tsx          # Main app (auth, landing, debate UI)
│   │   ├── components/
│   │   │   ├── MessageCard.tsx    # Agent message renderer
│   │   │   ├── HumanInputPanel.tsx# HITL input interface
│   │   │   ├── PhaseIndicator.tsx # 6-phase progress bar
│   │   │   ├── TypingIndicator.tsx# Loading animation
│   │   │   ├── AiriaChatWidget.tsx# Embedded AI chat assistant
│   │   │   └── ui/               # 45+ shadcn/ui components
│   │   ├── hooks/
│   │   │   └── useSpeechRecognition.ts  # Whisper voice input
│   │   └── lib/                   # Utilities
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
├── server.py                      # FastAPI main server
├── agents_creation.py             # CrewAI agent definitions & tasks
├── database.py                    # Supabase auth & session storage
├── memory.py                      # Supermemory integration
├── pdf_generator.py               # Strategy brief PDF generation
├── slack_notify.py                # Slack webhook notifications
├── airia_client.py                # AIRIA platform integration
├── requirements.txt               # Python dependencies
├── render.yaml                    # Render deployment config
└── reports/                       # Generated PDF strategy briefs
```

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **npm** or **yarn**

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/airia-ai.git
cd airia-ai
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Environment Variables

Create a `.env` file in the root directory:

```env
# Required - Core APIs
GEMINI_API_KEY=your_google_gemini_api_key
SERPER_API_KEY=your_serper_api_key

# Required - Database & Auth
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Required - Institutional Memory
SUPERMEMORY_API_KEY=your_supermemory_api_key

# Optional - Voice Input
OPENAI_API_KEY=your_openai_api_key

# Optional - Notifications
SLACK_WEBHOOK_URL=your_slack_webhook_url

# Optional - AIRIA Chat Widget
AIRIA_PIPELINE_ID=your_pipeline_id
AIRIA_WIDGET_API_KEY=your_widget_api_key
AIRIA_API_KEY=your_airia_api_key
```

### 5. Run the Application

**Start the backend:**

```bash
uvicorn server:app --reload --port 8000
```

**Start the frontend (in a new terminal):**

```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:8080` (frontend) and `http://localhost:8000` (API).

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/signup` | Register a new user |
| `POST` | `/api/auth/login` | Authenticate user |
| `POST` | `/api/session/create` | Create a new debate session |
| `POST` | `/api/{session_id}/upload` | Upload document (PDF/DOCX/TXT) |
| `GET` | `/api/{session_id}/agents_research` | Start debate (SSE stream) |
| `POST` | `/api/{session_id}/human_input` | Submit HITL feedback |
| `GET` | `/api/{session_id}/download_pdf` | Download strategy brief PDF |
| `GET` | `/api/sessions/history/{user_id}` | Get user's session history |
| `POST` | `/api/speech-to-text` | Transcribe audio via Whisper |
| `POST` | `/api/chat` | AIRIA chat widget proxy |

---

## How It Works

1. **Authenticate** — Sign up or log in via Supabase
2. **Ask a Question** — Enter a strategic business question (e.g., *"Should we expand into the European market?"*)
3. **Select Board Type** — Choose from Tech, Healthcare, Finance, or Retail to customize agent expertise
4. **Upload Context** *(optional)* — Attach relevant documents for data-driven analysis
5. **Watch the Debate** — AI agents research, take positions, and debate in real-time
6. **Intervene** — During the HITL pause, challenge agents or provide additional context
7. **Receive Strategy Brief** — Download a PDF with executive summary, board votes, and recommendations

---

## Deployment

The project is configured for deployment on **Render** via `render.yaml`:

```bash
# Deploy to Render
# Push to your GitHub repo, connect to Render, and it auto-deploys

# Manual deployment
uvicorn server:app --host 0.0.0.0 --port $PORT
```

---

## Security

- **Input Validation** — Question length limits and prompt injection detection
- **Authentication** — Supabase Auth with email/password
- **API Key Protection** — All sensitive keys stored as environment variables
- **CORS** — Configurable cross-origin resource sharing
- **Session Isolation** — Each debate session is scoped to authenticated users

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is proprietary. All rights reserved.

---

<p align="center">
  <b>Built with CrewAI + Google Gemini + React</b>
  <br/>
  <sub>Powered by AIRIA</sub>
</p>
