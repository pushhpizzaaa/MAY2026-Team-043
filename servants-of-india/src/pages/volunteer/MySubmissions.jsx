import { Link } from "react-router-dom";
import { submissionApi } from "../../services/endpoints";
import { useAsync } from "../../hooks/useAsync";
import { EmptyState, PageHeader, PageLoader, StatusBadge } from "../../components/ui";
import { formatDateTime } from "../../utils/datetime";

export default function MySubmissions() {
  const { data, loading, error } = useAsync(() => submissionApi.mine(), []);

  return (
    <div>
      <PageHeader
        title="My Submissions"
        subtitle="Track the status of every proof you've submitted."
        action={<Link to="/submit-proof" className="btn-accent text-sm">New submission</Link>}
      />

      {loading ? (
        <PageLoader />
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : data.length === 0 ? (
        <EmptyState
          title="No submissions yet"
          subtitle="Submit proof of your service to start earning your certificate."
          action={<Link to="/submit-proof" className="btn-accent">Submit proof</Link>}
        />
      ) : (
        <div className="space-y-3">
          {data.map((s) => (
            <div key={s.id} className="card">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex gap-4">
                  <img
                    src={s.image_url}
                    alt="proof"
                    className="h-20 w-20 rounded-lg border border-slate-200 object-cover"
                  />
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-brand-900">{s.category_name}</h3>
                      <StatusBadge status={s.status} />
                    </div>
                    <p className="mt-1 max-w-xl text-sm text-slate-500">{s.description}</p>
                    <p className="mt-1 text-xs text-slate-400">
                      Submitted {formatDateTime(s.submitted_at)} IST
                    </p>
                  </div>
                </div>
              </div>
              {s.status === "rejected" && s.review?.remarks && (
                <div className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                  <b>Rejection reason:</b> {s.review.remarks} — you may resubmit.
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
