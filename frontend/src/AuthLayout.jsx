import { useEffect, useState } from 'react';
import { Activity } from 'lucide-react';

export function Brand({ compact = false }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-orange-400 text-slate-900 shadow-lg shadow-brand/20">
        <Activity size={22} strokeWidth={2.5} />
      </div>
      <div className="leading-tight">
        <p className="font-extrabold text-white">FinHealth</p>
        {!compact && <p className="text-xs font-medium text-brand">Cash-flow intelligence</p>}
      </div>
    </div>
  );
}

// True once something has been loading for a while (a sleeping free server can take a minute).
export function useSlowHint(active, delay = 6000) {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    if (!active) return undefined;
    const timer = setTimeout(() => setSlow(true), delay);
    return () => {
      clearTimeout(timer);
      setSlow(false);
    };
  }, [active, delay]);
  return slow;
}

function LockIllustration() {
  return (
    <div className="relative mx-auto h-[420px] w-full max-w-md">
      <div className="absolute -left-6 bottom-0 h-56 w-56 rounded-full bg-sky-500/10" />
      <div className="absolute right-0 top-0 h-44 w-44 rounded-full bg-brand/10" />
      <div className="absolute inset-x-6 bottom-10 top-10 rounded-[2rem] border border-line bg-card p-5 shadow-2xl">
        <div className="flex items-center gap-3 rounded-xl bg-ink px-4 py-3">
          <span className="h-3 w-3 rounded-full bg-brand" />
          <span className="h-2 w-28 rounded bg-slate-600" />
        </div>
        <div className="mt-4 flex h-[250px] items-center justify-center rounded-2xl bg-ink">
          <svg viewBox="0 0 120 140" className="h-44 w-44" aria-hidden="true">
            <defs>
              <linearGradient id="lockGradient" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stopColor="#ffb800" />
                <stop offset="1" stopColor="#38bdf8" />
              </linearGradient>
            </defs>
            <path d="M32 62V44a28 28 0 0 1 56 0v18" fill="none" stroke="url(#lockGradient)" strokeWidth="12" strokeLinecap="round" />
            <rect x="14" y="58" width="92" height="72" rx="16" fill="url(#lockGradient)" />
            <circle cx="60" cy="88" r="9" fill="#060a18" />
            <rect x="56" y="92" width="8" height="20" rx="4" fill="#060a18" />
          </svg>
        </div>
        <div className="mx-auto mt-5 h-2 w-3/4 rounded bg-slate-700" />
      </div>
    </div>
  );
}

export default function AuthLayout({ eyebrow, title, subtitle, children, footer }) {
  return (
    <div className="min-h-screen bg-ink text-slate-200">
      <header className="px-6 py-6 sm:px-10">
        <Brand />
      </header>

      <main className="mx-auto grid max-w-6xl items-center gap-12 px-6 pb-12 pt-2 lg:min-h-[calc(100vh-190px)] lg:grid-cols-2">
        <div className="hidden lg:block">
          <LockIllustration />
        </div>

        <div className="card w-full max-w-md justify-self-center p-8 shadow-2xl shadow-black/40 lg:justify-self-end">
          <p className="eyebrow">{eyebrow}</p>
          <h1 className="mt-2 text-3xl font-extrabold text-white">{title}</h1>
          <p className="mt-2 text-sm text-slate-400">{subtitle}</p>
          <div className="mt-6">{children}</div>
          <p className="mt-6 text-center text-sm text-slate-400">{footer}</p>
        </div>
      </main>

      <p className="px-6 pb-8 text-xs text-slate-500 sm:px-10">
        One account. Your numbers stay private to you.
      </p>
    </div>
  );
}
