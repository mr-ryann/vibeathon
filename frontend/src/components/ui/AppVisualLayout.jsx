import BouncingBalls from "./BouncingBalls.jsx";

export default function AppVisualLayout({ hero, children }) {
  return (
    <section className="app-visual">
      <div className="app-visual__hero">
        <div className="app-visual__overlay" />
        <BouncingBalls />
        <div className="app-visual__content">{hero}</div>
      </div>
      <div className="app-visual__body">{children}</div>
    </section>
  );
}
