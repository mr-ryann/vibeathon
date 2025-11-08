import { useEffect } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { AppProvider, useAppContext } from "./context/AppContext.jsx";
import NavBar from "./components/NavBar.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import TrendsPage from "./pages/TrendsPage.jsx";
import ScriptPage from "./pages/ScriptPage.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import AnalyticsPage from "./pages/AnalyticsPage.jsx";
import { getHealth } from "./services/api.js";
import "./styles/app.css";

function AppContent() {
  const { setBackendStatus, setErrorMessage, errorMessage } = useAppContext();

  useEffect(() => {
    getHealth()
      .then((response) => setBackendStatus(response.data))
      .catch((error) => {
        console.error("Health check failed", error);
        setBackendStatus(null);
        setErrorMessage("Nexus backend is unreachable. Check the FastAPI server.");
      });
  }, [setBackendStatus, setErrorMessage]);

  return (
    <div className="app-shell">
      <NavBar />
      {errorMessage ? <div className="banner error">{errorMessage}</div> : null}
      <main className="page-shell">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/trends" element={<TrendsPage />} />
          <Route path="/script" element={<ScriptPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="footer">
        <p>Powered by Nexus • Creators ship daily here</p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}
