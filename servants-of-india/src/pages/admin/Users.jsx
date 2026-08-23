import { useState } from "react";
import { userApi } from "../../services/endpoints";
import { useAuth } from "../../contexts/AuthContext";
import { useToast } from "../../contexts/ToastContext";
import { useAsync } from "../../hooks/useAsync";
import { EmptyState, PageHeader, PageLoader, StatusBadge } from "../../components/ui";
import Modal from "../../components/Modal";
import { formatDate } from "../../utils/datetime";

const ROLE_LABEL = { volunteer: "Volunteer", event_manager: "Event Manager", super_admin: "Super Admin" };

export default function AdminUsers() {
  const { user: me } = useAuth();
  const toast = useToast();
  const [filters, setFilters] = useState({ role: "", status: "" });
  const [search, setSearch] = useState(""); // email search
  const [selected, setSelected] = useState(null); // user shown in the detail modal
  const { data, loading, error, reload } = useAsync(
    () => userApi.list({ role: filters.role || undefined, status: filters.status || undefined }),
    [filters.role, filters.status]
  );

  const visible = (data || []).filter((u) =>
    u.email.toLowerCase().includes(search.trim().toLowerCase())
  );

  const changeStatus = async (id, status) => {
    try {
      await userApi.setStatus(id, status);
      toast.success(`User ${status}`);
      reload();
    } catch (err) {
      toast.error(err.message);
    }
  };

  return (
    <div>
      <PageHeader
        title="Users"
        subtitle="View and manage every account."
        action={
          <div className="flex flex-wrap gap-2">
            <input
              type="search"
              className="input w-56"
              placeholder="Search by email…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select className="input w-40" value={filters.role} onChange={(e) => setFilters({ ...filters, role: e.target.value })}>
              <option value="">All roles</option>
              <option value="volunteer">Volunteers</option>
              <option value="event_manager">Event Managers</option>
              <option value="super_admin">Admins</option>
            </select>
            <select className="input w-40" value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="blocked">Blocked</option>
              <option value="deactivated">Deactivated</option>
            </select>
          </div>
        }
      />

      {loading ? (
        <PageLoader />
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : visible.length === 0 ? (
        <EmptyState title="No users match these filters" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {visible.map((u) => (
                <tr key={u.id} className="cursor-pointer hover:bg-slate-50" onClick={() => setSelected(u)}>
                  <td className="px-4 py-3 font-medium text-brand-800 hover:underline">{u.full_name}</td>
                  <td className="px-4 py-3 text-slate-500">{u.email}</td>
                  <td className="px-4 py-3 text-slate-500">{ROLE_LABEL[u.role]}</td>
                  <td className="px-4 py-3"><StatusBadge status={u.status} /></td>
                  <td className="px-4 py-3 text-right" onClick={(e) => e.stopPropagation()}>
                    {u.id === me.id ? (
                      <span className="text-xs text-slate-300">You</span>
                    ) : (
                      <div className="flex justify-end gap-2 text-xs">
                        {u.status !== "active" && (
                          <button onClick={() => changeStatus(u.id, "active")} className="text-emerald-600 hover:underline">Activate</button>
                        )}
                        {u.status !== "blocked" && (
                          <button onClick={() => changeStatus(u.id, "blocked")} className="text-red-600 hover:underline">Block</button>
                        )}
                        {u.status !== "deactivated" && (
                          <button onClick={() => changeStatus(u.id, "deactivated")} className="text-slate-500 hover:underline">Deactivate</button>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* User detail modal */}
      <Modal open={!!selected} onClose={() => setSelected(null)} title="User details">
        {selected && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="grid h-12 w-12 place-items-center rounded-full bg-brand-100 text-lg font-bold text-brand-700">
                {selected.full_name?.[0]?.toUpperCase()}
              </div>
              <div>
                <p className="font-semibold text-slate-800">{selected.full_name}</p>
                <p className="text-sm text-slate-500">{ROLE_LABEL[selected.role]}</p>
              </div>
              <div className="ml-auto"><StatusBadge status={selected.status} /></div>
            </div>
            <dl className="grid grid-cols-1 gap-3 border-t border-slate-100 pt-4 sm:grid-cols-2">
              <Field label="Email" value={selected.email} />
              <Field label="Phone" value={selected.phone} />
              <Field label="Location" value={selected.location} />
              <Field label="Organization" value={selected.organization} />
              <Field label="Joined" value={formatDate(selected.created_at)} />
            </dl>
          </div>
        )}
      </Modal>
    </div>
  );
}

function Field({ label, value, mono }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</dt>
      <dd className={`mt-0.5 text-sm text-slate-700 ${mono ? "font-mono text-xs break-all" : ""}`}>
        {value || "—"}
      </dd>
    </div>
  );
}
