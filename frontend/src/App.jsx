import { BrowserRouter as Router, Routes, Route, Link, useNavigate, Navigate } from 'react-router-dom';
import { LayoutDashboard, Upload, FileText, LogOut } from 'lucide-react';
import Dashboard from './Dashboard';
import UploadScreen from './UploadScreen';
import Login from './Login';
import Signup from './Signup';
import History from './History';

// Protect routes: checks if a token exists
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function SidebarLayout({ children }) {
  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-darkBg text-slate-300 font-sans">
      <aside className="w-64 bg-[#111827] border-r border-slate-800 flex flex-col">
        <div className="p-6">
          <h2 className="text-xl font-bold text-white tracking-wider">FIN<span className="text-accentYellow">HEALTH</span></h2>
        </div>
        <nav className="flex-1 px-4 space-y-2 mt-4">
          <Link to="/dashboard" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 hover:text-accentYellow transition-colors">
            <LayoutDashboard size={20} /><span>Dashboard</span>
          </Link>
          <Link to="/upload" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 hover:text-accentYellow transition-colors">
            <Upload size={20} /><span>Upload Data</span>
          </Link>
          <Link to="/history" className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800 hover:text-accentYellow transition-colors">
            <FileText size={20} /><span>Report History</span>
          </Link>
        </nav>
        <div className="p-4 border-t border-slate-800">
          <button onClick={handleLogout} className="w-full flex items-center gap-3 p-3 rounded-lg text-red-400 hover:bg-slate-800 transition-colors">
            <LogOut size={20} /><span>Sign out</span>
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto p-8">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<ProtectedRoute><SidebarLayout><Dashboard /></SidebarLayout></ProtectedRoute>} />
        <Route path="/upload" element={<ProtectedRoute><SidebarLayout><UploadScreen /></SidebarLayout></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><SidebarLayout><History /></SidebarLayout></ProtectedRoute>} />
      </Routes>
    </Router>
  );
}