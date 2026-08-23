import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthLayout from "./AuthLayout";
import { useAuth } from "../../contexts/AuthContext";
import { useToast } from "../../contexts/ToastContext";
import { Spinner } from "../../components/ui";

export default function Register() {
  const { register, loading } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    phone: "",
    location: "",
    organization: "",
  });

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    if (form.password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
    try {
      await register(form);
      toast.success("Account created — welcome!");
      navigate("/dashboard", { replace: true });
    } catch (err) {
      toast.error(err.message);
    }
  };

  return (
    <AuthLayout
      title="Create your volunteer account"
      subtitle="Only volunteers self-register. Managers are added by an admin."
      footer={
        <>
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-brand-700 hover:underline">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="label">Full name *</label>
          <input required className="input" value={form.full_name} onChange={update("full_name")} />
        </div>
        <div>
          <label className="label">Email *</label>
          <input type="email" required className="input" value={form.email} onChange={update("email")} />
        </div>
        <div>
          <label className="label">Password *</label>
          <input type="password" required className="input" value={form.password} onChange={update("password")} placeholder="Min. 8 characters" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Phone *</label>
            <input required className="input" value={form.phone} onChange={update("phone")} />
          </div>
          <div>
            <label className="label">Location *</label>
            <input required className="input" value={form.location} onChange={update("location")} />
          </div>
        </div>
        <div>
          <label className="label">Organization</label>
          <input className="input" value={form.organization} onChange={update("organization")} />
        </div>
        <button type="submit" disabled={loading} className="btn-accent w-full">
          {loading ? <Spinner /> : "Create account"}
        </button>
      </form>
    </AuthLayout>
  );
}
