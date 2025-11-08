import { NavLink } from "react-router-dom";
import { PenTool, Clapperboard } from "lucide-react";
import { useAppContext } from "../context/AppContext.jsx";
import ExpandableTabs from "./ui/ExpandableTabs.jsx";

const navLinks = [
  { to: "/", label: "Dashboard" },
  { to: "/trends", label: "Trends" },
  { to: "/analytics", label: "Analytics" }
];

const workflowTabs = [
  {
    to: "/script",
    label: "Script Generation",
    description: "Draft hooks, captions & sponsor copy",
    icon: PenTool
  },
  {
    to: "/upload",
    label: "Video Processing",
    description: "Clip, prep & launch shorts",
    icon: Clapperboard
  }
];

function StatusIndicator() {
  const { backendStatus } = useAppContext();
  const isOnline = backendStatus?.status === "healthy";
  const label = isOnline ? "Backend online" : "Backend offline";

  return (
    <span
      className={`status-indicator ${isOnline ? "online" : "offline"}`}
      title={label}
    >
      ●
    </span>
  );
}

export default function NavBar() {
  return (
    <header className="nav-shell">
      <div className="brand">
        <span className="brand-symbol">⚡</span>
        <span className="brand-name">Nexus Studio</span>
        <StatusIndicator />
      </div>
      <nav className="nav-links">
        {navLinks.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
      <ExpandableTabs tabs={workflowTabs} />
    </header>
  );
}
