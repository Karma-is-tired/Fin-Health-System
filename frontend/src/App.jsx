import { useState } from 'react';
import { BrowserRouter, Navigate, NavLink, Outlet, Route, Routes, useLocation } from 'react-router-dom';
import { FileText, LayoutDashboard, LogOut, Menu, UploadCloud } from 'lucide-react';
import { Brand } from './AuthLayout';
import Dashboard from './Dashboard';
import UploadScreen from './UploadScreen';
import History from './History';
import Login from './Login';
import Signup from './Signup';
import { currentEmail, isLoggedIn, signOut } from './api';

const NAV = [
  { section: 'Overview', items: [{ to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard }] },
  {
    section: 'Your data',
    items: [
      { to: '/upload', label: 'Upload data', icon: UploadCloud },
      { to: '/history', label: 'Report history', icon: FileText },
    ],
  },
];

const TITLES = {
  '/dashboard': ['Overview', 'Dashboard'],
  '/upload': ['Your data', 'Upload data'],
  '/history': ['Reports', 'Report history'],
};

function AppShell() {
  const location = useLocation();
  const [open, setOpen] = useState(() => window.innerWidth >= 1024);
  const email = currentEmail();
  const [eyebrow, title] = TITLES[location.pathname] || ['Workspace', 'FinHealth'];

  // On a phone, tapping a link closes the menu.
  const closeOnMobile = () => {
    if (window.innerWidth < 1024) setOpen(false);
  };

  return (
    <div className="min-h-screen bg-ink">
      {open && (
        <button
          aria-label="Close menu"
          onClick={() => setOpen(false)}
          className="fixed inset-0 z-30 bg-black/60 lg:hidden"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-line bg-panel transition-transform duration-200 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="border-b border-line px-5 py-5">
          <Brand />
        </div>

        <nav className="flex-1 space-y-6 overflow-y-auto px-4 py-6">
          {NAV.map((group) => (
            <div key={group.section}>
              <p className="mb-3 px-3 text-[10px] font-extrabold uppercase tracking-[0.25em] text-slate-500">
                {group.section}
              </p>
              <div className="space-y-2">
                {group.items.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={closeOnMobile}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-xl px-4 py-3.5 text-sm font-bold transition ${
                        isActive
                          ? 'bg-brand text-slate-900 shadow-lg shadow-brand/20'
                          : 'text-slate-300 hover:bg-card hover:text-white'
                      }`
                    }
                  >
                    <Icon size={18} />
                    {label}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-line p-4">
          <button
            onClick={signOut}
            className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-bold text-rose-400 transition hover:bg-card"
          >
            <LogOut size={18} />
            Sign out
          </button>
        </div>
      </aside>

      <div className={`transition-[padding] duration-200 ${open ? 'lg:pl-72' : ''}`}>
        <header className="sticky top-0 z-20 flex items-center gap-4 border-b border-line bg-ink/90 px-4 py-3 backdrop-blur sm:px-6">
          <button
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
            className="flex h-11 w-11 items-center justify-center rounded-xl border border-line bg-panel text-white hover:border-slate-600"
          >
            <Menu size={20} />
          </button>
          <div className="leading-tight">
            <p className="text-[10px] font-extrabold uppercase tracking-[0.25em] text-brand">{eyebrow}</p>
            <p className="text-lg font-extrabold text-white">{title}</p>
          </div>

          <div className="ml-auto flex items-center gap-3">
            <p className="hidden max-w-[220px] truncate text-sm text-slate-400 sm:block">{email}</p>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand text-base font-extrabold text-slate-900">
              {(email[0] || 'U').toUpperCase()}
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-6xl p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function RequireLogin() {
  return isLoggedIn() ? <AppShell /> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route element={<RequireLogin />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<UploadScreen />} />
          <Route path="/history" element={<History />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
