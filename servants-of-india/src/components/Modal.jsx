export default function Modal({ open, onClose, title, children, wide = false }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-slate-950/70 p-4 backdrop-blur-xs">
      <div
        className={`mt-10 w-full ${wide ? "max-w-2xl" : "max-w-lg"} rounded-xl border border-amber-300 bg-white shadow-2xl text-slate-800`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-amber-200 px-6 py-4">
          <h3 className="text-lg font-black text-blue-900">{title}</h3>
          <button onClick={onClose} className="rounded-lg p-1 text-slate-400 hover:bg-amber-100 hover:text-slate-700">✕</button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}