import { useState } from "react";
import { userApi } from "../../services/endpoints";
import { useToast } from "../../contexts/ToastContext";
import { useAsync } from "../../hooks/useAsync";
import { EmptyState, PageHeader, PageLoader, Spinner, StatusBadge } from "../../components/ui";
import Modal from "../../components/Modal";

const EMPTY = { full_name: "", email: "", password: "", role: "event_manager", organization: "", phone: "", location: "" };

export default function AdminEventManagers() {
  const toast = useToast();
  const { data, loading, error, reload } = useAsync(() => userApi.list({ role: "event_manager" }), []);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const create = async (e) => {
    e.preventDefault();
    if (form.password.length < 8) return toast.error("Password must be at least 8 characters");
    if (form.role === "event_manager") {
      if (!form.organization.trim()) return toast.error("Organization is required for an Event Manager");
      if (!form.phone.trim()) return toast.error("Phone is required for an Event Manager");
      if (!form.location.trim()) return toast.error("Location is required for an Event Manager");
    }
    setSaving(true);
    try {
      await userApi.create(form);
      toast.success("Account created");
      setForm(EMPTY);
      setOpen(false);
      reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Event Managers"
        subtitle="Create and manage Event Manager accounts."
        action={<button onClick={() => setOpen(true)} className="btn-accent">+ New account</button>}
      />

      {loading ? (
        <PageLoader />
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : data.length === 0 ? (
        <EmptyState title="No event managers yet" action={<button onClick={() => setOpen(true)} className="btn-accent">Create one</button>} />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Organization</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.map((u) => (
                <tr key={u.id}>
                  <td className="px-4 py-3 font-medium text-slate-700">{u.full_name}</td>
                  <td className="px-4 py-3 text-slate-500">{u.email}</td>
                  <td className="px-4 py-3 text-slate-500">{u.organization || "—"}</td>
                  <td className="px-4 py-3"><StatusBadge status={u.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title="New privileged account">
        <form onSubmit={create} className="space-y-4">
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
              <label className="label">Role *</label>
              <select className="input" value={form.role} onChange={update("role")}>
                <option value="event_manager">Event Manager</option>
                <option value="super_admin">Super Admin</option>
              </select>
            </div>
            <div>
              <label className="label">Organization {form.role === "event_manager" && "*"}</label>
              <input
                required={form.role === "event_manager"}
                className="input"
                value={form.organization}
                onChange={update("organization")}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Phone {form.role === "event_manager" && "*"}</label>
              <input
                required={form.role === "event_manager"}
                className="input"
                value={form.phone}
                onChange={update("phone")}
              />
            </div>
            <div>
              <label className="label">Location {form.role === "event_manager" && "*"}</label>
              <input
                required={form.role === "event_manager"}
                className="input"
                value={form.location}
                onChange={update("location")}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={() => setOpen(false)} className="btn-ghost border border-slate-200">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? <Spinner /> : "Create account"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
