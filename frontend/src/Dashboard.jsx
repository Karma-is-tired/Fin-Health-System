import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle, DownloadCloud, Loader2, Sparkles, TrendingDown, TrendingUp, UploadCloud, Wallet,
} from 'lucide-react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { apiJson, bandOf, downloadFile, money, monthLabel } from './api';

const TONES = {
  emerald: 'bg-emerald-400/10 text-emerald-300',
  sky: 'bg-sky-400/10 text-sky-300',
  brand: 'bg-brand/10 text-brand',
  rose: 'bg-rose-400/10 text-rose-300',
};

const FACTOR_NAMES = {
  profitability: 'Profitability',
  cash_flow: 'Cash flow',
  expense_control: 'Expense control',
  receivables: 'Receivables',
  budget: 'Budget adherence',
};

const BAND_COLOURS = {
  Strong: { text: 'text-emerald-300', bar: 'bg-emerald-400', stroke: '#34d399' },
  Moderate: { text: 'text-brand', bar: 'bg-brand', stroke: '#ffb800' },
  Weak: { text: 'text-rose-300', bar: 'bg-rose-400', stroke: '#fb7185' },
};

function ScoreRing({ score, band }) {
  const radius = 74;
  const circumference = 2 * Math.PI * radius;
  const colours = BAND_COLOURS[band] || { stroke: '#334155', text: 'text-slate-400' };
  const offset = circumference * (1 - Math.min(score, 100) / 100);

  return (
    <div className="relative flex h-48 w-48 shrink-0 items-center justify-center">
      <svg viewBox="0 0 180 180" className="absolute inset-0 -rotate-90">
        <circle cx="90" cy="90" r={radius} fill="none" stroke="#1a2342" strokeWidth="14" />
        {band && (
          <circle
            cx="90" cy="90" r={radius} fill="none" stroke={colours.stroke} strokeWidth="14"
            strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset}
          />
        )}
      </svg>
      <div className="text-center">
        <p className="text-5xl font-extrabold text-white">{band ? score : '—'}</p>
        <p className="text-xs font-semibold text-slate-400">out of 100</p>
        <p className={`mt-1 text-sm font-extrabold ${colours.text}`}>{band || 'No data yet'}</p>
      </div>
    </div>
  );
}

