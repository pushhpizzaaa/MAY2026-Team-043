import React from 'react';
import { CATEGORIES } from '../../App';

export default function NoticeBoard({ currentRole, events, setEvents, setCurrentPage }) {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div>
          <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">Public Field Operations Desk</h3>
          <p className="text-xs text-slate-500">Chronological real-world active events registry replacing ad-hoc chat channels.</p>
        </div>
        {currentRole === 'ADMIN' && (
          <button onClick={() => {
            const title = prompt("Enter Event Title:");
            if(!title) return;
            const catId = Number(prompt("Enter Category ID (1 to 5):", "1"));
            const venue = prompt("Enter Venue/Location:");
            const date = prompt("Enter Date (YYYY-MM-DD):", "2026-07-12");
            
            const created = {
              id: "e-" + Date.now(),
              title,
              category_id: catId,
              venue,
              city: "Local Grid",
              state: "IN",
              event_date: date,
              start_time: "10:00",
              end_time: "14:00",
              description: "Admin posted operating protocol.",
              status: "UPCOMING"
            };
            setEvents([created, ...events]);
          }} className="bg-indigo-600 text-white font-bold text-xs px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
            + Broadcast New Event
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {events.map(ev => (
          <div key={ev.id} className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden flex flex-col">
            <div className="p-4 bg-slate-50 border-b flex justify-between items-center">
              <span className="text-3xs uppercase font-extrabold tracking-widest bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded">
                {CATEGORIES.find(c => c.id === ev.category_id)?.name}
              </span>
              <span className="text-2xs font-mono text-slate-500 font-bold">{ev.event_date}</span>
            </div>
            <div className="p-4 flex-1 space-y-2">
              <h4 className="font-bold text-slate-900 text-base leading-snug">{ev.title}</h4>
              <p className="text-xs text-slate-600 line-clamp-3">{ev.description}</p>
              <div className="text-xs bg-slate-50 p-2 rounded text-slate-500 font-medium">
                📍 <strong>Venue:</strong> {ev.venue}, {ev.city} ({ev.state})
              </div>
            </div>
            <div className="p-4 border-t bg-slate-50/50 flex justify-end gap-2">
              {currentRole === 'VOLUNTEER' && ev.status === 'UPCOMING' && (
                <button onClick={() => setCurrentPage('submit')} className="bg-indigo-600 text-white text-2xs font-bold px-3 py-1.5 rounded hover:bg-indigo-700">
                  Attend & File Proof
                </button>
              )}
              {currentRole === 'ADMIN' && (
                <button onClick={() => setEvents(events.filter(e => e.id !== ev.id))} className="text-red-600 hover:bg-red-50 text-2xs px-3 py-1.5 rounded font-bold transition">
                  Archive Notice
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}