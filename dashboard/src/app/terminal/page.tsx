"use client";

import { useEffect, useRef, useState } from "react";

export default function TerminalPage() {
  const [lines, setLines] = useState<string[]>([
    "DevinClaw Federal CLI Bridge v1.0.0",
    "Connecting to WebSocket...",
    "",
  ]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // In production, connect to /ws/terminal/{session_id}
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/terminal/default`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        setLines((prev) => [...prev, "Connected to DevinClaw API.", ""]);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "output" && data.content) {
          setLines((prev) => [...prev, data.content]);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        setLines((prev) => [...prev, "Disconnected from API.", ""]);
      };

      ws.onerror = () => {
        setConnected(false);
        setLines((prev) => [...prev, "WebSocket connection failed. API may be offline.", ""]);
      };

      return () => ws.close();
    } catch {
      setLines((prev) => [...prev, "WebSocket not available. Run with docker-compose up.", ""]);
    }
  }, []);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [lines]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLines((prev) => [...prev, `$ ${input}`]);

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "input", content: input }));
    } else {
      setLines((prev) => [...prev, `[local] Command queued: ${input}`]);
    }

    setInput("");
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: "#0a0a0f" }}>
      {/* Header */}
      <div
        style={{
          padding: "12px 20px",
          background: "#111118",
          borderBottom: "1px solid #222",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <a href="/" style={{ color: "#999", textDecoration: "none", fontSize: 14 }}>
            Dashboard
          </a>
          <span style={{ color: "#444" }}>/</span>
          <span style={{ color: "#fff", fontWeight: 600, fontSize: 14 }}>Terminal</span>
        </div>
        <span
          style={{
            fontSize: 12,
            padding: "4px 10px",
            borderRadius: 12,
            background: connected ? "#1b5e20" : "#4a0000",
            color: connected ? "#4caf50" : "#f44336",
          }}
        >
          {connected ? "Connected" : "Disconnected"}
        </span>
      </div>

      {/* Terminal */}
      <div
        ref={terminalRef}
        style={{
          flex: 1,
          padding: 16,
          fontFamily: "'Cascadia Code', 'Fira Code', 'JetBrains Mono', monospace",
          fontSize: 13,
          lineHeight: 1.6,
          overflow: "auto",
          whiteSpace: "pre-wrap",
        }}
      >
        {lines.map((line, i) => (
          <div key={i} style={{ color: line.startsWith("$") ? "#4caf50" : "#ccc" }}>
            {line}
          </div>
        ))}
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        style={{
          padding: "12px 16px",
          background: "#111118",
          borderTop: "1px solid #222",
          display: "flex",
          gap: 8,
        }}
      >
        <span style={{ color: "#4caf50", fontFamily: "monospace" }}>$</span>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a command or task description..."
          style={{
            flex: 1,
            background: "transparent",
            border: "none",
            color: "#fff",
            fontSize: 14,
            fontFamily: "'Cascadia Code', 'Fira Code', monospace",
            outline: "none",
          }}
          autoFocus
        />
      </form>
    </div>
  );
}
