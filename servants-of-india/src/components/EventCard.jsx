export default function EventCard({ event }) {
  return (
    <div className="rounded-xl border border-stone/15 bg-white p-4 shadow-sm transition hover:shadow-md">
      <div className="mb-2 flex items-start justify-between gap-2">
        <h3 className="font-display text-base font-semibold leading-snug text-ink">{event.title}</h3>
        <span className="whitespace-nowrap rounded-full bg-chakra/10 px-2 py-0.5 text-[11px] font-semibold text-chakra">
          {event.category}
        </span>
      </div>
      <p className="mb-3 text-sm text-stone">{event.description}</p>
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone/80">
        <span>📅 {event.date}</span>
        <span>🕒 {event.time}</span>
        <span>📍 {event.address}</span>
      </div>
    </div>
  )
}
