import { NextRequest, NextResponse } from "next/server";

const A2A_AGENT_URL = process.env.A2A_AGENT_URL || "http://localhost:10002";
const A2UI_EXTENSION_URI = "https://a2ui.org/a2a-extension/a2ui/v0.8";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { prompt, history } = body;

    if (!prompt || typeof prompt !== "string" || !prompt.trim()) {
      return NextResponse.json({ error: "prompt is required" }, { status: 400 });
    }

    const requestId = `req-${Date.now()}`;
    const messageId = `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

    const rpcPayload = {
      jsonrpc: "2.0",
      id: requestId,
      method: "message/send",
      params: {
        message: {
          messageId,
          role: "user",
          parts: [{ kind: "text", text: prompt.trim() }],
          extensions: [A2UI_EXTENSION_URI],
          // Attach history in message metadata so executor can read it
          metadata: {
            conversationHistory: history || [],
          },
        },
        configuration: {
          acceptedOutputModes: ["text", "application/json+a2ui"],
          extensions: [A2UI_EXTENSION_URI],
        },
        extensions: [A2UI_EXTENSION_URI],
      },
    };

    let agentResponse: Response;
    try {
      agentResponse = await fetch(A2A_AGENT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(rpcPayload),
        signal: AbortSignal.timeout(60_000),
      });
    } catch (fetchErr) {
      const code = (fetchErr as any)?.cause?.code;
      if (code === "ECONNREFUSED") {
        return NextResponse.json(
          { error: `Cannot reach the A2A agent at ${A2A_AGENT_URL}. Is the Python agent running?` },
          { status: 503 }
        );
      }
      if (fetchErr instanceof Error && fetchErr.name === "TimeoutError") {
        return NextResponse.json({ error: "A2A agent timed out." }, { status: 504 });
      }
      throw fetchErr;
    }

    if (!agentResponse.ok) {
      const errText = await agentResponse.text();
      console.error("A2A agent error:", agentResponse.status, errText);
      return NextResponse.json({ error: `Agent returned ${agentResponse.status}` }, { status: 502 });
    }

    const rpcResult = await agentResponse.json();

    if (rpcResult.error) {
      console.error("JSON-RPC error:", rpcResult.error);
      return NextResponse.json({ error: rpcResult.error.message || "Agent error" }, { status: 500 });
    }

    const a2uiMessages: Record<string, unknown>[] = [];
    let textContent = "";

    const parts =
      rpcResult.result?.status?.message?.parts ||
      rpcResult.result?.artifact?.parts ||
      rpcResult.result?.message?.parts ||
      [];

    for (const part of parts) {
      if (part.kind === "data" && part.metadata?.mimeType === "application/json+a2ui" && part.data) {
        a2uiMessages.push(part.data as Record<string, unknown>);
        continue;
      }
      if (part.kind === "text" && typeof part.text === "string") {
        const raw: string = part.text;
        if (raw.includes("---a2ui_JSON---")) {
          const [before, jsonPart] = raw.split("---a2ui_JSON---", 2);
          textContent += before.trimEnd();
          if (jsonPart?.trim()) {
            try {
              const cleaned = jsonPart.trim().replace(/^```json\s*/i, "").replace(/\s*```$/, "").trim();
              const parsed = JSON.parse(cleaned);
              if (Array.isArray(parsed)) a2uiMessages.push(...parsed);
              else a2uiMessages.push(parsed);
            } catch (e) {
              console.error("Failed to parse inline A2UI JSON:", e);
            }
          }
        } else {
          textContent += raw;
        }
      }
    }

    textContent = textContent.replace(/^<text>\s*/i, "").replace(/\s*<\/text>$/i, "").trim();
    console.log(`[generate] ${a2uiMessages.length} A2UI messages. Text: "${textContent.slice(0, 80)}"`);

    return NextResponse.json({
      messages: a2uiMessages,
      text: textContent,
      raw: process.env.NODE_ENV === "development" ? rpcResult : undefined,
    });
  } catch (err) {
    console.error("Generate route error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Internal server error" },
      { status: 500 }
    );
  }
}
