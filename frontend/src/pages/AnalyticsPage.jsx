import { useEffect, useState } from "react";
import { getAnalytics } from "../services/api.js";
import { useAppContext } from "../context/AppContext.jsx";
import DotLoader from "../components/ui/DotLoader.jsx";

export default function AnalyticsPage() {
  const { setErrorMessage, setIsBusy, isBusy } = useAppContext();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    let isMounted = true;
    setIsBusy(true);
    getAnalytics()
      .then((response) => {
        if (isMounted) {
          setStats(response.data);
          setErrorMessage("");
        }
      })
      .catch((error) => {
        console.error("Analytics fetch failed", error);
        const detail = error.response?.data?.detail;
        setErrorMessage(detail || "Analytics endpoint unavailable.");
      })
      .finally(() => {
        if (isMounted) {
          setIsBusy(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [setErrorMessage, setIsBusy]);

  return (
    <section className="card">
      <header className="card__header">
        <h2>SignalPulse: Performance Loop</h2>
        <p>Review how Nexus experiments landed so you can feed insights back into tomorrow’s drops.</p>
      </header>

      {isBusy && !stats ? <DotLoader label="Pulling performance metrics" /> : null}

      {stats ? (
        <div style={{ marginTop: "2rem" }}>
          <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
            <article className="trend-card">
              <strong>Total views</strong>
              <p>{stats.totalViews}</p>
            </article>
            <article className="trend-card">
              <strong>Total likes</strong>
              <p>{stats.totalLikes}</p>
            </article>
            <article className="trend-card">
              <strong>Total comments</strong>
              <p>{stats.totalComments}</p>
            </article>
            <article className="trend-card">
              <strong>Engagement rate</strong>
              <p>{stats.engagementRate}%</p>
            </article>
          </div>

          {stats.topPerforming?.length ? (
            <div style={{ marginTop: "2rem" }}>
              <h3>Top performing videos</h3>
              <div className="grid">
                {stats.topPerforming.map((item) => (
                  <article key={item.id} className="trend-card">
                    <strong>{item.title}</strong>
                    <p>Views: {item.views}</p>
                    <p>Likes: {item.likes}</p>
                  </article>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
