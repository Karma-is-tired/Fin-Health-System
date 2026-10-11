import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, ShieldCheck } from 'lucide-react';
import AuthLayout, { useSlowHint } from './AuthLayout';
import { isLoggedIn, signUp } from './api';

export default function Signup() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const slow = useSlowHint(loading);

  useEffect(() => {
    if (isLoggedIn()) navigate('/dashboard', { replace: true });
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password.length < 8) return setError('Your password needs at least 8 characters.');
    if (password !== confirm) return setError('The two passwords do not match.');

    setLoading(true);
    try {
      await signUp(email.trim(), password); // signing up also signs you in
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      eyebrow="Get started"
      title="Create your account"
      subtitle="Just an email and a password. Next time, sign in with the same two."
      footer={<>Already have an account? <Link to="/login" className="font-bold text-brand">Sign in</Link></>}
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-white">Email address</span>
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            className="field"
          />
        </label>

        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-white">Password</span>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              required
              minLength={8}
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              className="field pr-12"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </label>

        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-white">Confirm password</span>
          <input
            type={showPassword ? 'text' : 'password'}
            required
            autoComplete="new-password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            className="field"
          />
        </label>

        {error && (
          <p role="alert" className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
            {error}
          </p>
        )}

        <button type="submit" disabled={loading} className="btn-primary w-full">
          <ShieldCheck size={18} />
          {loading ? 'Creating account…' : 'Sign up'}
        </button>

        {slow && (
          <p className="text-center text-xs text-slate-400">
            The server may be waking up after being idle. This can take up to a minute.
          </p>
        )}
      </form>
    </AuthLayout>
  );
}