function StatCard({ index, label, value, note, noteTone, icon: Icon, tone }) {
  return (
    <div className="card relative overflow-hidden p-5">
      <span className="absolute right-4 top-4 text-[10px] font-extrabold tracking-widest text-slate-600">
        {String(index).padStart(2, '0')}
      </span>
      <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${TONES[tone]}`}>
        <Icon size={20} />
      </div>
      <p className="mt-5 text-2xl font-extrabold text-white sm:text-3xl">{value}</p>
      <p className="mt-1 text-sm font-semibold text-slate-300">{label}</p>
      <p className={`mt-1 text-xs ${noteTone}`}>{note}</p>
    </div>
  );
}

function changeNote(pct, goodWhenUp) {
  if (pct === null || pct === undefined) return { text: 'No earlier month to compare', tone: 'text-slate-500' };
  const good = goodWhenUp ? pct >= 0 : pct <= 0;
  return { text: `${pct > 0 ? '+' : ''}${pct}% vs last month`, tone: good ? 'text-emerald-300' : 'text-rose-300' };
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState('');

  const load = useCallback(async () => {
    try {
      const [score, summary, trend] = await Promise.all([
        apiJson('/health-score'), apiJson('/financial-summary'), apiJson('/monthly-trend'),
      ]);
      setData({ score, summary, trend });
      setError('');
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const run = async (name, task) => {
    setBusy(name);
    try {
      await task();
    } catch (err) {
      setError(err.message);
    }
    setBusy('');
  };

  const downloadReport = () =>
    run('report', () => downloadFile('/download-report', `FinHealth_${data.summary.latest_month}.docx`));
  const loadSample = () =>
    run('sample', async () => {
      await apiJson('/load-demo-data', { method: 'POST' });
      await load();
    });

  if (error && !data) {
    return (
      <div className="card p-8 text-center">
        <AlertCircle className="mx-auto mb-3 text-rose-300" size={32} />
        <p className="text-slate-300">{error}</p>
        <button onClick={load} className="btn-primary mt-5">Try again</button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6" aria-busy="true">
        <div className="card h-64 animate-pulse" />
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[0, 1, 2, 3].map((i) => <div key={i} className="card h-36 animate-pulse" />)}
        </div>
      </div>
    );
  }

  const { score, summary, trend } = data;
  const hasData = summary.has_data;
  const band = hasData ? bandOf(score.overall) : null;
  const revenueNote = changeNote(summary.revenue_change_pct, true);
  const expenseNote = changeNote(summary.expense_change_pct, false);
  const profitable = summary.net_profit >= 0;
  const chartData = trend.map((row) => ({ ...row, label: monthLabel(row.month) }));

  return (
    <div className="space-y-6">
      {error && (
        <p role="alert" className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          {error}
        </p>
      )}

      <section className="card relative overflow-hidden p-6 sm:p-10">
        <div className="pointer-events-none absolute -right-20 -top-20 h-72 w-72 rounded-full bg-brand/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 left-1/3 h-64 w-64 rounded-full bg-sky-500/10 blur-3xl" />
        <div className="relative flex flex-col items-start justify-between gap-8 md:flex-row md:items-center">
          <div className="max-w-xl">
            <p className="eyebrow">Financial health</p>
            <h1 className="mt-3 text-3xl font-extrabold leading-tight text-white sm:text-5xl">
              Know exactly where your money stands
            </h1>
            <p className="mt-4 text-slate-400">
              {hasData
                ? `Your latest period is ${summary.latest_month}. Upload fresh data any time to update your score.`
                : 'Upload your transactions to see your health score, cash-flow trend and risk alerts.'}
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link to="/upload" className="btn-primary"><UploadCloud size={18} />Upload data</Link>
              <button onClick={downloadReport} disabled={!hasData || busy === 'report'} className="btn-ghost">
                {busy === 'report' ? <Loader2 size={18} className="animate-spin" /> : <DownloadCloud size={18} className="text-brand" />}
                {busy === 'report' ? 'Generating…' : 'Download report'}
              </button>
            </div>
          </div>
          <ScoreRing score={score.overall} band={band} />
        </div>
      </section>

      {!hasData ? (
        <section className="card p-8 text-center">
          <Sparkles className="mx-auto mb-3 text-brand" size={32} />
          <h2 className="text-xl font-extrabold text-white">Nothing to show yet</h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-slate-400">
            Upload a CSV or Excel file of your transactions, or explore the dashboard with sample data first.
          </p>
          <div className="mt-5 flex flex-wrap justify-center gap-3">
            <Link to="/upload" className="btn-primary">Upload my data</Link>
            <button onClick={loadSample} disabled={busy === 'sample'} className="btn-ghost">
              {busy === 'sample' ? <Loader2 size={18} className="animate-spin" /> : <Sparkles size={18} className="text-brand" />}
              Try sample data
            </button>
          </div>
        </section>
      ) : (
        <>
          <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard index={1} label="Revenue" value={money(summary.revenue)} note={revenueNote.text} noteTone={revenueNote.tone} icon={TrendingUp} tone="emerald" />
            <StatCard index={2} label="Expenses" value={money(summary.expenses)} note={expenseNote.text} noteTone={expenseNote.tone} icon={Wallet} tone="sky" />
            <StatCard index={3} label="Net profit" value={money(summary.net_profit)} note={profitable ? 'You are in the green' : 'Spending exceeds income'} noteTone={profitable ? 'text-emerald-300' : 'text-rose-300'} icon={profitable ? TrendingUp : TrendingDown} tone={profitable ? 'brand' : 'rose'} />
            <StatCard index={4} label="Overdue invoices" value={money(summary.overdue_receivables)} note={summary.overdue_receivables > 0 ? 'Follow these up' : 'Nothing overdue'} noteTone={summary.overdue_receivables > 0 ? 'text-rose-300' : 'text-emerald-300'} icon={AlertCircle} tone="rose" />
          </section>

          <section className="grid gap-6 lg:grid-cols-5">
            <div className="card p-6 lg:col-span-3">
              <p className="eyebrow">Cash flow</p>
              <h2 className="mt-1 text-xl font-extrabold text-white">Income vs expenses</h2>
              <div className="mt-6 h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} barGap={4}>
                    <CartesianGrid stroke="#1a2342" vertical={false} />
                    <XAxis dataKey="label" stroke="#64748b" tickLine={false} axisLine={false} fontSize={12} />
                    <YAxis stroke="#64748b" tickLine={false} axisLine={false} fontSize={12} width={48}
                      tickFormatter={(v) => new Intl.NumberFormat('en', { notation: 'compact' }).format(v)} />
                    <Tooltip
                      cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                      formatter={(value) => money(value)}
                      contentStyle={{ background: '#0a1124', border: '1px solid #1a2342', borderRadius: 12, color: '#fff' }}
                      labelStyle={{ color: '#94a3b8' }}
                    />
                    <Bar dataKey="income" name="Income" fill="#ffb800" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="expense" name="Expenses" fill="#38bdf8" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-3 flex gap-5 text-xs text-slate-400">
                <span className="flex items-center gap-2"><i className="h-2.5 w-2.5 rounded-full bg-brand" />Income</span>
                <span className="flex items-center gap-2"><i className="h-2.5 w-2.5 rounded-full bg-sky-400" />Expenses</span>
              </div>
            </div>

            <div className="card p-6 lg:col-span-2">
              <p className="eyebrow">Score breakdown</p>
              <h2 className="mt-1 text-xl font-extrabold text-white">What drives your score</h2>
              <div className="mt-6 space-y-5">
                {Object.entries(score.scores).map(([factor, value]) => {
                  const colours = BAND_COLOURS[bandOf(value)];
                  return (
                    <div key={factor}>
                      <div className="mb-2 flex items-center justify-between text-sm">
                        <span className="font-semibold text-slate-200">{FACTOR_NAMES[factor] || factor}</span>
                        <span className={`font-extrabold ${colours.text}`}>{value}</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-line">
                        <div className={`h-full rounded-full ${colours.bar}`} style={{ width: `${value}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
              <p className="mt-6 text-xs text-slate-500">
                Scores appear as soon as there is enough data. Add invoices and a budget on the upload page to unlock all five.
              </p>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
