import { Link } from "react-router-dom";
import { adminApi } from "../../services/endpoints";
import { useAuth } from "../../contexts/AuthContext";
import { useAsync } from "../../hooks/useAsync";
import { PageHeader, PageLoader, StatCard } from "../../components/ui";
import { BarChart, DonutChart } from "../../components/Charts";

export default function EmDashboard() {
  const { user } = useAuth();
  const { data, loading, error } = useAsync(() => adminApi.stats(), []);

  if (loading) return <PageLoader />;
  if (error) return <p className="text-red-600">{error}</p>;

  const s = data.submissions || {};
  const ev = data.events_by_status || {};

  return (
    <div>
      <PageHeader
        title={`Welcome, ${user.full_name.split(" ")[0]}`}
        subtitle="Overview of your events and the review queue."
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Your events" value={data.events ?? 0} accent="saffron" />
        <StatCard label="Pending reviews" value={s.pending ?? 0} />
        <StatCard label="Approved" value={s.approved ?? 0} />
        <StatCard label="Rejected" value={s.rejected ?? 0} />
      </div>

      {/* Graphical overview */}
      <div className="mt-8 grid gap-4 lg:grid-cols-2">
        <DonutChart
          title="Submissions by status"
          data={[
            { label: "Pending", value: s.pending ?? 0, color: "#d97706" },
            { label: "Approved", value: s.approved ?? 0, color: "#059669" },
            { label: "Rejected", value: s.rejected ?? 0, color: "#dc2626" },
          ]}
        />
        <BarChart
          title="Your events by status"
          data={[
            { label: "Upcoming", value: ev.upcoming ?? 0, color: "#1e4e79" },
            { label: "Completed", value: ev.completed ?? 0, color: "#059669" },
            { label: "Cancelled", value: ev.cancelled ?? 0, color: "#dc2626" },
          ]}
        />
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <Link to="/em/review-queue" className="btn-primary">Go to review queue</Link>
        <Link to="/em/events" className="btn-accent">Manage events</Link>
      </div>
    </div>
  );
}
