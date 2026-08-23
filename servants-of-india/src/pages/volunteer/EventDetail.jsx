import { Link, useNavigate, useParams } from "react-router-dom";
import { eventApi } from "../../services/endpoints";
import { useAsync } from "../../hooks/useAsync";
import { PageLoader, StatusBadge } from "../../components/ui";
import { formatDate } from "../../utils/datetime";

export default function EventDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: e, loading, error } = useAsync(() => eventApi.get(id), [id]);

  if (loading) return <PageLoader />;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div className="max-w-3xl">
      <button onClick={() => navigate(-1)} className="btn-ghost mb-4 text-sm">← Back</button>

      <div className="card">
        <div className="flex items-start justify-between">
          <span className="badge bg-brand-100 text-brand-700">{e.category_name}</span>
          <StatusBadge status={e.status} />
        </div>
        <h1 className="mt-3 text-2xl font-bold text-brand-900">{e.title}</h1>
        <p className="mt-3 whitespace-pre-line text-slate-600">{e.description}</p>

        <dl className="mt-6 grid grid-cols-1 gap-4 border-t border-slate-100 pt-6 sm:grid-cols-2">
          <Detail label="Venue" value={e.venue} />
          <Detail label="Address" value={`${e.address}, ${e.city}, ${e.state}`} />
          <Detail label="Date" value={formatDate(e.event_date)} />
          <Detail label="Time" value={`${e.start_time} – ${e.end_time}`} />
          <Detail label="Capacity" value={e.capacity ?? "Unlimited"} />
          <Detail label="Organised by" value={e.created_by_name} />
        </dl>

        <div className="mt-6 border-t border-slate-100 pt-6">
          {e.status === "completed" ? (
            <Link to="/submit-proof" state={{ eventId: e.id, categoryId: e.category_id }} className="btn-accent">
              Submit proof for this event
            </Link>
          ) : (
            <p className="rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-500">
              You can submit proof of presence once this event is marked
              <span className="font-medium"> completed</span>.
            </p>
          )}
        </div>
      </div>
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
