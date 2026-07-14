// Date/time formatting helpers.
//
// The backend stores timestamps in UTC. When SQLite returns them, the ISO string
// can arrive without a timezone offset (e.g. "2026-07-11T09:30:00"), which the
// browser would otherwise interpret as *local* time. We normalise such naive
// strings to UTC, then render everything in India Standard Time (Asia/Kolkata).

const IST = "Asia/Kolkata";

function toUtcDate(iso) {
  if (!iso) return null;
  // If the string has no timezone info (no trailing Z and no +hh:mm), treat as UTC.
  const hasTz = /[zZ]$|[+-]\d{2}:?\d{2}$/.test(iso);
  const normalized = hasTz ? iso : `${iso}Z`;
  const d = new Date(normalized);
  return isNaN(d.getTime()) ? null : d;
}

/** Full date + time in IST, e.g. "11 Jul 2026, 3:00 pm". */
export function formatDateTime(iso) {
  const d = toUtcDate(iso);
  if (!d) return "—";
  return d.toLocaleString("en-IN", {
    timeZone: IST,
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

/** Date only in IST, e.g. "11 Jul 2026". */
export function formatDate(iso) {
  const d = toUtcDate(iso);
  if (!d) return "—";
  return d.toLocaleDateString("en-IN", {
    timeZone: IST,
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}
