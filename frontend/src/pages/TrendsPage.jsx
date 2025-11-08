import { useState } from "react";
import { BrainCircuit } from "lucide-react";
import { fetchTrends } from "../services/api.js";
import { useAppContext } from "../context/AppContext.jsx";
import AIInput from "../components/ui/AIInput.jsx";
import ButtonArrowDown from "../components/ui/ButtonArrowDown.jsx";
import DotLoader from "../components/ui/DotLoader.jsx";

const NICHE_SUGGESTIONS = [
  "AI startup breakdowns",
  "Creator economy playbooks",
  "Tech review storytelling"
];

const GROWTH_SUGGESTIONS = [
  "10k views / 24h",
  "2x follower lift",
  "Spike saves & shares"
];

export default function TrendsPage() {
  const {
    trends,
    setTrends,
    setSelectedTrend,
    setErrorMessage,
    setIsBusy,
    isBusy
  } = useAppContext();

  const [niche, setNiche] = useState("");
  const [growthGoal, setGrowthGoal] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!niche.trim()) {
      setErrorMessage("Add a niche so Nexus knows where to scout.");
      return;
    }
    setIsBusy(true);
    setErrorMessage("");

    try {
      const { data } = await fetchTrends({ niche, growth_goal: growthGoal });
      setTrends(data.trends || []);
      if (data.trends?.length) {
        setSelectedTrend(data.trends[0]);
      }
    } catch (error) {
      console.error("Failed to fetch trends", error);
      const detail = error.response?.data?.detail;
      setErrorMessage(detail || "Unable to fetch trends. Check the backend log.");
      setTrends([]);
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <section className="card">
      <header className="card__header">
        <h2>BuzzFind: Trend Intelligence</h2>
        <p>Feed Nexus your arena and end goal—our scouts surface what deserves your next drop.</p>
      </header>

      <form onSubmit={handleSubmit} className="field-grid" style={{ marginTop: "1.5rem" }}>
        <AIInput
          id="niche"
          label="Creator niche"
          value={niche}
          onChange={(event) => setNiche(event.target.value)}
          placeholder="e.g. AI founders weekly, tech mythbusting"
          suggestions={NICHE_SUGGESTIONS}
        />

        <AIInput
          id="goal"
          label="Growth outcome"
          value={growthGoal}
          onChange={(event) => setGrowthGoal(event.target.value)}
          placeholder="define the metric Nexus should chase"
          suggestions={GROWTH_SUGGESTIONS}
        />

        <div className="field-group" style={{ alignSelf: "end" }}>
          <ButtonArrowDown type="submit" disabled={isBusy || !niche.trim()}>
            {isBusy ? "Scanning" : "Get trend map"}
          </ButtonArrowDown>
        </div>
      </form>

      {isBusy ? <DotLoader label="Nexus scouting live data" /> : null}

      {trends.length ? (
        <div className="grid trends" style={{ marginTop: "2rem" }}>
          {trends.map((trend, index) => (
            <article key={`${trend.title}-${index}`} className="trend-card">
              <header className="trend-card__header">
                <BrainCircuit size={18} aria-hidden="true" />
                <strong>{trend.title}</strong>
              </header>
              <p>{trend.summary}</p>
              {trend.source ? (
                <span className="toast">Source: {trend.source}</span>
              ) : null}
              <ButtonArrowDown
                variant="secondary"
                type="button"
                onClick={() => setSelectedTrend(trend)}
              >
                Use this signal
              </ButtonArrowDown>
            </article>
          ))}
        </div>
      ) : !isBusy ? (
        <p style={{ marginTop: "2.5rem", color: "var(--text-secondary)" }}>
          Nexus is ready. Feed a niche and target to see live opportunities.
        </p>
      ) : null}
    </section>
  );
}
