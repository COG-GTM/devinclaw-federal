"use client";

import { useEffect, useState } from "react";

interface HealthStatus {
  status: string;
  version: string;
  name: string;
}

const NAV_ITEMS = [
  { label: "Dashboard", href: "/" },
  { label: "Tasks", href: "/tasks" },
  { label: "Sessions", href: "/sessions" },
  { label: "Skills", href: "/skills" },
  { label: "Compliance", href: "/compliance" },
  { label: "Audit", href: "/audit" },
  { label: "Terminal", href: "/terminal" },
];

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  return (
    <div style={{ minHeight: "100vh", display: "flex" }}>
      {/* Sidebar */}
      <nav
        style={{
          width: 240,
          background: "#111118",
          borderRight: "1px solid #222",
          padding: "24px 0",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div style={{ padding: "0 20px 24px", borderBottom: "1px solid #222" }}>
          <h1 style={{ fontSize: 18, fontWeight: 700, margin: 0, color: "#fff" }}>
            DevinClaw Federal
          </h1>
          <span style={{ fontSize: 12, color: "#666", marginTop: 4, display: "block" }}>
            Standalone Orchestrator
          </span>
        </div>

        <div style={{ padding: "16px 12px", flex: 1 }}>
          {NAV_ITEMS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              style={{
                display: "block",
                padding: "10px 12px",
                borderRadius: 6,
                color: item.href === "/" ? "#fff" : "#999",
                textDecoration: "none",
                fontSize: 14,
                background: item.href === "/" ? "#1a1a2e" : "transparent",
                marginBottom: 2,
              }}
            >
              {item.label}
            </a>
          ))}
        </div>

        <div style={{ padding: "12px 20px", borderTop: "1px solid #222", fontSize: 12, color: "#555" }}>
          {health ? (
            <span style={{ color: "#4caf50" }}>API Connected v{health.version}</span>
          ) : (
            <span style={{ color: "#f44336" }}>API Disconnected</span>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ flex: 1, padding: 32 }}>
        <h2 style={{ fontSize: 24, fontWeight: 600, marginTop: 0, marginBottom: 24 }}>
          Operations Dashboard
        </h2>

        {/* Metrics Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
          {[
            { label: "Active Tasks", value: "0", color: "#2196f3" },
            { label: "Active Sessions", value: "0", color: "#4caf50" },
            { label: "Skills Loaded", value: "15", color: "#ff9800" },
            { label: "Compliance Score", value: "92%", color: "#9c27b0" },
          ].map((metric) => (
            <div
              key={metric.label}
              style={{
                background: "#111118",
                border: "1px solid #222",
                borderRadius: 8,
                padding: 20,
              }}
            >
              <div style={{ fontSize: 12, color: "#888", marginBottom: 8 }}>{metric.label}</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: metric.color }}>{metric.value}</div>
            </div>
          ))}
        </div>

        {/* Framework Status */}
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Compliance Frameworks</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16, marginBottom: 32 }}>
          {[
            { name: "NIST 800-53", status: "Compliant", controls: "18/18" },
            { name: "DISA STIG", status: "Compliant", controls: "0 CAT I findings" },
            { name: "FedRAMP Moderate", status: "In Progress", controls: "142/325" },
            { name: "FISMA", status: "Compliant", controls: "Next: 2027-01-15" },
          ].map((fw) => (
            <div
              key={fw.name}
              style={{
                background: "#111118",
                border: "1px solid #222",
                borderRadius: 8,
                padding: 16,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{fw.name}</div>
                <div style={{ fontSize: 12, color: "#888" }}>{fw.controls}</div>
              </div>
              <span
                style={{
                  fontSize: 12,
                  padding: "4px 10px",
                  borderRadius: 12,
                  background: fw.status === "Compliant" ? "#1b5e20" : "#4a3000",
                  color: fw.status === "Compliant" ? "#4caf50" : "#ff9800",
                }}
              >
                {fw.status}
              </span>
            </div>
          ))}
        </div>

        {/* Guardrails Summary */}
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Guardrail Gates (HG-001 to HG-010)</h3>
        <div
          style={{
            background: "#111118",
            border: "1px solid #222",
            borderRadius: 8,
            padding: 16,
          }}
        >
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 }}>
            {Array.from({ length: 10 }, (_, i) => (
              <div
                key={i}
                style={{
                  padding: "8px 12px",
                  borderRadius: 6,
                  background: "#1b5e20",
                  textAlign: "center",
                  fontSize: 12,
                }}
              >
                <div style={{ fontWeight: 600, color: "#4caf50" }}>HG-{String(i + 1).padStart(3, "0")}</div>
                <div style={{ color: "#81c784", marginTop: 2 }}>Active</div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
