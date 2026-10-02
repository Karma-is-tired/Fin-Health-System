import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const API_BASE = "https://fin-health-system.onrender.com"; 

export default function Signup() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    if (password !== confirmPassword) return setError("Passwords do not match");

    const res = await fetch(`${API_BASE}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok) setStep(2);
    else setError(data.detail);
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    const res = await fetch(`${API_BASE}/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, otp })
    });
    if (res.ok) navigate('/login');
    else setError((await res.json()).detail);
  };

  return (
    <div className="min-h-screen bg-darkBg flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-cardBg rounded-xl p-8 border border-slate-700 shadow-2xl">
        <h3 className="text-accentYellow text-sm font-bold tracking-widest uppercase mb-2">
          {step === 1 ? "Create Account" : "Verify Email"}
        </h3>
        <h1 className="text-3xl font-bold text-white mb-6">
          {step === 1 ? "Sign up securely" : "Enter your OTP"}
        </h1>
        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {step === 1 ? (
          <form onSubmit={handleSignup} className="space-y-4">
            <input type="email" placeholder="Email address" required onChange={e => setEmail(e.target.value)} className="w-full bg-[#0b1120] border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-accentYellow" />
            <input type="password" placeholder="Password" required onChange={e => setPassword(e.target.value)} className="w-full bg-[#0b1120] border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-accentYellow" />
            <input type="password" placeholder="Confirm Password" required onChange={e => setConfirmPassword(e.target.value)} className="w-full bg-[#0b1120] border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-accentYellow" />
            <button type="submit" className="w-full bg-accentYellow text-black font-bold py-3 rounded-lg hover:bg-yellow-400">Send OTP</button>
            <p className="text-slate-400 text-sm text-center mt-4">Already have an account? <Link to="/login" className="text-accentYellow">Log in</Link></p>
          </form>
        ) : (
          <form onSubmit={handleVerify} className="space-y-4">
            <p className="text-slate-400 text-sm mb-4">Check your email {email} (or backend terminal if dev mode) for the 6-digit code.</p>
            <input type="text" placeholder="123456" required onChange={e => setOtp(e.target.value)} className="w-full bg-[#0b1120] border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-accentYellow text-center tracking-widest text-xl" />
            <button type="submit" className="w-full bg-accentYellow text-black font-bold py-3 rounded-lg hover:bg-yellow-400">Verify Account</button>
          </form>
        )}
      </div>
    </div>
  );
}