import { ArrowRight } from "lucide-react";
import AppVisualLayout from "../components/ui/AppVisualLayout.jsx";
import ButtonArrowDown from "../components/ui/ButtonArrowDown.jsx";
import { useNavigate } from "react-router-dom";

const workflowCards = [
  {
    title: "agent_ripple",
    description: "Trend scout analyzing viral patterns and discovering high-velocity content opportunities.",
    cta: "Scout trends",
    to: "/trends"
  },
  {
    title: "agent_quill",
    description: "Creative writer generating hooks, scripts, and captions in your unique voice.",
    cta: "Generate script",
    to: "/script"
  },
  {
    title: "agent_core",
    description: "Strategic orchestrator processing videos and optimizing content strategy.",
    cta: "Process video",
    to: "/upload"
  },
  {
    title: "agent_pulse + agent_envoy",
    description: "Engagement tracker (pulse) and brand partnership finder (envoy) working together.",
    cta: "View analytics",
    to: "/analytics"
  }
];

export default function DashboardPage() {
  const navigate = useNavigate();

  return (
    <AppVisualLayout
      hero={
        <div className="hero">
          <span className="hero__eyebrow">Nexus Studio</span>
          <h1>AI co-founder for your short-form empire.</h1>
          <p>
            Nexus orchestrates trend scouting, script generation, sponsor outreach, and video upload workflows—one control center built for creators shipping daily.
          </p>
          <div className="hero__actions">
            <ButtonArrowDown onClick={() => navigate("/trends")}>Start with trends</ButtonArrowDown>
            <button className="button button--secondary" type="button" onClick={() => navigate("/analytics")}>
              <span>Review analytics</span>
              <ArrowRight size={16} aria-hidden="true" />
            </button>
          </div>
        </div>
      }
    >
      <div className="grid dashboard">
        {workflowCards.map((card) => (
          <article key={card.title} className="dashboard-card">
            <header>
              <h3>{card.title}</h3>
            </header>
            <p>{card.description}</p>
            <ButtonArrowDown onClick={() => navigate(card.to)}>{card.cta}</ButtonArrowDown>
          </article>
        ))}
      </div>
    </AppVisualLayout>
  );
}
