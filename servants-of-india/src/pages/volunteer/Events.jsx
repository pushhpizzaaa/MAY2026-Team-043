import { useState } from "react";
import { Link } from "react-router-dom";
import { eventApi } from "../../services/endpoints";
import { useAsync } from "../../hooks/useAsync";
import { EmptyState, PageHeader, PageLoader, StatusBadge } from "../../components/ui";

export default function Events() {
  const [status, setStatus] = useState("");
  const { data, loading, error } = useAsync(
    () => eventApi.list(status ? { status } : {}),
    [status]
  );

  return (
    <div>
      <PageHeader
        title="Events"
        subtitle="Browse service events happening across the country."
        action={
          <select className="input w-44" value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All statuses</option>
            <option value="upcoming">Upcoming</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        }
      />

      {loading ? (
        <PageLoader />
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : data.length === 0 ? (
        <EmptyState title="No events found" subtitle="Check back soon for new service opportunities." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((e) => (
            <Link key={e.id} to={`/events/${e.slug}`} className="card transition hover:shadow-md">
              <div className="flex items-start justify-between">
                <span className="badge bg-brand-100 text-brand-700">{e.category_name}</span>
                <StatusBadge status={e.status} />
              </div>
              <h3 className="mt-3 font-semibold text-brand-900">{e.title}</h3>
              <p className="mt-1 line-clamp-2 text-sm text-slate-500">{e.description}</p>
              <div className="mt-4 space-y-1 text-sm text-slate-500">
                <p>📍 {e.venue}, {e.city}</p>
                <p>📅 {new Date(e.event_date).toLocaleDateString()} · {e.start_time}–{e.end_time}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
