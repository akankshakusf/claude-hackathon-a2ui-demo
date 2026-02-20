"use client";

import { useState, useRef, useEffect, useCallback } from "react";

type AppState = "idle" | "thinking" | "rendered" | "error";

interface HistoryTurn {
  role: "user" | "assistant";
  content: string;
}

interface UIVersion {
  id: number;
  prompt: string;
  messages: Record<string, unknown>[];
  history: HistoryTurn[];
  timestamp: Date;
}

const PROMPTS = [
  "Build a contact form with name, email, and message",
  "Create a dashboard with 3 KPI stat cards",
  "Make a team member profile card for Sarah Chen, Lead Designer",
  "Generate a todo list for launching a product",
  "Design a booking confirmation for a flight to Tokyo",
  "Create a feedback survey with star ratings",
  "Build a settings panel with toggles and dropdowns",
  "Make a job application form",
];

function ThinkingDots() {
  return (
    <div className="thinking">
      <span className="dot" />
      <span className="dot" />
      <span className="dot" />
    </div>
  );
}

function A2UIRenderer({ messages }: { messages: Record<string, unknown>[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  useEffect(() => {
    if (!mounted || !containerRef.current || messages.length === 0) return;

    const init = async () => {
      try {
        await import("@a2ui/lit");
        const { Data } = await import("@a2ui/lit/0.8");
        const { ContextProvider, createContext } = await import("@lit/context");
        const themeContext = createContext("A2UITheme");

        if (!containerRef.current) return;
        containerRef.current.innerHTML = "";

        const beginMsg = messages.find((m) => "beginRendering" in m) as any;
        if (!beginMsg?.beginRendering) return;
        const { surfaceId } = beginMsg.beginRendering;

        const theme = {
          components: {
            Text: { all: {}, h1: {}, h2: {}, h3: {}, h4: {}, h5: {}, caption: {}, body: {} },
            Button: {},
            TextField: { container: {}, label: {}, element: {} },
            Icon: {},
            Card: {},
            Row: {},
            Column: {},
            List: {},
            Divider: {},
            CheckBox: {},
            Slider: {},
            MultipleChoice: {},
            DateTimeInput: {},
            Tabs: {},
            Modal: {},
          },
          markdown: {},
          additionalStyles: {},
        };

        const processor = new Data.A2uiMessageProcessor();
        processor.processMessages(messages);
        const surface = processor.getSurfaces().get(surfaceId);
        if (!surface) { console.error("[A2UI] No surface for id:", surfaceId); return; }

        const wrapper = document.createElement("div");
        wrapper.style.cssText = "width:100%;";
        containerRef.current.appendChild(wrapper);

        new ContextProvider(wrapper, { context: themeContext, initialValue: theme });

        const el = document.createElement("a2ui-surface") as any;
        el.style.cssText = "width:100%; display:block;";
        wrapper.appendChild(el);

        await customElements.whenDefined("a2ui-surface");
        await new Promise(r => setTimeout(r, 150));

        el.surfaceId = surfaceId;
        el.processor = processor;
        el.surface = surface;

        console.log("[A2UI] Rendered successfully");
      } catch (e) {
        console.error("[A2UI] Render error:", e);
      }
    };

    init();
  }, [mounted, messages]);

  if (!mounted) return null;
  return (
    <div
      ref={containerRef}
      style={{ width: "100%", minHeight: "300px", background: "#fff", borderRadius: "12px", padding: "24px", color: "#111" }}
    />
  );
}

// Version Preview Modal
function VersionPreviewModal({
  version,
  onClose,
  onRestore,
}: {
  version: UIVersion;
  onClose: () => void;
  onRestore: (version: UIVersion) => void;
}) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-meta">
            <span className="modal-version-badge">v{version.id}</span>
            <span className="modal-prompt">{version.prompt}</span>
          </div>
          <div className="modal-actions">
            <button className="ab p" onClick={() => { onRestore(version); onClose(); }}>
              ↩ Restore & Continue
            </button>
            <button className="ab modal-close" onClick={onClose}>✕</button>
          </div>
        </div>
        <div className="modal-canvas">
          <A2UIRenderer messages={version.messages} />
        </div>
        <div className="modal-footer">
          <span className="modal-ts">
            Generated at {version.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </span>
          {version.history.length > 2 && (
            <span className="history-badge">
              {Math.floor(version.history.length / 2)} refinement{version.history.length > 4 ? "s" : ""} applied
            </span>
          )}
          <span style={{ marginLeft: "auto", fontFamily: "var(--mono)", fontSize: "10px", color: "var(--dim)" }}>
            esc to close
          </span>
        </div>
      </div>
    </div>
  );
}

// Version Timeline Strip
function VersionTimeline({
  versions,
  activeId,
  onSelect,
}: {
  versions: UIVersion[];
  activeId: number;
  onSelect: (v: UIVersion) => void;
}) {
  const stripRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (stripRef.current) {
      stripRef.current.scrollLeft = stripRef.current.scrollWidth;
    }
  }, [versions.length]);

  if (versions.length === 0) return null;

  return (
    <div className="timeline-wrap">
      <span className="timeline-label">VERSIONS</span>
      <div className="timeline-strip" ref={stripRef}>
        {versions.map((v, idx) => (
          <div key={v.id} style={{ display: "flex", alignItems: "center", gap: "4px", flexShrink: 0 }}>
            <button
              className={`version-pill ${v.id === activeId ? "active" : ""}`}
              onClick={() => v.id !== activeId && onSelect(v)}
              title={v.prompt}
            >
              <span className="pill-num">v{v.id}</span>
              <span className="pill-prompt">{v.prompt.length > 28 ? v.prompt.slice(0, 28) + "…" : v.prompt}</span>
            </button>
            {idx < versions.length - 1 && <span className="pill-arrow">›</span>}
          </div>
        ))}
        <div className="pill-now">
          <span className="pill-dot" />
          <span className="pill-now-label">now</span>
        </div>
      </div>
    </div>
  );
}

