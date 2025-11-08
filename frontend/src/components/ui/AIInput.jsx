import { useMemo } from "react";
import { Sparkles } from "lucide-react";

export default function AIInput({
  label,
  value,
  onChange,
  placeholder,
  suggestions = [],
  id,
  type = "text",
  disabled = false
}) {
  const suggestionText = useMemo(() => suggestions.join(" · "), [suggestions]);

  return (
    <label className={"ai-input" + (disabled ? " disabled" : "")}
      htmlFor={id}
    >
      <span className="ai-input__label">
        <Sparkles size={16} aria-hidden="true" />
        {label}
      </span>
      <div className="ai-input__field">
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
        />
        {suggestionText ? (
          <span className="ai-input__suggestions">{suggestionText}</span>
        ) : null}
      </div>
    </label>
  );
}
