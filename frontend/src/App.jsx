import { useEffect, useState } from "react";

const API_BASE = "https://fin-health-system.onrender.com";
const API_KEY = "dev-secret-key-change-later";

function App() {
  const [healthScore, setHealthScore] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/health-score`, { headers: { "X-API-Key": API_KEY } })
      .then((res) => res.json())
      .then(setHealthScore)
      .catch(() => setError("Could not reach the API. Is main.py running?"));

    fetch(`${API_BASE}/financial-summary`, { headers: { "X-API-Key": API_KEY } })
      .then((res) => res.json())
      .then(setSummary)
      .catch(() => setError("Could not reach the API. Is main.py running?"));
  }, []);

  if (error) {
    return <div style={{ padding: 40, fontFamily: "sans-serif", color: "#A23B2E" }}>{error}</div>;
  }

  if (!healthScore || !summary) {
    return <div style={{ padding: 40, fontFamily: "sans-serif" }}>Loading...</div>;
  }

  const cardStyle = {
    border: "1px solid #DCDED4",
    borderRadius: 6,
    padding: 16,
    flex: 1,
  };
  
  const labelStyle = { 
    fontSize: 12,
    color: "#5D7A6B",
    textTransform: "uppercase"
  };
  
  const numberStyle = { 
    fontSize: 24,
    fontWeight: "bold",
    color: "#12201C"
  };

  return (
    <div style={{ fontFamily: "sans-serif", padding: 40, maxWidth: 900, margin: "0 auto" }}>
      <h1>Financial Health & Cash-Flow System</h1>
      <p style={{ color: "#5D7A6B" }}>Latest period: {summary.latest_month}</p>

      <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
        <div style={{ ...cardStyle, flex: "0 0 160px", textAlign: "center" }}>
          <div style={{ fontSize: 36, fontWeight: "bold" }}>{healthScore.overall}</div>
          <div style={labelStyle}>/ 100 Health Score</div>
        </div>
        
        <div style={cardStyle}>
          <div style={labelStyle}>Revenue</div>
          <div style={numberStyle}>{summary.revenue.toLocaleString()}</div>
        </div>
        
        <div style={cardStyle}>
          <div style={labelStyle}>Net Profit</div>
          <div style={numberStyle}>{summary.net_profit.toLocaleString()}</div>
        </div>
        
        <div style={cardStyle}>
          <div style={labelStyle}>Overdue A/R</div>
          <div style={{ ...numberStyle, color: "#A23B2E" }}>{summary.overdue_receivables.toLocaleString()}</div>
        </div>
      </div>

      <h3>Score breakdown</h3>
      <ul>
        {Object.entries(healthScore.scores).map(([factor, score]) => (
          <li key={factor}>{factor}: {score} / 100</li>
        ))}
      </ul>
    </div>
  );
}

export default App;