// Main Page
export default function Home() {
  const [input, setInput] = useState("");
  const [state, setState] = useState<AppState>("idle");
  const [a2uiMessages, setA2uiMessages] = useState<Record<string, unknown>[]>([]);
  const [lastPrompt, setLastPrompt] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [placeholderIdx, setPlaceholderIdx] = useState(0);
  const [history, setHistory] = useState<HistoryTurn[]>([]);
  const [versions, setVersions] = useState<UIVersion[]>([]);
  const [activeVersionId, setActiveVersionId] = useState(0);
  const [previewVersion, setPreviewVersion] = useState<UIVersion | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const refineRef = useRef<HTMLInputElement>(null);
  const versionCounter = useRef(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIdx((i) => (i + 1) % PROMPTS.length);
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  const submit = async (prompt: string, isRefinement = false) => {
    const trimmed = prompt.trim();
    if (!trimmed || state === "thinking") return;

    setLastPrompt(trimmed);
    setInput("");
    setState("thinking");
    setErrorMsg("");

    if (!isRefinement) {
      setA2uiMessages([]);
      setHistory([]);
      setVersions([]);
      versionCounter.current = 0;
    }

    const historyToSend = isRefinement ? history : [];

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: trimmed, history: historyToSend }),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      if (!data.messages || data.messages.length === 0)
        throw new Error("Claude generated no UI — try rephrasing");

      const newHistory = [
        ...historyToSend,
        { role: "user" as const, content: trimmed },
        {
          role: "assistant" as const,
          content: data.text
            ? `${data.text}\n---a2ui_JSON---\n${JSON.stringify(data.messages)}`
            : JSON.stringify(data.messages),
        },
      ];

      versionCounter.current += 1;
      const newVersion: UIVersion = {
        id: versionCounter.current,
        prompt: trimmed,
        messages: data.messages,
        history: newHistory,
        timestamp: new Date(),
      };

      setA2uiMessages(data.messages);
      setHistory(newHistory);
      setVersions((prev) => [...prev, newVersion]);
      setActiveVersionId(newVersion.id);
      setState("rendered");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Something went wrong");
      setState("error");
    }
  };

  const restoreVersion = useCallback((version: UIVersion) => {
    setA2uiMessages(version.messages);
    setHistory(version.history);
    setLastPrompt(version.prompt);
    setActiveVersionId(version.id);
    setState("rendered");
    setVersions((prev) => prev.slice(0, prev.findIndex((v) => v.id === version.id) + 1));
    versionCounter.current = version.id;
    setTimeout(() => refineRef.current?.focus(), 80);
  }, []);

  const reset = () => {
    setState("idle");
    setA2uiMessages([]);
    setInput("");
    setErrorMsg("");
    setHistory([]);
    setVersions([]);
    setActiveVersionId(0);
    versionCounter.current = 0;
    setTimeout(() => inputRef.current?.focus(), 80);
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
          --bg: #f8f7ff; --surface: #ffffff; --surface2: #f0eeff;
          --border: rgba(0,0,0,0.1); --border-hi: rgba(109,40,217,0.5);
          --accent: #6d28d9; --accent-soft: #7c3aed; --accent2: #0891b2;
          --glow: rgba(109,40,217,0.12); --text: #1a1035;
          --muted: #6b7280; --dim: #9ca3af;
          --mono: 'DM Mono', monospace; --display: 'Syne', sans-serif; --r: 14px;
        }
        body { background: var(--bg); color: var(--text); font-family: var(--display); min-height: 100vh; overflow-x: hidden; -webkit-font-smoothing: antialiased; }
        body::before { content: ''; position: fixed; inset: 0; background-image: linear-gradient(rgba(109,40,217,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(109,40,217,0.04) 1px, transparent 1px); background-size: 44px 44px; pointer-events: none; z-index: 0; }
        .orb { position: fixed; border-radius: 50%; filter: blur(130px); pointer-events: none; z-index: 0; }
        .orb1 { width: 700px; height: 700px; background: radial-gradient(circle, rgba(109,40,217,0.08), transparent 70%); top: -250px; left: -250px; }
        .orb2 { width: 550px; height: 550px; background: radial-gradient(circle, rgba(8,145,178,0.06), transparent 70%); bottom: -180px; right: -180px; }
        .app { position: relative; z-index: 1; min-height: 100vh; display: flex; flex-direction: column; }
        .hdr { padding: 18px 32px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); background: rgba(255,255,255,0.85); backdrop-filter: blur(10px); }
        .logo { display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 700; letter-spacing: -0.025em; color: var(--text); }
        .pulse { width: 9px; height: 9px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 10px rgba(109,40,217,0.4); animation: pulse 2.2s ease-in-out infinite; }
        @keyframes pulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.5; transform:scale(0.8); } }
        .chip-badge { font-family: var(--mono); font-size: 10px; letter-spacing: 0.06em; padding: 3px 9px; border-radius: 5px; background: rgba(109,40,217,0.08); border: 1px solid rgba(109,40,217,0.2); color: var(--accent); }
        .idle { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; padding: 48px 24px; gap: 52px; }
        .hero { text-align:center; max-width: 660px; }
        .eyebrow { font-family: var(--mono); font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--accent2); margin-bottom: 18px; }
        h1 { font-size: clamp(38px, 6.5vw, 68px); font-weight: 800; line-height: 1.04; letter-spacing: -0.045em; margin-bottom: 18px; color: var(--text); }
        h1 span { background: linear-gradient(135deg, #6d28d9 0%, #0891b2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .sub { font-size: 16px; color: var(--muted); line-height: 1.65; font-weight: 400; }
        .iz { width:100%; max-width: 700px; display:flex; flex-direction:column; gap:14px; }
        .iw { position: relative; background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); transition: border-color 0.2s, box-shadow 0.2s; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
        .iw:focus-within { border-color: var(--border-hi); box-shadow: 0 0 0 3px var(--glow), 0 4px 20px rgba(0,0,0,0.08); }
        .iw textarea { width:100%; background:transparent; border:none; outline:none; resize:none; color: var(--text); font-family: var(--display); font-size: 16px; line-height: 1.55; padding: 20px 130px 20px 22px; min-height: 68px; max-height: 180px; }
        .iw textarea::placeholder { color: var(--dim); }
        .ia { position:absolute; right:14px; bottom:14px; display:flex; align-items:center; gap:10px; }
        .kh { font-family: var(--mono); font-size: 10px; color: var(--dim); }
        .go { background: linear-gradient(135deg, var(--accent), #5b21b6); color: #fff; border:none; border-radius:9px; width:38px; height:38px; cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:17px; transition: opacity 0.15s, transform 0.15s; flex-shrink:0; box-shadow: 0 2px 8px rgba(109,40,217,0.3); }
        .go:hover:not(:disabled) { opacity:0.88; transform:scale(1.06); }
        .go:disabled { opacity:0.25; cursor:not-allowed; }
        .chips { display:flex; flex-wrap:wrap; gap:8px; }
        .chip { font-family: var(--mono); font-size: 11px; padding: 6px 13px; border-radius: 7px; background: var(--surface); border: 1px solid var(--border); color: var(--muted); cursor:pointer; transition: all 0.15s; white-space: nowrap; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
        .chip:hover { border-color: rgba(109,40,217,0.35); color: var(--accent); background: rgba(109,40,217,0.05); }
        .thinking-scr { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:22px; }
        .thinking { display:flex; gap:7px; align-items:center; }
        .dot { width:9px; height:9px; border-radius:50%; background: var(--accent); animation: bop 1.4s ease-in-out infinite; }
        .dot:nth-child(2) { animation-delay:0.2s; background: #8b5cf6; }
        .dot:nth-child(3) { animation-delay:0.4s; background: var(--accent2); }
        @keyframes bop { 0%,80%,100% { transform:translateY(0); opacity:0.35; } 40% { transform:translateY(-11px); opacity:1; } }
        .thlabel { font-family: var(--mono); font-size:11px; letter-spacing:0.12em; text-transform:uppercase; color: var(--accent); }
        .thprompt { font-family: var(--mono); font-size:13px; color: var(--muted); max-width:500px; text-align:center; padding:0 24px; line-height:1.5; }
        .thprompt em { color: var(--text); font-style:normal; }
        .rendered { flex:1; display:flex; flex-direction:column; overflow:hidden; }
        .rh { padding: 12px 24px; display:flex; align-items:center; gap:12px; border-bottom: 1px solid var(--border); flex-shrink:0; background: var(--surface); }
        .rl { font-family:var(--mono); font-size:10px; color:var(--dim); letter-spacing:0.06em; }
        .rp { font-size:13px; color:var(--muted); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .ras { display:flex; gap:8px; align-items:center; }
        .ab { font-family:var(--mono); font-size:11px; padding:5px 13px; border-radius:7px; border:1px solid var(--border); background:var(--surface); color: var(--muted); cursor:pointer; transition:all 0.15s; white-space:nowrap; }
        .ab:hover { border-color: rgba(109,40,217,0.35); color: var(--accent); }
        .ab.p { background: rgba(109,40,217,0.08); border-color:rgba(109,40,217,0.3); color: var(--accent); }
        .ab.p:hover { background: rgba(109,40,217,0.14); }
        .history-badge { font-family:var(--mono); font-size:10px; color: var(--accent); padding:2px 8px; border-radius:4px; background:rgba(109,40,217,0.08); border:1px solid rgba(109,40,217,0.2); }
        .canvas { flex:1; overflow-y:auto; display:flex; align-items:flex-start; justify-content:center; padding: 32px 24px 52px; background: var(--bg); }
        .ci { width:100%; max-width:700px; animation: fadeUp 0.4s ease; }
        @keyframes fadeUp { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
        .refbar { border-top: 1px solid var(--border); padding:16px 24px; display:flex; gap:10px; align-items:center; flex-shrink:0; background: var(--surface); }
        .ri { flex:1; background: var(--bg); border:1px solid var(--border); border-radius:9px; color:var(--text); font-family:var(--display); font-size:14px; padding:10px 16px; outline:none; transition: border-color 0.2s; }
        .ri:focus { border-color: var(--border-hi); box-shadow: 0 0 0 3px var(--glow); }
        .ri::placeholder { color: var(--dim); }
        .err { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px; padding:40px; text-align:center; }
        .err-icon { font-size:42px; }
        .err-title { font-size:20px; font-weight:700; color: var(--text); }
        .err-msg { font-family:var(--mono); font-size:12px; color:var(--muted); max-width:420px; line-height:1.5; }

        /* Version Timeline */
        .timeline-wrap { border-bottom: 1px solid var(--border); padding: 10px 24px; display: flex; align-items: center; gap: 14px; flex-shrink: 0; background: rgba(255,255,255,0.9); backdrop-filter: blur(8px); }
        .timeline-label { font-family: var(--mono); font-size: 9px; letter-spacing: 0.14em; color: var(--dim); flex-shrink: 0; text-transform: uppercase; }
        .timeline-strip { display: flex; align-items: center; gap: 4px; overflow-x: auto; scrollbar-width: none; flex: 1; padding-bottom: 2px; }
        .timeline-strip::-webkit-scrollbar { display: none; }
        .version-pill { display: flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; border: 1px solid var(--border); background: var(--surface2); color: var(--muted); font-family: var(--mono); font-size: 10px; cursor: pointer; transition: all 0.15s; white-space: nowrap; flex-shrink: 0; }
        .version-pill:hover:not(.active) { border-color: rgba(109,40,217,0.35); color: var(--accent); background: rgba(109,40,217,0.05); transform: translateY(-1px); }
        .version-pill.active { border-color: var(--accent); background: rgba(109,40,217,0.1); color: var(--accent); cursor: default; box-shadow: 0 0 0 3px rgba(109,40,217,0.08); }
        .pill-num { font-weight: 600; color: var(--accent); font-size: 9px; }
        .version-pill.active .pill-num { color: var(--accent); }
        .pill-prompt { max-width: 160px; overflow: hidden; text-overflow: ellipsis; }
        .pill-arrow { color: var(--dim); font-size: 14px; line-height: 1; pointer-events: none; }
        .pill-now { display: flex; align-items: center; gap: 5px; padding: 0 6px; flex-shrink: 0; }
        .pill-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent2); box-shadow: 0 0 6px rgba(8,145,178,0.5); animation: pulse 2s ease-in-out infinite; }
        .pill-now-label { font-family: var(--mono); font-size: 9px; color: var(--accent2); letter-spacing: 0.1em; }

        /* Version Preview Modal */
        .modal-overlay { position: fixed; inset: 0; background: rgba(15,10,30,0.5); backdrop-filter: blur(12px); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 24px; animation: fadeIn 0.18s ease; }
        @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
        .modal-box { background: var(--surface); border: 1px solid rgba(109,40,217,0.2); border-radius: 18px; width: 100%; max-width: 760px; max-height: 88vh; display: flex; flex-direction: column; box-shadow: 0 24px 80px rgba(0,0,0,0.15), 0 0 0 1px rgba(109,40,217,0.08); animation: slideUp 0.22s ease; }
        @keyframes slideUp { from { opacity:0; transform:translateY(20px) scale(0.97); } to { opacity:1; transform:translateY(0) scale(1); } }
        .modal-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-shrink: 0; background: var(--surface2); border-radius: 18px 18px 0 0; }
        .modal-meta { display: flex; align-items: center; gap: 10px; min-width: 0; }
        .modal-version-badge { font-family: var(--mono); font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 6px; background: rgba(109,40,217,0.1); border: 1px solid rgba(109,40,217,0.25); color: var(--accent); flex-shrink: 0; }
        .modal-prompt { font-size: 13px; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .modal-actions { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
        .modal-close { padding: 5px 10px !important; }
        .modal-canvas { flex: 1; overflow-y: auto; padding: 28px 24px; scrollbar-width: thin; scrollbar-color: var(--dim) transparent; background: var(--bg); }
        .modal-footer { padding: 12px 20px; border-top: 1px solid var(--border); display: flex; align-items: center; gap: 10px; flex-shrink: 0; background: var(--surface2); border-radius: 0 0 18px 18px; }
        .modal-ts { font-family: var(--mono); font-size: 10px; color: var(--dim); }
      `}</style>

      <div className="orb orb1" />
      <div className="orb orb2" />

      <div className="app">
        <header className="hdr">
          <div className="logo">
            <div className="pulse" />
            <span>Morphic UI</span>
          </div>
          <span className="chip-badge">Claude · A2UI · A2A</span>
        </header>

        {state === "idle" && (
          <main className="idle">
            <div className="hero">
              <p className="eyebrow">Agent-Driven Generative Interface</p>
              <h1>Describe it.<br /><span>Claude builds it.</span></h1>
              <p className="sub">
                Type any interface you need — a form, a dashboard, a card, a list.
                Claude reasons about your intent and assembles a live, interactive UI.
              </p>
            </div>
            <div className="iz">
              <div className="iw">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      submit(input, false);
                    }
                  }}
                  placeholder={PROMPTS[placeholderIdx]}
                  rows={2}
                  autoFocus
                />
                <div className="ia">
                  <span className="kh">↵ enter</span>
                  <button className="go" onClick={() => submit(input, false)} disabled={!input.trim()}>→</button>
                </div>
              </div>
              <div className="chips">
                {PROMPTS.slice(0, 5).map((p) => (
                  <button key={p} className="chip" onClick={() => submit(p, false)}>{p}</button>
                ))}
              </div>
            </div>
          </main>
        )}

        {state === "thinking" && (
          <div className="thinking-scr">
            <ThinkingDots />
            <div className="thlabel">Claude is composing your UI</div>
            <p className="thprompt">"<em>{lastPrompt}</em>"</p>
          </div>
        )}

        {state === "rendered" && (
          <div className="rendered">
            <div className="rh">
              <span className="rl">ACTIVE</span>
              <span className="rp">{lastPrompt}</span>
              <div className="ras">
                {history.length > 2 && (
                  <span className="history-badge">{Math.floor(history.length / 2)} refinement{history.length > 4 ? "s" : ""}</span>
                )}
                <button className="ab p" onClick={() => refineRef.current?.focus()}>Refine ↑</button>
                <button className="ab" onClick={reset}>New UI</button>
              </div>
            </div>

            {versions.length > 1 && (
              <VersionTimeline
                versions={versions}
                activeId={activeVersionId}
                onSelect={setPreviewVersion}
              />
            )}

            <div className="canvas">
              <div className="ci">
                <A2UIRenderer messages={a2uiMessages} />
              </div>
            </div>
            <div className="refbar">
              <input
                ref={refineRef}
                className="ri"
                placeholder="Refine — e.g. 'add a phone field' or 'make it dark mode'"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    const val = (e.target as HTMLInputElement).value;
                    if (val.trim()) {
                      submit(val, true);
                      (e.target as HTMLInputElement).value = "";
                    }
                  }
                }}
              />
              <button className="ab p" onClick={() => {
                if (refineRef.current?.value.trim()) {
                  submit(refineRef.current.value, true);
                  refineRef.current.value = "";
                }
              }}>→</button>
            </div>
          </div>
        )}

        {state === "error" && (
          <div className="err">
            <div className="err-icon">⚠</div>
            <div className="err-title">Generation failed</div>
            <p className="err-msg">{errorMsg}</p>
            <button className="ab p" onClick={reset}>Try again</button>
          </div>
        )}
      </div>

      {previewVersion && (
        <VersionPreviewModal
          version={previewVersion}
          onClose={() => setPreviewVersion(null)}
          onRestore={restoreVersion}
        />
      )}
    </>
  );
}