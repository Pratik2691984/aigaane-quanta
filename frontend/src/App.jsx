import { useEffect, useState } from "react";
import AigaaneInspector from "./AigaaneInspector";
import NyayaTab from "./NyayaTab";
import LexiconTab from "./LexiconTab";
import PipelineTab from "./PipelineTab";
import Studio3Tab from "./Studio3Tab";
import { probeEngine } from "./engineStatus";

export default function App() {
  const [engineStatus, setEngineStatus] = useState("checking...");
  const [activeTab, setActiveTab] = useState("inspector");

  useEffect(() => {
    probeEngine().then((res) => setEngineStatus(res.status));
  }, []);

  const tabs = [
    { id: "inspector", label: "Aigaane Inspector" },
    { id: "nyaya", label: "Nyāya Verifier" },
    { id: "lexicon", label: "Lexicon" },
    { id: "studio3", label: "Studio III (Tāla)" },
    { id: "pipeline", label: "Pipeline" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a" }}>
      <div
        style={{
          padding: "10px",
          background: engineStatus === "ok" ? "#064e3b" : "#7f1d1d",
          color: "white",
          textAlign: "center",
          fontWeight: "bold",
        }}
      >
        Engine Status: {engineStatus.toUpperCase()}
      </div>

      <nav style={{
        display: "flex", gap: "5px", padding: "10px",
        background: "#1e293b", borderBottom: "1px solid #334155",
      }}>
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            style={{
              padding: "10px 20px",
              background: activeTab === t.id ? "#38bdf8" : "transparent",
              color: activeTab === t.id ? "#0f172a" : "#94a3b8",
              border: "none",
              borderRadius: "6px",
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main style={{ maxWidth: "1200px", margin: "0 auto" }}>
        {activeTab === "inspector" && <AigaaneInspector />}
        {activeTab === "nyaya" && <NyayaTab />}
        {activeTab === "lexicon" && <LexiconTab />}
        {activeTab === "studio3" && <Studio3Tab />}
        {activeTab === "pipeline" && <PipelineTab />}
      </main>
    </div>
  );
}