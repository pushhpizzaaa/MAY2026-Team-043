import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthLayout from "./AuthLayout";
import { useAuth } from "../../contexts/AuthContext";
import { useToast } from "../../contexts/ToastContext";
import { homeForRole } from "../../components/ProtectedRoute";
import { Spinner } from "../../components/ui";

export default function Login() {
  const { login, loading } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });

  const submit = async (e) => {
    e.preventDefault();
    try {
      const user = await login(form.email, form.password);
      toast.success(`Welcome back, ${user.full_name.split(" ")[0]}!`);
      navigate(homeForRole(user.role), { replace: true });
    } catch (err) {
      toast.error(err.message);
    }
  };

  return (
    <AuthLayout
      title="Sign in"
      subtitle="Welcome back. Enter your credentials to continue."
      footer={
        <>
          New here?{" "}
          <Link to="/register" className="font-semibold text-brand-700 hover:underline">
            Create a volunteer account
          </Link>
        </>
      }
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="label">Email</label>
          <input
            type="email"
            required
            className="input"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label className="label">Password</label>
          <input
            type="password"
            required
            className="input"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder="••••••••"
          />
        </div>
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? <Spinner /> : "Sign in"}
        </button>
      </form>
    </AuthLayout>
  );
}
