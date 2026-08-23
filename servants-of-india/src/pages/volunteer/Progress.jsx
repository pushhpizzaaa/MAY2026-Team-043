import { Link } from "react-router-dom";
import { progressApi } from "../../services/endpoints";
import { useAsync } from "../../hooks/useAsync";
import { PageHeader, PageLoader, StatusBadge } from "../../components/ui";

export default function Progress() {
  const { data, loading, error } = useAsync(() => progressApi.me(), []);

  if (loading) return <PageLoader />;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <div className="max-w-2xl">
      <PageHeader title="My Progress" subtitle="Complete all five categories to earn your certificate." />

      {/* Stars */}
      <div className="card mb-6 text-center">
        <p className="text-sm font-medium text-slate-500">Categories completed</p>
        <div className="mt-3 flex justify-center gap-2 text-3xl">
          {Array.from({ length: data.total_categories }).map((_, i) => (
            <span key={i} className={i < data.stars ? "text-saffron-500" : "text-slate-200"}>★</span>
          ))}
        </div>
        <p className="mt-3 text-2xl font-bold text-brand-900">
          {data.stars} / {data.total_categories}
        </p>
        {data.all_completed && (
          <Link to="/certificate" className="btn-accent mt-4">Generate certificate →</Link>
        )}
      </div>

      <div className="space-y-2">
        {data.categories.map((c) => (
          <div key={c.category_id} className="card flex items-center justify-between py-4">
            <span className="font-medium text-slate-700">{c.category_name}</span>
            <StatusBadge status={c.status} />
          </div>
        ))}
      </div>
    </div>
  );
}
