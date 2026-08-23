import { useState } from "react";
import { Link } from "react-router-dom";
import { submissionApi } from "../../services/endpoints";
import { useAsync } from "../../hooks/useAsync";
import { EmptyState, PageHeader, PageLoader, StatusBadge } from "../../components/ui";
import { formatDateTime } from "../../utils/datetime";

const TABS = [
  { key: "pending", label: "Pending" },
  { key: "approved", label: "Approved" },
  { key: "rejected", label: "Rejected" },
  { key: "all", label: "All" },
];

export default function ReviewQueue() {
  const [tab, setTab] = useState("pending");
  const { data, loading, error } = useAsync(() => submissionApi.queue(tab), [tab]);

  return (
    <div>
      <PageHeader title="Review Queue" subtitle="Approve or reject volunteer proof submissions." />

      <div className="mb-5 flex gap-1 rounded-lg border border-slate-200 bg-white p-1">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition ${
              tab === t.key ? "bg-brand-700 text-white" : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <PageLoader />
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : data.length === 0 ? (
        <EmptyState title="Nothing here" subtitle={`No ${tab} submissions.`} />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {data.map((s) => (
            <Link key={s.id} to={`/em/submissions/${s.id}`} className="card flex gap-4 transition hover:shadow-md">
              <img src={s.image_url} alt="proof" className="h-20 w-20 shrink-0 rounded-lg border border-slate-200 object-cover" />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="truncate font-semibold text-brand-900">{s.category_name}</h3>
                  <StatusBadge status={s.status} />
                </div>
                <p className="mt-0.5 text-sm text-slate-500">{s.volunteer_name}</p>
                <p className="mt-1 line-clamp-2 text-sm text-slate-500">{s.description}</p>
                <p className="mt-1 text-xs text-slate-400">{formatDateTime(s.submitted_at)} IST</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
