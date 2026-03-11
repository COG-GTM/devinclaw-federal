import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DevinClaw Federal",
  description: "AI-Powered Federal Modernization Orchestrator",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "system-ui, -apple-system, sans-serif", background: "#0a0a0f", color: "#e0e0e0" }}>
        <nav style={{ display: "flex", gap: "1rem", padding: "1rem 2rem", background: "#111118", borderBottom: "1px solid #222" }}>
          <a href="/" style={{ color: "#60a5fa", textDecoration: "none", fontWeight: 600 }}>Dashboard</a>
          <a href="/terminal" style={{ color: "#60a5fa", textDecoration: "none" }}>Terminal</a>
          <a href="/trace" style={{ color: "#60a5fa", textDecoration: "none" }}>Trace</a>
          <a href="/topology" style={{ color: "#60a5fa", textDecoration: "none" }}>Topology</a>
          <a href="/rollups" style={{ color: "#60a5fa", textDecoration: "none" }}>Rollups</a>
        </nav>
        {children}
      </body>
    </html>
  );
}
