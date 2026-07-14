import { Link } from "react-router-dom";
import { progressApi, submissionApi, notificationApi } from "../../services/endpoints";
import { useAuth } from "../../contexts/AuthContext";
import { useAsync } from "../../hooks/useAsync";
import { PageHeader, PageLoader, StatCard, StatusBadge } from "../../components/ui";

export default function VolunteerDashboard() {
  const { user } = useAuth();
  const progress = useAsync(() => progressApi.me(), []);
  const subs = useAsync(() => submissionApi.mine(), []);
  const notes = useAsync(() => notificationApi.list(), []);

  if (progress.loading) return <PageLoader />;

  const p = progress.data || { stars: 0, total_categories: 5, all_completed: false };
  const recent = (subs.data || []).slice(0, 4);

  return (
    <div>
      <PageHeader
        title={`Namaste, ${user.full_name.split(" ")[0]} 👋`}
        subtitle="Here's your service journey so far."
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Categories completed" value={`${p.stars} / ${p.total_categories}`} accent="saffron" />
        <StatCard label="Total submissions" value={subs.data?.length ?? "—"} />
        <StatCard label="Unread notifications" value={notes.data?.unread_count ?? "—"} />
      </div>

      {/* Progress bar */}
      <div className="card mt-6">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-brand-900">Progress to certificate</h3>
          <Link to="/progress" className="text-sm font-semibold text-brand-700 hover:underline">
            View details
          </Link>
        </div>
        <div className="mt-4 h-3 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-saffron-500 transition-all"
            style={{ width: `${(p.stars / p.total_categories) * 100}%` }}
          />
        </div>
        <p className="mt-3 text-sm text-slate-500">
          {p.all_completed ? (
            <>
              All categories complete!{" "}
              <Link to="/certificate" className="font-semibold text-saffron-600 hover:underline">
                Generate your certificate →
              </Link>
            </>
          ) : (
            `${p.total_categories - p.stars} categor${p.total_categories - p.stars === 1 ? "y" : "ies"} left to complete.`
          )}
        </p>
      </div>

      {/* Recent submissions */}
      <div className="card mt-6">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-brand-900">Recent submissions</h3>
          <Link to="/submit-proof" className="btn-accent text-sm">Submit proof</Link>
        </div>
        {recent.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">No submissions yet.</p>
        ) : (
          <ul className="mt-4 divide-y divide-slate-100">
            {recent.map((s) => (
              <li key={s.id} className="flex items-center justify-between py-3">
                <div>
                  <p className="text-sm font-semibold text-slate-700">{s.category_name}</p>
                  <p className="text-xs text-slate-400">
                    {new Date(s.submitted_at).toLocaleDateString()}
                  </p>
                </div>
                <StatusBadge status={s.status} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
