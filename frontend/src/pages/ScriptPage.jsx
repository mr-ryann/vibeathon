import { useMemo, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MessageCircleHeart } from "lucide-react";
import { generateScript } from "../services/api.js";
import { useAppContext } from "../context/AppContext.jsx";
import AIInput from "../components/ui/AIInput.jsx";
import ButtonArrowDown from "../components/ui/ButtonArrowDown.jsx";
import DotLoader from "../components/ui/DotLoader.jsx";

const VIBE_SUGGESTIONS = [
  "Playful + data-backed",
  "High energy storyteller",
  "Dry humor with receipts"
];

export default function ScriptPage() {
  const {
    trends,
    selectedTrend,
    setSelectedTrend,
    scriptResult,
    setScriptResult,
    setErrorMessage,
    setIsBusy,
    isBusy
  } = useAppContext();

  const navigate = useNavigate();
  const [vibe, setVibe] = useState("");

  const fallbackTrend = useMemo(() => trends[0] || null, [trends]);

  useEffect(() => {
    if (trends.length === 0 && !selectedTrend) {
      setErrorMessage("Please fetch trends first before generating scripts.");
      const timer = setTimeout(() => {
        navigate('/trends');
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [trends.length, selectedTrend, navigate, setErrorMessage]);

  const handleGenerate = async (event) => {
    event.preventDefault();
    const trendToUse = selectedTrend || fallbackTrend;
    if (!trendToUse) {
      setErrorMessage("Pick a trend first in the Trends tab.");
      return;
    }
    if (!vibe.trim()) {
      setErrorMessage("Describe your vibe so Nexus can match your voice.");
      return;
    }

    setIsBusy(true);
    setErrorMessage("");

    try {
      const { data } = await generateScript({ trend: trendToUse, vibe });
      setScriptResult(data);
    } catch (error) {
      console.error("Script generation failed", error);
      const detail = error.response?.data?.detail;
      setErrorMessage(detail || "Unable to generate script. Check the backend log.");
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <section className="card">
      <header className="card__header">
        <h2>agent_quill: Creative Engine</h2>
        <p>Your AI writer crafting scripts, hooks, and captions in your unique voice.</p>
      </header>

      <form onSubmit={handleGenerate} className="field-grid" style={{ marginTop: "1.5rem" }}>
        <div className="field-group">
          <label htmlFor="trend-select">Trend signal</label>
          <select
            id="trend-select"
            value={selectedTrend ? selectedTrend.title : fallbackTrend?.title || ""}
            onChange={(event) => {
              const next = trends.find((trend) => trend.title === event.target.value);
              setSelectedTrend(next || null);
            }}
          >
            <option value="" disabled>
              {trends.length ? "Choose a trend" : "Load trends first"}
            </option>
            {trends.map((trend) => (
              <option key={trend.title} value={trend.title}>
                {trend.title}
              </option>
            ))}
          </select>
        </div>

        <AIInput
          id="vibe"
          label="Creator vibe"
          value={vibe}
          onChange={(event) => setVibe(event.target.value)}
          placeholder=""
          suggestions={VIBE_SUGGESTIONS}
        />

        <div className="field-group" style={{ alignSelf: "end" }}>
          <ButtonArrowDown type="submit" disabled={isBusy || !vibe.trim()}>
            {isBusy ? "Generating" : "Generate playbook"}
          </ButtonArrowDown>
        </div>
      </form>

      {isBusy ? <DotLoader label="quill agent drafting your script" /> : null}

      {scriptResult?.script ? (
        <div className="field-group" style={{ marginTop: "2rem" }}>
          <label>Script output</label>
          <textarea
            className="script-output"
            value={scriptResult.script}
            readOnly
          />
        </div>
      ) : null}

      {scriptResult?.sponsors?.length ? (
        <div style={{ marginTop: "2rem" }}>
          <h3>Partner radar</h3>
          <div className="grid" style={{ marginTop: "1rem" }}>
            {scriptResult.sponsors.map((sponsor) => (
              <article key={sponsor.name} className="trend-card">
                <header className="trend-card__header">
                  <MessageCircleHeart size={18} aria-hidden="true" />
                  <strong>{sponsor.name}</strong>
                </header>
                <p>{sponsor.category}</p>
                <p>Email: {sponsor.email}</p>
                <details>
                  <summary>Email template</summary>
                  <pre style={{ whiteSpace: "pre-wrap" }}>{sponsor.emailTemplate}</pre>
                </details>
              </article>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}
