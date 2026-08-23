// Dependency-free SVG charts — a horizontal bar chart and a donut chart.
// Kept minimal and theme-aligned with the brand/saffron palette.

const PALETTE = ["#0f2b46", "#1e4e79", "#d97706", "#059669", "#dc2626", "#7c3aed"];

/**
 * Horizontal bar chart.
 * @param {{label: string, value: number, color?: string}[]} data
 */
export function BarChart({ title, data = [] }) {
  const max = Math.max(1, ...data.map((d) => d.value));
  return (
    <div className="card">
      {title && <h3 className="mb-4 text-sm font-semibold text-slate-700">{title}</h3>}
      <div className="space-y-3">
        {data.map((d, i) => (
          <div key={d.label}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="font-medium text-slate-600">{d.label}</span>
              <span className="tabular-nums text-slate-400">{d.value}</span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${(d.value / max) * 100}%`,
                  backgroundColor: d.color || PALETTE[i % PALETTE.length],
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Donut chart with a legend.
 * @param {{label: string, value: number, color?: string}[]} data
 */
export function DonutChart({ title, data = [] }) {
  const total = data.reduce((s, d) => s + d.value, 0);
  const radius = 60;
  const stroke = 22;
  const circ = 2 * Math.PI * radius;
  let offset = 0;

  return (
    <div className="card">
      {title && <h3 className="mb-4 text-sm font-semibold text-slate-700">{title}</h3>}
      <div className="flex items-center gap-6">
        <svg viewBox="0 0 160 160" className="h-40 w-40 shrink-0 -rotate-90">
          {/* Track */}
          <circle cx="80" cy="80" r={radius} fill="none" stroke="#f1f5f9" strokeWidth={stroke} />
          {total > 0 &&
            data.map((d, i) => {
              const frac = d.value / total;
              const dash = frac * circ;
              const seg = (
                <circle
                  key={d.label}
                  cx="80"
                  cy="80"
                  r={radius}
                  fill="none"
                  stroke={d.color || PALETTE[i % PALETTE.length]}
                  strokeWidth={stroke}
                  strokeDasharray={`${dash} ${circ - dash}`}
                  strokeDashoffset={-offset}
                />
              );
              offset += dash;
              return seg;
            })}
        </svg>

        <div className="space-y-2">
          {total === 0 && <p className="text-sm text-slate-400">No data yet.</p>}
          {data.map((d, i) => (
            <div key={d.label} className="flex items-center gap-2 text-sm">
              <span
                className="inline-block h-3 w-3 rounded-sm"
                style={{ backgroundColor: d.color || PALETTE[i % PALETTE.length] }}
              />
              <span className="text-slate-600">{d.label}</span>
              <span className="ml-auto tabular-nums font-medium text-slate-800">{d.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
