import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, DollarSign, AlertCircle, DownloadCloud } from 'lucide-react';

const API_BASE = "https://fin-health-system.onrender.com"; // Ensure this is your live URL
const API_KEY = "dev-secret-key-change-later";

export default function Dashboard() {
  const [healthScore, setHealthScore] = useState(null);
  const [summary, setSummary] = useState(null);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/health-score`, { headers: { "X-API-Key": API_KEY } })
      .then(res => res.json())
      .then(setHealthScore);

    fetch(`${API_BASE}/financial-summary`, { headers: { "X-API-Key": API_KEY } })
      .then(res => res.json())
      .then(setSummary);
  }, []);

  const handleDownloadReport = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch(`${API_BASE}/download-report`, {
        headers: { "X-API-Key": API_KEY }
      });
      
      if (!response.ok) throw new Error("Download failed");
      
      // Magic trick to download a file securely through React
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Executive_Report_${summary.latest_month}.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      alert("Failed to generate report.");
    }
    setIsDownloading(false);
  };

  if (!healthScore || !summary) return <div className="text-accentYellow">Loading analytics...</div>;

  return (
    <div>
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Financial Dashboard</h1>
          <p className="text-slate-400 mt-1">System Architecture Overview — Latest period: {summary.latest_month}</p>
        </div>
        <div className="flex items-center gap-6">
          <button 
            onClick={handleDownloadReport}
            disabled={isDownloading}
            className="flex items-center gap-2 bg-slate-800 text-white px-4 py-3 rounded-lg hover:bg-slate-700 transition-colors border border-slate-600 font-medium disabled:opacity-50"
          >
            <DownloadCloud size={20} className="text-accentYellow" />
            {isDownloading ? "Generating..." : "Download Report"}
          </button>
          
          <div className="text-right bg-cardBg px-6 py-3 rounded-lg border border-slate-700">
            <p className="text-sm text-slate-400 uppercase tracking-wider">Health Score</p>
            <p className="text-4xl font-bold text-accentYellow">{healthScore.overall} <span className="text-lg text-slate-500">/ 100</span></p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <MetricCard title="Total Revenue" amount={summary.revenue} icon={<TrendingUp size={24} className="text-green-400"/>} />
        <MetricCard title="Net Profit" amount={summary.net_profit} icon={summary.net_profit < 0 ? <TrendingDown size={24} className="text-red-400"/> : <TrendingUp size={24} className="text-green-400"/>} />
        <MetricCard title="Overdue A/R" amount={summary.overdue_receivables} icon={<AlertCircle size={24} className="text-red-400"/>} isAlert={summary.overdue_receivables > 0} />
      </div>

      <div className="bg-cardBg border border-slate-700 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-6">Algorithm Breakdown</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(healthScore.scores).map(([factor, score]) => (
            <div key={factor} className="bg-[#0b1120] p-4 rounded-lg border border-slate-800 flex justify-between items-center">
              <span className="text-slate-300 capitalize">{factor.replace('_', ' ')}</span>
              <span className="text-accentYellow font-bold">{score} / 100</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, amount, icon, isAlert }) {
  return (
    <div className={`bg-cardBg p-6 rounded-xl border ${isAlert ? 'border-red-500/50' : 'border-slate-700'}`}>
      <div className="flex justify-between items-start mb-4">
        <p className="text-slate-400 font-medium">{title}</p>
        <div className="p-2 bg-[#0b1120] rounded-lg">{icon}</div>
      </div>
      <p className={`text-3xl font-bold ${isAlert ? 'text-red-400' : 'text-white'}`}>
        ${amount.toLocaleString()}
      </p>
    </div>
  );
}