// Small presentational primitives shared across pages.

export function Spinner({ className = "" }) {
  return (
    <svg
      className={`animate-spin h-5 w-5 ${className}`}
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}

export function PageLoader() {
  return (
    <div className="flex items-center justify-center py-24 text-brand-700">
      <Spinner className="h-8 w-8" />
    </div>
  );
}

export function EmptyState({ title, subtitle, action }) {
  return (
    <div className="rounded-xl border border-dashed border-slate-300 bg-white/50 px-6 py-14 text-center">
      <p className="text-base font-semibold text-slate-700">{title}</p>
      {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

const STATUS_STYLES = {
  pending: "bg-amber-100 text-amber-700",
  approved: "bg-emerald-100 text-emerald-700",
  completed: "bg-emerald-100 text-emerald-700",
  rejected: "bg-red-100 text-red-700",
  not_started: "bg-slate-100 text-slate-600",
  upcoming: "bg-brand-100 text-brand-700",
  cancelled: "bg-red-100 text-red-700",
  active: "bg-emerald-100 text-emerald-700",
  blocked: "bg-red-100 text-red-700",
  deactivated: "bg-slate-200 text-slate-600",
};

export function StatusBadge({ status }) {
  const cls = STATUS_STYLES[status] || "bg-slate-100 text-slate-600";
  return <span className={`badge ${cls}`}>{String(status).replace(/_/g, " ")}</span>;
}

export function PageHeader({ title, subtitle, action }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-bold text-brand-900">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function StatCard({ label, value, accent = "brand" }) {
  const ring = accent === "saffron" ? "text-saffron-500" : "text-brand-700";
  return (
    <div className="card">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className={`mt-2 text-3xl font-bold ${ring}`}>{value}</p>
    </div>
  );
}
