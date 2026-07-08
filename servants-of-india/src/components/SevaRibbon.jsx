// SevaRibbon: the signature visual for the 5-milestone progress board.
// Each milestone is a circular medallion strung along a ribbon line.
// empty   -> outlined circle, no fill
// pending -> dashed ring, amber fill (awaiting admin review)
// locked  -> solid filled circle with a locking ring (admin-approved)

const STATUS_STYLES = {
  empty: {
    circle: 'border-2 border-stone/30 bg-white',
    text: 'text-stone/60',
    badge: null,
  },
  pending: {
    circle: 'border-2 border-dashed border-saffron bg-saffron-light/30',
    text: 'text-saffron-dark',
    badge: 'Pending Review',
  },
  locked: {
    circle: 'border-4 border-leaf bg-leaf text-white shadow-md shadow-leaf/30',
    text: 'text-leaf-dark font-semibold',
    badge: 'Approved',
  },
}

export default function SevaRibbon({ milestones }) {
  return (
    <div className="w-full overflow-x-auto py-4">
      <div className="relative flex min-w-[560px] items-start justify-between px-4">
        {/* connecting ribbon line */}
        <div className="absolute left-8 right-8 top-8 h-[3px] bg-gradient-to-r from-saffron via-cream to-leaf" />

        {milestones.map((m) => {
          const style = STATUS_STYLES[m.status]
          return (
            <div key={m.id} className="relative z-10 flex w-24 flex-col items-center gap-2 text-center">
              <div
                className={`flex h-16 w-16 items-center justify-center rounded-full transition-all ${style.circle}`}
                aria-label={`${m.label}: ${m.status}`}
              >
                {m.status === 'locked' ? (
                  <svg viewBox="0 0 24 24" className="h-7 w-7" fill="currentColor">
                    <path d="M12 2 14.6 8.1 21.3 8.7 16.2 13.1 17.7 19.7 12 16.1 6.3 19.7 7.8 13.1 2.7 8.7 9.4 8.1Z" />
                  </svg>
                ) : (
                  <span className={`text-xs font-body ${style.text}`}>{m.status === 'pending' ? '…' : ''}</span>
                )}
              </div>
              <p className="font-body text-xs font-semibold leading-tight text-ink">{m.label}</p>
              {style.badge && (
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                    m.status === 'locked' ? 'bg-leaf/10 text-leaf-dark' : 'bg-saffron/10 text-saffron-dark'
                  }`}
                >
                  {style.badge}
                </span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
