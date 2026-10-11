import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, Clock, DownloadCloud, FileText, Loader2 } from 'lucide-react';
import { apiJson, bandOf, downloadFile } from './api';

const SCORE_TEXT = { Strong: 'text-emerald-300', Moderate: 'text-brand', Weak: 'text-rose-300' };

// SQLite stores UTC times without a timezone marker.
const formatDate = (stamp) =>
  new Date(`${String(stamp).replace(' ', 'T')}Z`).toLocaleDateString(undefined, {
    day: 'numeric', month: 'short', year: 'numeric',
  });

export default function History() {
  const [reports, setReports] = useState(null);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(null);

  useEffect(() => {
    apiJson('/history').then(setReports).catch((err) => setError(err.message));
  }, []);

  const download = async (report) => {
    setDownloading(report.id);
    setError('');
    try {
      await downloadFile(`/download-past-report/${report.id}`, `FinHealth_Archive_${report.report_month}.docx`);
    } catch (err) {
      setError(err.message);
    }
    setDownloading(null);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <p className="eyebrow">Reports</p>
        <h1 className="mt-2 text-3xl font-extrabold text-white">Report history</h1>
        <p className="mt-2 text-slate-400">Every report you generate is saved here so you can download it again.</p>
      </div>

      {error && (
        <p role="alert" className="flex items-center gap-2 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          <AlertCircle size={16} />{error}
        </p>
      )}

      <div className="card overflow-hidden">
        {reports === null && !error ? (
          <div className="space-y-3 p-6" aria-busy="true">
            {[0, 1, 2].map((i) => <div key={i} className="h-12 animate-pulse rounded-xl bg-line" />)}
          </div>
        ) : reports && reports.length === 0 ? (
          <div className="p-10 text-center">
            <FileText className="mx-auto mb-3 text-slate-500" size={32} />
            <p className="text-slate-400">No reports yet. Open the dashboard and choose Download report.</p>
            <Link to="/dashboard" className="btn-primary mt-5">Go to dashboard</Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] text-left">
              <thead className="bg-ink text-xs uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="p-4 font-bold">Generated</th>
                  <th className="p-4 font-bold">Period</th>
                  <th className="p-4 font-bold">Score</th>
                  <th className="p-4 text-right font-bold">Report</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {(reports || []).map((report) => (
                  <tr key={report.id} className="transition hover:bg-ink/60">
                    <td className="p-4 text-slate-300">
                      <span className="flex items-center gap-2"><Clock size={15} className="text-slate-500" />{formatDate(report.created_at)}</span>
                    </td>
                    <td className="p-4 font-bold text-white">{report.report_month}</td>
                    <td className={`p-4 font-extrabold ${SCORE_TEXT[bandOf(report.overall_score)]}`}>{report.overall_score}</td>
                    <td className="p-4 text-right">
                      <button onClick={() => download(report)} disabled={downloading === report.id} className="btn-ghost !px-4 !py-2">
                        {downloading === report.id ? <Loader2 size={16} className="animate-spin" /> : <DownloadCloud size={16} className="text-brand" />}
                        Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
