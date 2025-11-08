export default function DotLoader({ label = "Loading" }) {
  return (
    <div className="dot-loader" role="status" aria-live="polite">
      <span className="dot" aria-hidden="true" />
      <span className="dot" aria-hidden="true" />
      <span className="dot" aria-hidden="true" />
      <span className="dot-loader__label">{label}</span>
    </div>
  );
}
