# Claude Canvas — Agent-Driven Generative Interfaces


**Describe any interface. Claude reasons about your intent and assembles a live, interactive UI from nothing.**

Instead of Claude *describing* a UI in text, Claude ***is*** the UI. You type a sentence, and a fully interactive form, dashboard, card, or list materializes on screen — built by the agent at runtime using the A2UI declarative JSON protocol over A2A (Agent-to-Agent) JSON-RPC. Every refinement is saved as a versioned snapshot you can revisit, preview live, and branch from.

---

## ✨ What It Does

1. **Type any prompt** — e.g. *"Build a contact form with name, email, and message"*
2. **Claude generates a live UI** — not a description, not a screenshot — a fully interactive A2UI surface rendered directly in the browser via Lit web components
3. **Refine iteratively** — *"Add a phone field"*, *"Make it more playful"*, *"Switch to dark mode"* — Claude remembers everything it built
4. **Every version is saved** — a horizontal version timeline lets you click back to any previous UI snapshot, preview it live in a modal, and restore it to continue refining from that exact point
5. **Form submissions are handled** — Claude-generated buttons fire real actions back to the agent

---

## 🎥 Demo Prompts

Try these to see the full range of what Claude can build:

| Prompt | What you'll see |
|---|---|
| `Build a contact form with name, email, and message` | Multi-field form with submit action |
| `Create a dashboard with 3 KPI stat cards` | Card layout with stats |
| `Make a team member profile card for Sarah Chen, Lead Designer` | Profile card with contact info |
| `Generate a todo list for launching a product` | Icon-decorated vertical list |
| `Design a booking confirmation for a flight to Tokyo` | Confirmation card with details |
| `Create a feedback survey with star ratings` | Survey form |
| `Build a settings panel with toggles and dropdowns` | Settings layout |
| `Make a job application form` | Multi-section form |

**Then refine the result:**
- `Add a phone number field`
- `Make the submit button more prominent`
- `Add a company name section`
- `Make it feel more playful`

---

## 🏗️ Architecture

