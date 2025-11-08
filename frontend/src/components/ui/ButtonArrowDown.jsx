import { ArrowDown } from "lucide-react";

export default function ButtonArrowDown({ children, variant = "primary", ...props }) {
  return (
    <button
      type="button"
      className={variant === "secondary" ? "button button--secondary" : "button"}
      {...props}
    >
      <span>{children}</span>
      <ArrowDown size={16} aria-hidden="true" />
    </button>
  );
}
