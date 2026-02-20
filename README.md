# Morphic UI — Agent-Driven Generative Interfaces

> Describe any interface. Claude reasons about your intent and assembles a live, interactive UI from nothing.

## What This Is

A hackathon project for the **AI Tinkerers "AI Interfaces" Hackathon** (Feb 21, 2026).

The core idea: instead of Claude *describing* a UI in text, Claude *is* the UI. You type a sentence, and a fully interactive form, dashboard, or card materializes on screen — built by the agent at runtime using the A2UI declarative JSON protocol.

```
User types → A2A JSON-RPC → Claude (Anthropic) → A2UI JSON → Live UI on screen
```

## Architecture

```
┌─────────────────────────────────────┐
│  Next.js Frontend (port 3000)       │
│  Blank canvas + prompt input        │
│  Calls /api/generate                │
│  Renders A2UI web components        │
└──────────────┬──────────────────────┘
               │ POST { prompt }
               ▼
┌─────────────────────────────────────┐
│  /api/generate  (Next.js API Route) │
│  Clean proxy — JSON-RPC message/send│
└──────────────┬──────────────────────┘
               │ JSON-RPC 2.0
               ▼
┌─────────────────────────────────────┐
│  Python A2A Agent (port 10002)      │
│  Google ADK + LiteLLM               │
│  Calls Anthropic Claude             │
│  Returns A2UI declarative JSON      │
└─────────────────────────────────────┘
```

## Stack

- **Frontend**: Next.js 16 + React 19 + `@a2ui/lit` web components
- **API**: Next.js route as clean JSON-RPC proxy
- **Agent**: Python, Google ADK, LiteLLM → Anthropic Claude
- **Protocol**: A2A (Agent-to-Agent JSON-RPC) + A2UI extension

## Setup

### 1. Python A2A Agent

```bash
cd a2a-agent
pip install -e .

# Create .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Run agent on port 10002
python -m agent
```

### 2. Next.js Frontend

```bash
# From project root
npm install

# Create .env.local
echo "A2A_AGENT_URL=http://localhost:10002" > .env.local

# Run dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Usage

Type anything into the prompt field:

- `"Build a contact form with name, email, and message"`
- `"Create a dashboard with 3 KPI stat cards"`
- `"Make a profile card for Sarah Chen, Lead Designer"`
- `"Generate a todo list for launching a product"`
- `"Design a booking confirmation for a flight to Tokyo"`

The canvas starts blank. Claude generates the UI. The screen morphs.

After generation, use the **Refine** bar at the bottom to iterate:
- `"Add a phone number field"`
- `"Make it feel more playful"`
- `"Add a submit button that shows a confirmation"`

## Why Claude Specifically

The A2UI JSON schema is complex — nested component trees, data model bindings, action contexts. Claude's instruction-following and structured output capabilities are what make this reliable. The agent validates every response against the schema and retries with error feedback when needed.

A weaker model produces invalid JSON. Claude produces valid, creative, well-structured interfaces.

## Environment Variables

See `.env.example` for all required variables.
