import { useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function ExpandableTabs({ tabs }) {
  const location = useLocation();
  const navigate = useNavigate();

  const activeIndex = useMemo(() => {
    const index = tabs.findIndex((tab) => location.pathname.startsWith(tab.to));
    return index === -1 ? 0 : index;
  }, [location.pathname, tabs]);

  return (
    <div className="expandable-tabs" role="tablist">
      {tabs.map((tab, index) => {
        const isActive = index === activeIndex;
        const Icon = tab.icon;
        return (
          <button
            key={tab.to}
            type="button"
            role="tab"
            aria-selected={isActive}
            className={isActive ? "expandable-tab active" : "expandable-tab"}
            onClick={() => navigate(tab.to)}
          >
            <span className="expandable-tab__icon" aria-hidden="true">
              <Icon size={18} />
            </span>
            <span className="expandable-tab__label">{tab.label}</span>
            <span className="expandable-tab__meta">{tab.description}</span>
          </button>
        );
      })}
    </div>
  );
}
