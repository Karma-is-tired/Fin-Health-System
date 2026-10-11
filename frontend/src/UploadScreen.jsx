import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, DownloadCloud, Loader2, UploadCloud } from 'lucide-react';
import { apiFetch } from './api';

const KINDS = {
  transactions: {
    label: 'Transactions',
    blurb: 'Your income and expenses, one row per transaction.',
    columns: ['date', 'amount', 'type (income or expense)', 'category', 'description'],
    template:
      'date,amount,type,category,description\n2026-06-02,250000,income,Product Sales,Shop sales\n2026-06-01,450000,expense,Rent,Shop rent\n',
  },
  invoices: {
    label: 'Invoices',
    blurb: 'Money your customers owe you, paid or not.',
    columns: ['customer', 'amount', 'due_date', 'status (paid or unpaid)'],
    template:
      'customer,amount,due_date,status\nAdebayo Stores,380000,2026-06-20,paid\nLagos Eats Ltd,540000,2026-06-28,unpaid\n',
  },
  budgets: {
    label: 'Budgets',
    blurb: 'What you planned to spend per category. Use the same month as your latest transactions.',
    columns: ['category', 'period (YYYY-MM)', 'budgeted_amount'],
    template: 'category,period,budgeted_amount\nRent,2026-06,450000\nMarketing,2026-06,120000\n',
  },
};

export default function UploadScreen() {
  const [kind, setKind] = useState('transactions');
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null); // { ok, text }
  const current = KINDS[kind];

  const pick = (next) => {
    setKind(next);
    setFile(null);
    setResult(null);
  };

  const accept = (candidate) => {
    if (!candidate) return;
    setFile(candidate);
    setResult(null);
  };

  const downloadTemplate = () => {
    const url = window.URL.createObjectURL(new Blob([current.template], { type: 'text/csv' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `${kind}_template.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  const upload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setResult(null);
    try {
      const body = new FormData();
      body.append('file', file);
      const res = await apiFetch(`/upload/${kind}`, { method: 'POST', body });
      const data = await res.json().catch(() => ({}));
      if (res.ok) {
        setResult({ ok: true, text: data.message });
        setFile(null);
      } else {
        setResult({ ok: false, text: typeof data.detail === 'string' ? data.detail : 'Upload failed.' });
      }
    } catch (err) {
      setResult({ ok: false, text: err.message });
    }
    setBusy(false);
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="eyebrow">Your data</p>
        <h1 className="mt-2 text-3xl font-extrabold text-white">Upload data</h1>
        <p className="mt-2 text-slate-400">Add a CSV or Excel file. Your dashboard updates straight away.</p>
      </div>

      <div className="grid grid-cols-3 gap-2 rounded-2xl border border-line bg-panel p-2">
        {Object.entries(KINDS).map(([key, item]) => (
          <button
            key={key}
            onClick={() => pick(key)}
            className={`rounded-xl px-3 py-3 text-sm font-bold transition ${
              kind === key ? 'bg-brand text-slate-900' : 'text-slate-300 hover:bg-card hover:text-white'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      <form onSubmit={upload} className="card space-y-5 p-6 sm:p-8">
        <div>
          <p className="font-bold text-white">{current.blurb}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {current.columns.map((column) => (
              <span key={column} className="rounded-lg border border-line bg-ink px-2.5 py-1 text-xs font-semibold text-slate-300">
                {column}
              </span>
            ))}
          </div>
          <button type="button" onClick={downloadTemplate} className="mt-4 inline-flex items-center gap-2 text-sm font-bold text-brand hover:underline">
            <DownloadCloud size={16} />
            Download template
          </button>
        </div>

        <label
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); accept(e.dataTransfer.files[0]); }}
          className={`flex cursor-pointer flex-col items-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition ${
            dragging ? 'border-brand bg-brand/5' : 'border-line hover:border-slate-600'
          }`}
        >
          <UploadCloud size={40} className="text-brand" />
          <p className="mt-3 font-bold text-white">{file ? file.name : 'Drop your file here, or tap to choose'}</p>
          <p className="mt-1 text-xs text-slate-500">.csv or .xlsx, up to 5 MB</p>
          <input type="file" accept=".csv,.xlsx" className="sr-only" onChange={(e) => accept(e.target.files[0])} />
        </label>

        <button type="submit" disabled={!file || busy} className="btn-primary w-full">
          {busy && <Loader2 size={18} className="animate-spin" />}
          {busy ? 'Processing…' : `Process ${current.label.toLowerCase()}`}
        </button>

        {result && (
          <div
            role="status"
            className={`rounded-xl border px-4 py-3 text-sm ${
              result.ok
                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
                : 'border-rose-500/30 bg-rose-500/10 text-rose-300'
            }`}
          >
            <p>{result.text}</p>
            {result.ok && (
              <Link to="/dashboard" className="mt-2 inline-flex items-center gap-1 font-bold text-white">
                View dashboard <ArrowRight size={14} />
              </Link>
            )}
          </div>
        )}
      </form>
    </div>
  );
}
