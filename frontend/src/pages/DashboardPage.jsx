import { ArrowRight } from "lucide-react";
import AppVisualLayout from "../components/ui/AppVisualLayout.jsx";
import ButtonArrowDown from "../components/ui/ButtonArrowDown.jsx";
import { useNavigate } from "react-router-dom";

const workflowCards = [
  {
    title: "BuzzFind",
    description: "Discover the highest-velocity trends across your niche with ripple, your trend scout.",
    agent: "ripple",
    cta: "Explore trends",
    to: "/trends"
  },
  {
    title: "Script Forge",
    description: "Generate hooks, scripts, captions with quill, your creative writer.",
    agent: "quill",
    cta: "Open script lab",
    to: "/script"
  },
  {
    title: "ShareBlast",
    description: "Clip raw videos into platform-ready shorts powered by core intelligence.",
    agent: "core",
    cta: "Process video",
    to: "/upload"
  },
  {
    title: "SignalPulse",
    description: "Track performance with pulse and connect to sponsors via envoy.",
    agent: "pulse + envoy",
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
              <span className="toast" style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
                Agent: {card.agent}
              </span>
            </header>
            <p>{card.description}</p>
            <ButtonArrowDown onClick={() => navigate(card.to)}>{card.cta}</ButtonArrowDown>
          </article>
        ))}
      </div>
    </AppVisualLayout>
  );
}