```
User types prompt
       │
       ▼
┌──────────────────────────────────────────┐
│  Next.js 15 Frontend  (localhost:3000)   │
│                                          │
│  • Blank canvas + prompt textarea        │
│  • Version timeline strip                │
│  • Version preview modal                 │
│  • Refine bar                            │
│  • A2UIRenderer (Lit web components)     │
│                                          │
│  Calls → /api/generate (Next.js route)   │
└──────────────────┬───────────────────────┘
                   │ POST { prompt, history }
                   ▼
┌──────────────────────────────────────────┐
│  /api/generate  (Next.js API Route)      │
│                                          │
│  • Wraps prompt + conversation history   │
│    into A2A JSON-RPC 2.0 payload         │
│  • Attaches A2UI extension URI           │
│  • Passes history via message metadata   │
│  • Parses A2UI JSON from response parts  │
└──────────────────┬───────────────────────┘
                   │ JSON-RPC 2.0 POST
                   ▼
┌──────────────────────────────────────────┐
│  Python A2A Agent  (localhost:10002)     │
│                                          │
│  • UIGeneratorExecutor (AgentExecutor)   │
│  • Reads conversation history from       │
│    message metadata                      │
│  • Calls Anthropic Claude                │
│  • Validates response vs A2UI schema     │
│  • Auto-retries with error feedback      │
│  • Returns A2UI JSON as DataPart(s)      │
└──────────────────┬───────────────────────┘
                   │ A2UI JSON messages
                   ▼
┌──────────────────────────────────────────┐
│  @a2ui/lit Web Components (browser)      │
│                                          │
│  • A2uiMessageProcessor parses messages  │
│  • a2ui-surface Custom Element renders   │
│  • Live interactive UI in the DOM        │
└──────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend framework | Next.js | 15.3.0 |
| UI library | React | 19.2.3 |
| UI rendering | `@a2ui/lit` (Lit web components) | ^0.8.1 |
| Agent protocol | A2A JSON-RPC 2.0 (`a2a-sdk`) | ≥0.3.0 |
| UI protocol | A2UI declarative JSON | v0.8 |
| LLM | Anthropic Claude `claude-sonnet-4-5` | via `anthropic` SDK ≥0.40.0 |
| Agent runtime | Python | 3.11+ |
| Schema validation | `jsonschema` | ≥4.0.0 |
| HTTP server | `uvicorn` + `starlette` | ≥0.23.0 |
| Package manager (Python) | `uv` | recommended |
| Styling | Custom CSS variables, Syne + DM Mono (Google Fonts) | — |
| TypeScript | TypeScript | ^5 |

---

## 📁 Project Structure

```
claude-hackathon-a2ui-demo/
│
├── src/app/
│   ├── page.tsx                        # Main UI page
│   │                                   #   - Idle/thinking/rendered/error states
│   │                                   #   - A2UIRenderer (Lit web component mount)
│   │                                   #   - VersionTimeline (horizontal pill strip)
│   │                                   #   - VersionPreviewModal (live snapshot preview)
│   │                                   #   - Refine bar with conversation history
│   ├── layout.tsx                      # Root layout, Google Fonts, Material Symbols
│   ├── globals.css                     # Global CSS reset
│   ├── a2ui-theme.css                  # A2UI Lit component theme overrides
│   ├── theme.ts                        # Theme constants
│   │
│   ├── api/generate/route.ts           # Next.js API route
│   │                                   #   - Builds A2A JSON-RPC 2.0 payload
│   │                                   #   - Attaches A2UI extension URI
│   │                                   #   - Passes history via message metadata
│   │                                   #   - Parses A2UI parts from RPC response
│   │                                   #   - Handles ECONNREFUSED + timeout errors
│   │
│   ├── components/
│   │   ├── PromptPill.tsx              # Clickable example prompt chip
│   │   └── protocol-cards/
│   │       └── A2UICard.tsx            # A2UI protocol info card with prompt pills
│   │
│   └── hooks/
│       └── useSendMessage.ts           # Hook for programmatic message sending
│
├── src/hooks/
│   └── use-media-query.ts              # Responsive breakpoint hook
│
├── a2a-agent/
│   └── agent/
│       ├── agent.py                    # Core LLM agent
│       │                               #   - SYSTEM_PROMPT with A2UI format rules
│       │                               #   - Claude API calls via anthropic SDK
│       │                               #   - JSON extraction & schema validation
│       │                               #   - Auto-retry with targeted error feedback
│       │                               #   - Conversation history injection
│       │
│       ├── agent_executor.py           # A2A AgentExecutor implementation
│       │                               #   - Reads history from message metadata
│       │                               #   - Handles form submit actions (userAction)
│       │                               #   - Splits text + A2UI JSON into typed Parts
│       │                               #   - Streams TaskState updates
│       │
│       ├── prompt_builder.py           # System prompt building blocks
│       │                               #   - A2UI_SCHEMA (full JSON schema)
│       │                               #   - UI_EXAMPLES (form, list, card, confirm)
│       │                               #   - get_ui_prompt(), get_text_prompt()
│       │
│       ├── a2ui_extension.py           # A2UI extension for A2A protocol
│       │                               #   - A2UI_EXTENSION_URI constant
│       │                               #   - create_a2ui_part() helper
│       │                               #   - try_activate_a2ui_extension()
│       │                               #   - get_a2ui_agent_extension()
│       │
│       ├── tools.py                    # Agent tool definitions
│       ├── __init__.py                 # Package init
│       └── __main__.py                 # Entry point — uvicorn on port 10002
│                                       #   - AgentCard with name, description, skills
│                                       #   - CORS middleware
│                                       #   - A2UI extension in agent capabilities
│
├── package.json                        # Node dependencies
├── next.config.ts                      # Next.js config
├── tsconfig.json                       # TypeScript config
├── a2a-agent/pyproject.toml            # Python dependencies (hatchling build)
├── a2a-agent/uv.lock                   # Locked Python dependency versions
├── a2a-agent/railway.toml              # Railway deployment config
└── a2a-agent/Dockerfile                # Docker build for the Python agent
```

---

## ⚙️ How It Works — Deep Dive

### The A2UI Protocol

Every UI Claude generates is expressed as an array of exactly 3 JSON messages:

```json
[
  {
    "beginRendering": {
      "surfaceId": "form-surface",
      "root": "root-column",
      "styles": { "primaryColor": "#6d28d9", "font": "Plus Jakarta Sans" }
    }
  },
  {
    "surfaceUpdate": {
      "surfaceId": "form-surface",
      "components": [
        { "id": "root-column", "component": { "Column": { "children": { "explicitList": ["title", "name-field", "submit-btn"] } } } },
        { "id": "title", "component": { "Text": { "usageHint": "h2", "text": { "literalString": "Contact Us" } } } },
        { "id": "name-field", "component": { "TextField": { "label": { "literalString": "Name" }, "text": { "path": "name" }, "textFieldType": "shortText" } } },
        { "id": "submit-btn", "component": { "Button": { "child": "submit-text", "primary": true, "action": { "name": "submit_form", "context": [{ "key": "name", "value": { "path": "name" } }] } } } },
        { "id": "submit-text", "component": { "Text": { "text": { "literalString": "Submit" } } } }
      ]
    }
  },
  {
    "dataModelUpdate": {
      "surfaceId": "form-surface",
      "path": "/",
      "contents": [{ "key": "name", "valueString": "" }]
    }
  }
]
```

- **`beginRendering`** — initializes a named surface with a root component ID and visual styles
- **`surfaceUpdate`** — declares all components as a flat map of ID → component definitions; containers reference children by string ID
- **`dataModelUpdate`** — seeds the reactive data model that components bind to via `{ "path": "field_name" }`

The `@a2ui/lit` library hydrates these messages into live Custom Elements via `A2uiMessageProcessor` and the `<a2ui-surface>` element.

### A2A Protocol Integration

The frontend communicates with the Python agent using **A2A JSON-RPC 2.0**. Every request is a `message/send` call with the A2UI extension URI attached. Conversation history is passed in `message.metadata.conversationHistory` so Claude receives the full prior exchange on every refinement call. The agent responds with typed `Part` objects — `TextPart` for the human-readable description and `DataPart` with `mimeType: application/json+a2ui` for each A2UI message.

### Why Claude Specifically

The A2UI JSON schema is deeply nested — components reference each other by string ID, data bindings use path expressions, the entire tree must be self-consistent, and `surfaceId` must stay constant across all 3 messages. Claude's instruction-following capabilities make this reliable where other models fail. The agent validates every response with Python's `jsonschema` and auto-retries with targeted error messages on failure. Conversation history enables Claude to make surgical refinements — changing one field without rebuilding the entire surface.

### Version Timeline

Every generation is saved as a `UIVersion` snapshot with its full A2UI JSON and conversation history. The horizontal timeline appears after the 2nd version. Clicking a past pill opens a live-rendered preview modal. **Restore & Continue** branches the session from that version's exact state so Claude can refine coherently from any past point.

---

## 🚀 Setup & Running Locally

### Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- **`uv`** (recommended) — install from [docs.astral.sh/uv](https://docs.astral.sh/uv)
- An **Anthropic API key** from [console.anthropic.com](https://console.anthropic.com)

---

### Step 1 — Python A2A Agent

```bash
cd a2a-agent

