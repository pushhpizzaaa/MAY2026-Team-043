import React from 'react';
import { CATEGORIES } from '../App';

export default function StarTracker({ progress, submissions }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-5 gap-4">
      {CATEGORIES.map(cat => {
        const isApproved = progress.some(p => p.category_id === cat.id && p.completed);
        const isPending = !isApproved && submissions.some(s => s.category_id === cat.id && s.status === 'PENDING');
        
        let cardStyle = "border-slate-200 bg-slate-50 text-slate-400";
        let starSymbol = "☆";
        let statusLabel = "Not Started";

        if (isApproved) {
          cardStyle = "border-emerald-300 bg-emerald-50 text-emerald-700 shadow-xs";
          starSymbol = "★";
          statusLabel = "Locked Solid";
        } else if (isPending) {
          cardStyle = "border-amber-300 bg-amber-50 text-amber-700 animate-pulse";
          starSymbol = "⏳";
          statusLabel = "Pending Admin Review";
        }

        return (
          <div key={cat.id} className={`border-2 rounded-xl p-4 text-center flex flex-col items-center transition-all ${cardStyle}`}>
            <div className="text-3xl mb-1">{starSymbol}</div>
            <p className="font-bold text-xs text-slate-900 leading-tight min-h-[32px] flex items-center justify-center">{cat.name}</p>
            <span className="text-3xs uppercase font-extrabold tracking-wider mt-2 px-2 py-0.5 rounded bg-white/60">{statusLabel}</span>
          </div>
        );
      })}
    </div>
  );
}