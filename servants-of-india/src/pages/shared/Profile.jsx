import { useEffect, useState } from "react";
import { userApi } from "../../services/endpoints";
import { useAuth } from "../../contexts/AuthContext";
import { useToast } from "../../contexts/ToastContext";
import { useAsync } from "../../hooks/useAsync";
import { PageHeader, PageLoader, Spinner } from "../../components/ui";
import { formatDate } from "../../utils/datetime";

export default function Profile() {
  const { user } = useAuth();
  const toast = useToast();
  const { data, loading } = useAsync(() => userApi.me(), []);
  const [form, setForm] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (data) {
      setForm({
        full_name: data.full_name || "",
        phone: data.phone || "",
        location: data.location || "",
        organization: data.organization || "",
      });
    }
  }, [data]);

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await userApi.updateMe(form);
      // Refresh cached user for the navbar name.
      localStorage.setItem("sob_user", JSON.stringify({ ...user, ...updated }));
      toast.success("Profile updated");
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !form) return <PageLoader />;

  return (
    <div className="max-w-2xl">
      <PageHeader title="My Profile" subtitle="Manage your account details." />
      <div className="card">
        <form onSubmit={save} className="space-y-4">
          <div>
            <label className="label">Email (cannot be changed)</label>
            <input className="input bg-slate-50" value={data.email} disabled />
          </div>
          <div>
            <label className="label">Full name</label>
            <input required className="input" value={form.full_name} onChange={update("full_name")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Phone</label>
              <input className="input" value={form.phone} onChange={update("phone")} />
            </div>
            <div>
              <label className="label">Location</label>
              <input className="input" value={form.location} onChange={update("location")} />
            </div>
          </div>
          <div>
            <label className="label">Organization</label>
            <input className="input" value={form.organization} onChange={update("organization")} />
          </div>
          <div className="flex justify-between border-t border-slate-100 pt-4 text-sm text-slate-500">
            <span>Role: <b className="capitalize text-slate-700">{data.role.replace("_", " ")}</b></span>
            <span>Joined: {formatDate(data.created_at)}</span>
          </div>
          <button type="submit" disabled={saving} className="btn-primary">
            {saving ? <Spinner /> : "Save changes"}
          </button>
        </form>
      </div>

      <ChangePassword />
    </div>
  );
}

function ChangePassword() {
  const toast = useToast();
  const [form, setForm] = useState({ current_password: "", new_password: "", confirm: "" });
  const [saving, setSaving] = useState(false);
  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    if (form.new_password.length < 8) return toast.error("New password must be at least 8 characters");
    if (form.new_password !== form.confirm) return toast.error("New passwords do not match");
    setSaving(true);
    try {
      await userApi.changePassword({
        current_password: form.current_password,
        new_password: form.new_password,
      });
      toast.success("Password updated");
      setForm({ current_password: "", new_password: "", confirm: "" });
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card mt-6">
      <h2 className="text-lg font-semibold text-brand-900">Change password</h2>
      <p className="mt-1 text-sm text-slate-500">Choose a strong password of at least 8 characters.</p>
      <form onSubmit={submit} className="mt-4 space-y-4">
        <div>
          <label className="label">Current password *</label>
          <input type="password" required className="input" value={form.current_password} onChange={update("current_password")} />
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label className="label">New password *</label>
            <input type="password" required className="input" value={form.new_password} onChange={update("new_password")} placeholder="Min. 8 characters" />
          </div>
          <div>
            <label className="label">Confirm new password *</label>
            <input type="password" required className="input" value={form.confirm} onChange={update("confirm")} />
          </div>
        </div>
        <button type="submit" disabled={saving} className="btn-primary">
          {saving ? <Spinner /> : "Update password"}
        </button>
      </form>
    </div>
  );
}