# Create and activate virtual environment
uv venv
.venv\Scripts\activate        # Windows PowerShell
source .venv/bin/activate     # macOS / Linux

# Install all dependencies
uv pip install -e .

# If you see "starlette and sse-starlette required" error:
uv pip install "a2a-sdk[http-server]"

# Create your .env file
echo ANTHROPIC_API_KEY=sk-ant-your-key-here > .env

# Start the agent
python -m agent
```

**Expected output:**
```
INFO - Starting UI Generator agent at http://localhost:10002
INFO - UIGeneratorAgent initialized with model: claude-sonnet-4-5
```

---

### Step 2 — Next.js Frontend

```bash
# From the project root (not a2a-agent/)
npm install

# Create environment file
echo A2A_AGENT_URL=http://localhost:10002 > .env.local

# Start the dev server
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** in an **incognito window** to avoid browser extension hydration conflicts.

---

### Environment Variables

| File | Variable | Description |
|---|---|---|
| `a2a-agent/.env` | `ANTHROPIC_API_KEY` | Your Anthropic API key (`sk-ant-...`) |
| `a2a-agent/.env` | `LITELLM_MODEL` | *(optional)* Override model, default: `claude-sonnet-4-5` |
| `.env.local` | `A2A_AGENT_URL` | URL of running A2A agent, default: `http://localhost:10002` |

