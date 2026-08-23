import { useState } from "react";
import { categoryApi, eventApi } from "../../services/endpoints";
import { useAuth } from "../../contexts/AuthContext";
import { useToast } from "../../contexts/ToastContext";
import { useAsync } from "../../hooks/useAsync";
import { EmptyState, PageHeader, PageLoader, Spinner, StatusBadge } from "../../components/ui";
import Modal from "../../components/Modal";
import { formatDate } from "../../utils/datetime";

const EMPTY = {
  title: "", description: "", category_id: "", venue: "", address: "",
  city: "", state: "", event_date: "", start_time: "", end_time: "",
  capacity: "", status: "upcoming",
};

export default function EmEvents() {
  const { user } = useAuth();
  const toast = useToast();
  const events = useAsync(() => eventApi.list(), []);
  const categories = useAsync(() => categoryApi.list(), []);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null); // event id or null
  const [form, setForm] = useState(EMPTY);
  const [saving, setSaving] = useState(false);
  const [viewing, setViewing] = useState(null); // event shown in detail modal
  const [toDelete, setToDelete] = useState(null); // event pending delete confirmation
  const [deleting, setDeleting] = useState(false);

  const canModify = (e) => user.role === "super_admin" || e.created_by === user.id;

  const openCreate = () => {
    setEditing(null);
    setForm(EMPTY);
    setModalOpen(true);
  };

  const openEdit = (e) => {
    setEditing(e.id);
    setForm({
      title: e.title, description: e.description, category_id: e.category_id,
      venue: e.venue, address: e.address, city: e.city, state: e.state,
      event_date: e.event_date, start_time: e.start_time, end_time: e.end_time,
      capacity: e.capacity ?? "", status: e.status,
    });
    setModalOpen(true);
  };

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    setSaving(true);
    const payload = { ...form, capacity: form.capacity ? Number(form.capacity) : null };
    try {
      if (editing) {
        await eventApi.update(editing, payload);
        toast.success("Event updated");
      } else {
        await eventApi.create(payload);
        toast.success("Event created");
      }
      setModalOpen(false);
      events.reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!toDelete) return;
    setDeleting(true);
    try {
      await eventApi.remove(toDelete.id);
      toast.success("Event deleted");
      setToDelete(null);
      events.reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Events"
        subtitle="Create and manage service events."
        action={<button onClick={openCreate} className="btn-accent">+ New event</button>}
      />

      {events.loading ? (
        <PageLoader />
      ) : events.data.length === 0 ? (
        <EmptyState title="No events yet" action={<button onClick={openCreate} className="btn-accent">Create your first event</button>} />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Title</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">City</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {events.data.map((e) => (
                <tr key={e.id} className="cursor-pointer hover:bg-slate-50" onClick={() => setViewing(e)}>
                  <td className="px-4 py-3 font-medium text-brand-800 hover:underline">{e.title}</td>
                  <td className="px-4 py-3 text-slate-500">{e.category_name}</td>
                  <td className="px-4 py-3 text-slate-500">{formatDate(e.event_date)}</td>
                  <td className="px-4 py-3 text-slate-500">{e.city}</td>
                  <td className="px-4 py-3"><StatusBadge status={e.status} /></td>
                  <td className="px-4 py-3 text-right" onClick={(ev) => ev.stopPropagation()}>
                    {canModify(e) ? (
                      <div className="flex justify-end gap-2">
                        <button onClick={() => openEdit(e)} className="text-brand-700 hover:underline">Edit</button>
                        <button onClick={() => setToDelete(e)} className="text-red-600 hover:underline">Delete</button>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-300">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create / edit form */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? "Edit event" : "New event"} wide>
        <form onSubmit={save} className="space-y-4">
          <div>
            <label className="label">Title *</label>
            <input required className="input" value={form.title} onChange={update("title")} />
          </div>
          <div>
            <label className="label">Description *</label>
            <textarea required className="input min-h-[80px]" value={form.description} onChange={update("description")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Category *</label>
              <select required className="input" value={form.category_id} onChange={update("category_id")}>
                <option value="">Select…</option>
                {(categories.data || []).map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Status</label>
              <select className="input" value={form.status} onChange={update("status")}>
                <option value="upcoming">Upcoming</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">Venue *</label>
            <input required className="input" value={form.venue} onChange={update("venue")} />
          </div>
          <div>
            <label className="label">Address *</label>
            <input required className="input" value={form.address} onChange={update("address")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">City *</label>
              <input required className="input" value={form.city} onChange={update("city")} />
            </div>
            <div>
              <label className="label">State *</label>
              <input required className="input" value={form.state} onChange={update("state")} />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="label">Date *</label>
              <input type="date" required className="input" value={form.event_date} onChange={update("event_date")} />
            </div>
            <div>
              <label className="label">Start *</label>
              <input type="time" required className="input" value={form.start_time} onChange={update("start_time")} />
            </div>
            <div>
              <label className="label">End *</label>
              <input type="time" required className="input" value={form.end_time} onChange={update("end_time")} />
            </div>
          </div>
          <div>
            <label className="label">Capacity</label>
            <input type="number" min="1" className="input" value={form.capacity} onChange={update("capacity")} placeholder="Leave blank for unlimited" />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={() => setModalOpen(false)} className="btn-ghost border border-slate-200">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? <Spinner /> : editing ? "Save changes" : "Create event"}
            </button>
          </div>
        </form>
      </Modal>

      {/* Event detail view */}
      <Modal open={!!viewing} onClose={() => setViewing(null)} title="Event details" wide>
        {viewing && (
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <span className="badge bg-brand-100 text-brand-700">{viewing.category_name}</span>
                <h2 className="mt-2 text-xl font-bold text-brand-900">{viewing.title}</h2>
              </div>
              <StatusBadge status={viewing.status} />
            </div>
            <p className="whitespace-pre-line text-slate-600">{viewing.description}</p>
            <dl className="grid grid-cols-1 gap-4 border-t border-slate-100 pt-4 sm:grid-cols-2">
              <Detail label="Venue" value={viewing.venue} />
              <Detail label="Address" value={`${viewing.address}, ${viewing.city}, ${viewing.state}`} />
              <Detail label="Date" value={formatDate(viewing.event_date)} />
              <Detail label="Time" value={`${viewing.start_time} – ${viewing.end_time}`} />
              <Detail label="Capacity" value={viewing.capacity ?? "Unlimited"} />
              <Detail label="Organised by" value={viewing.created_by_name} />
            </dl>
            <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
              {canModify(viewing) && (
                <button
                  onClick={() => { const e = viewing; setViewing(null); openEdit(e); }}
                  className="btn-primary"
                >
                  Edit event
                </button>
              )}
              <button onClick={() => setViewing(null)} className="btn-ghost border border-slate-200">Close</button>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete confirmation */}
      <Modal open={!!toDelete} onClose={() => setToDelete(null)} title="Delete event?">
        {toDelete && (
          <div className="space-y-5">
            <p className="text-sm text-slate-600">
              Are you sure you want to delete <b className="text-slate-800">{toDelete.title}</b>?
              This action cannot be undone.
            </p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setToDelete(null)} className="btn-ghost border border-slate-200">Cancel</button>
              <button onClick={confirmDelete} disabled={deleting} className="btn-danger">
                {deleting ? <Spinner /> : "Delete event"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

function Detail({ label, value }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</dt>
      <dd className="mt-0.5 text-sm font-medium text-slate-700">{value}</dd>
    </div>
  );
}
