import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { LayoutDashboard, Upload, LogOut } from 'lucide-react';
import Dashboard from './Dashboard';
import UploadScreen from './UploadScreen';
import Login from './Login';

function SidebarLayout({ children }) {
  return (
    <div className="flex h-screen bg-darkBg text-slate-300 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-[#111827] border-r border-slate-800 flex flex-col">
        <div className="p-6">
          <h2 className="text-xl font-bold text-white tracking-wider">FIN<span className="text-accentYellow">HEALTH</span></h2>
        </div>
        <nav className="flex-1 px-4 space-y-2 mt-4">
          <Link to="/dashboard" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 hover:text-accentYellow transition-colors">
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </Link>
          <Link to="/upload" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 hover:text-accentYellow transition-colors">
            <Upload size={20} />
            <span>Upload Data</span>
          </Link>
        </nav>
        <div className="p-4 border-t border-slate-800">
          <Link to="/" className="flex items-center gap-3 p-3 rounded-lg text-red-400 hover:bg-slate-800 transition-colors">
            <LogOut size={20} />
            <span>Sign out</span>
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<SidebarLayout><Dashboard /></SidebarLayout>} />
        <Route path="/upload" element={<SidebarLayout><UploadScreen /></SidebarLayout>} />
      </Routes>
    </Router>
  );
}