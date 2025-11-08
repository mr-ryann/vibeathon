import { createContext, useContext, useMemo, useState } from "react";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [trends, setTrends] = useState([]);
  const [selectedTrend, setSelectedTrend] = useState(null);
  const [scriptResult, setScriptResult] = useState(null);
  const [backendStatus, setBackendStatus] = useState(null);
  const [isBusy, setIsBusy] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const value = useMemo(
    () => ({
      trends,
      setTrends,
      selectedTrend,
      setSelectedTrend,
      scriptResult,
      setScriptResult,
      backendStatus,
      setBackendStatus,
      isBusy,
      setIsBusy,
      errorMessage,
      setErrorMessage
    }),
    [
      trends,
      selectedTrend,
      scriptResult,
      backendStatus,
      isBusy,
      errorMessage
    ]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppContext must be used within an AppProvider");
  }
  return context;
}
