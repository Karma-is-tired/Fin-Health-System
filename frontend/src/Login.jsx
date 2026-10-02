import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const API_BASE = "https://fin-health-system.onrender.com"; 

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    // FastAPI's OAuth2 expects form-encoded data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });

    const data = await res.json();
    if (res.ok) {
      localStorage.setItem('token', data.access_token);
      navigate('/dashboard');
    } else {
      setError(data.detail);
    }
  };

  return (
    <div className="min-h-screen bg-darkBg flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-cardBg rounded-xl p-8 border border-slate-700 shadow-2xl">
        <h3 className="text-accentYellow text-sm font-bold tracking-widest uppercase mb-2">Welcome Back</h3>
        <h1 className="text-3xl font-bold text-white mb-6">Sign in securely</h1>
        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}
        
        <form onSubmit={handleLogin} className="space-y-6">
          <input type="email" placeholder="Email address" required onChange={e => setEmail(e.target.value)} className="w-full bg-[#0b1120] border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-accentYellow" />
          <input type="password" placeholder="Password" required onChange={e => setPassword(e.target.value)} className="w-full bg-[#0b1120] border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-accentYellow" />
          <button type="submit" className="w-full bg-accentYellow text-black font-bold py-3 rounded-lg hover:bg-yellow-400">Sign in</button>
        </form>
        <p className="text-slate-400 text-sm text-center mt-6">No account yet? <Link to="/signup" className="text-accentYellow">Create one</Link></p>
      </div>
    </div>
  );
}