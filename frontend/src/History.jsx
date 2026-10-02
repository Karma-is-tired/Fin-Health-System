import { useEffect, useState } from 'react';
import { DownloadCloud, Clock } from 'lucide-react';

const API_BASE = "https://fin-health-system.onrender.com";

export default function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/history`, {
      headers: { "Authorization": `Bearer ${localStorage.getItem('token')}` }
    })
    .then(res => res.json())
    .then(setHistory);
  }, []);

  const downloadPastReport = async (id, month) => {
    const res = await fetch(`${API_BASE}/download-past-report/${id}`, {
      headers: { "Authorization": `Bearer ${localStorage.getItem('token')}` }
    });
    if (!res.ok) return alert("Failed to download archive");
    
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `FinHealth_Archive_${month}.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-2">Report History</h1>
      <p className="text-slate-400 mb-8">Access and download previously generated financial analysis documents.</p>

      <div className="bg-cardBg border border-slate-700 rounded-xl overflow-hidden">
        {history.length === 0 ? (
          <div className="p-8 text-center text-slate-400">No reports generated yet. Go to the Dashboard and click Download Report.</div>
        ) : (
          <table className="w-full text-left">
            <thead className="bg-[#0b1120] text-slate-400 text-sm uppercase tracking-wider">
              <tr>
                <th className="p-4">Date Generated</th>
                <th className="p-4">Analysis Month</th>
                <th className="p-4">Score</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {history.map((report) => (
                <tr key={report.id} className="hover:bg-slate-800 transition-colors">
                  <td className="p-4 text-slate-300 flex items-center gap-2">
                    <Clock size={16} className="text-slate-500" />
                    {new Date(report.created_at).toLocaleDateString()}
                  </td>
                  <td className="p-4 font-medium text-white">{report.report_month}</td>
                  <td className="p-4 text-accentYellow font-bold">{report.overall_score}</td>
                  <td className="p-4 text-right">
                    <button 
                      onClick={() => downloadPastReport(report.id, report.report_month)}
                      className="text-sm bg-slate-700 hover:bg-accentYellow hover:text-black text-white py-2 px-4 rounded-lg transition-colors flex items-center gap-2 ml-auto"
                    >
                      <DownloadCloud size={16} /> Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}