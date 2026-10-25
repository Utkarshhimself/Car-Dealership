import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate(location.state?.from?.pathname ?? "/inventory", { replace: true });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to sign in");
    } finally {
      setSubmitting(false);
    }
  }

  return <AuthCard title="Welcome back" subtitle="Sign in to browse the dealership inventory.">
    <form onSubmit={submit} className="stack">
      <label>Email<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
      <label>Password<input required type="password" minLength={1} value={password} onChange={(event) => setPassword(event.target.value)} /></label>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="button" disabled={submitting}>{submitting ? "Signing in…" : "Sign in"}</button>
    </form>
    <p className="muted">New here? <Link to="/register">Create an account</Link>.</p>
  </AuthCard>;
}

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(email, password);
      navigate("/login", { replace: true, state: { registered: true } });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to create account");
    } finally {
      setSubmitting(false);
    }
  }

  return <AuthCard title="Create your account" subtitle="Use at least 12 characters for your password.">
    <form onSubmit={submit} className="stack">
      <label>Email<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
      <label>Password<input required type="password" minLength={12} value={password} onChange={(event) => setPassword(event.target.value)} /></label>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="button" disabled={submitting}>{submitting ? "Creating account…" : "Create account"}</button>
    </form>
    <p className="muted">Already registered? <Link to="/login">Sign in</Link>.</p>
  </AuthCard>;
}

function AuthCard({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return <main className="auth-layout"><section className="auth-card"><p className="eyebrow">Motorhouse</p><h1>{title}</h1><p className="muted">{subtitle}</p>{children}</section></main>;
}