---

## 🎨 UI Walkthrough

### Idle Screen
- Large animated headline — *"Describe it. Claude builds it."*
- Auto-rotating placeholder prompts in the textarea
- One-click example prompt chips

### Thinking State
- Three animated bouncing dots (purple → lavender → cyan)
- Shows the prompt currently being processed

### Rendered State
- **Header bar** — active prompt, refinement count badge, Refine and New UI buttons
- **Version Timeline** — horizontal scrollable strip (`v1 › v2 › v3 ● now`); active version glows purple; auto-scrolls to newest
- **Canvas** — clean white surface with the live A2UI component
- **Refine bar** — press Enter or → to send; full conversation context preserved

### Version Preview Modal
- Click any past version pill → full-screen overlay opens
- Live re-renders that A2UI snapshot (actual component, not a screenshot)
- Shows generation timestamp and refinement count
- **↩ Restore & Continue** — branches from that version's exact state and history
- Press `Esc` or click outside to close

---

## 🐳 Docker (Agent)

```bash
cd a2a-agent
docker build -t morphic-ui-agent .
docker run -p 10002:10002 -e ANTHROPIC_API_KEY=sk-ant-... morphic-ui-agent
```

---

## 🔧 Troubleshooting

| Error | Fix |
|---|---|
| `ImportError: starlette and sse-starlette required` | `uv pip install "a2a-sdk[http-server]"` |
| pip installs to Anaconda instead of `.venv` | Use `.venv\Scripts\pip install ...` explicitly |
| React hydration error (`data-gptw=""` in browser) | Open in incognito — a browser extension is injecting DOM attributes |
| Agent starts but no UI renders | Check `ANTHROPIC_API_KEY` in `a2a-agent/.env` is valid |
| `Cannot reach A2A agent` / 503 error | Start the Python agent before the frontend |

---

## 🏆 Hackathon Judging Alignment

| Criterion | How We Address It |
|---|---|
| **Working Prototype & Execution** | Fully functional end-to-end: prompt → Claude → A2UI JSON → live UI → refinement loop. Schema validation + auto-retry ensures stable output. |
| **Interface Novelty & Playfulness** | A blank canvas that morphs into live interactive UI on demand. Horizontal version timeline as "UI version control." No chat window, no templates — pure generative surface. |
| **Theme Alignment: Generative Interfaces** | Claude *is* the UI — every component, layout, and data binding is agent-authored at runtime. The interface itself is the innovation. |
| **Leveraging Claude's Capabilities** | Complex nested A2UI JSON schema requires Claude's precise instruction-following. Multi-turn conversation history enables coherent refinement. Auto-retry with targeted schema errors uses Claude's error-correction strength. |

---

## 👥 Team

Built at the **AI Tinkerers "AI Interfaces" Hackathon**, February 21, 2026, hosted at Betaworks, New York City.

---

## 📄 License

MIT
