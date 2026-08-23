import { Link } from "react-router-dom";
import { adminApi } from "../../services/endpoints";
import { useAsync } from "../../hooks/useAsync";
import { PageHeader, PageLoader, StatCard } from "../../components/ui";
import { BarChart, DonutChart } from "../../components/Charts";

export default function AdminDashboard() {
  const { data, loading, error } = useAsync(() => adminApi.stats(), []);

  if (loading) return <PageLoader />;
  if (error) return <p className="text-red-600">{error}</p>;

  const u = data.users || {};
  const s = data.submissions || {};
  const ev = data.events_by_status || {};

  return (
    <div>
      <PageHeader title="Admin Dashboard" subtitle="System-wide overview." />

      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">Users</h3>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard label="Total users" value={u.total ?? 0} accent="saffron" />
        <StatCard label="Volunteers" value={u.volunteers ?? 0} />
        <StatCard label="Event Managers" value={u.event_managers ?? 0} />
        <StatCard label="Admins" value={u.admins ?? 0} />
        <StatCard label="Blocked" value={u.blocked ?? 0} />
      </div>

      <h3 className="mb-3 mt-8 text-sm font-semibold uppercase tracking-wide text-slate-400">Activity</h3>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard label="Events" value={data.events ?? 0} accent="saffron" />
        <StatCard label="Pending" value={s.pending ?? 0} />
        <StatCard label="Approved" value={s.approved ?? 0} />
        <StatCard label="Rejected" value={s.rejected ?? 0} />
        <StatCard label="Certificates" value={data.certificates_issued ?? 0} />
      </div>

      {/* Graphical overview */}
      <h3 className="mb-3 mt-8 text-sm font-semibold uppercase tracking-wide text-slate-400">Analytics</h3>
      <div className="grid gap-4 lg:grid-cols-2">
        <DonutChart
          title="Submissions by status"
          data={[
            { label: "Pending", value: s.pending ?? 0, color: "#d97706" },
            { label: "Approved", value: s.approved ?? 0, color: "#059669" },
            { label: "Rejected", value: s.rejected ?? 0, color: "#dc2626" },
          ]}
        />
        <BarChart
          title="Users & events"
          data={[
            { label: "Volunteers", value: u.volunteers ?? 0, color: "#1e4e79" },
            { label: "Event Managers", value: u.event_managers ?? 0, color: "#0f2b46" },
            { label: "Upcoming events", value: ev.upcoming ?? 0, color: "#d97706" },
            { label: "Completed events", value: ev.completed ?? 0, color: "#059669" },
            { label: "Certificates", value: data.certificates_issued ?? 0, color: "#7c3aed" },
          ]}
        />
      </div>

      {/* Quick actions — review queue box gets a highlighted background (#13) */}
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Link to="/admin/users" className="btn-primary">Manage users</Link>
        <Link to="/admin/event-managers" className="btn-accent">Manage event managers</Link>
        <Link
          to="/em/review-queue"
          className="flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 shadow-card transition hover:bg-amber-100"
        >
          <div>
            <p className="text-sm font-semibold text-amber-900">Review Queue</p>
            <p className="text-xs text-amber-700">{s.pending ?? 0} pending submission(s)</p>
          </div>
          <span className="grid h-9 w-9 place-items-center rounded-full bg-amber-500 text-white">→</span>
        </Link>
      </div>
    </div>
  );
}
