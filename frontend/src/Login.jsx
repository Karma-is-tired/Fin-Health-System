import { useNavigate } from 'react-router-dom';

export default function Login() {
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    navigate('/dashboard'); // Mock login for now
  };

  return (
    <div className="min-h-screen bg-darkBg flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-cardBg rounded-xl p-8 border border-slate-700 shadow-2xl">
        <h3 className="text-accentYellow text-sm font-bold tracking-widest uppercase mb-2">Welcome Back</h3>
        <h1 className="text-3xl font-bold text-white mb-6">Sign in securely</h1>
        
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Email address</label>
            <input type="email" required className="w-full bg-[#0b1120] border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-accentYellow" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">API Key (Password)</label>
            <input type="password" required className="w-full bg-[#0b1120] border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-accentYellow" />
          </div>
          <button type="submit" className="w-full bg-accentYellow text-black font-bold py-3 rounded-lg hover:bg-yellow-400 transition-colors">
            Sign in
          </button>
        </form>
      </div>
    </div>
  );
}