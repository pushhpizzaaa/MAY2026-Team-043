import React from 'react';
import { CATEGORIES } from '../../data/mockData';

export default function SubmitProof({ 
  progress, selectedCategory, setSelectedCategory, 
  selectedEventId, setSelectedEventId, events, 
  proofNote, setProofNote, handleVolunteerSubmitProof 
}) {
  return (
    <div className="max-w-xl mx-auto bg-white border border-slate-200 rounded-2xl shadow-md p-6">
      <h3 className="text-xl font-bold text-slate-900 mb-2">File Completed Field Documentation</h3>
      <p className="text-xs text-slate-500 mb-6">Enforcing strict server-side schema parameters: Only non-locked stars are selectable.</p>
      
      <form onSubmit={handleVolunteerSubmitProof} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Target Category Layer</label>
          <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 bg-white outline-none">
            {CATEGORIES.map(c => {
              const isLocked = progress.some(p => p.category_id === c.id && p.completed);
              return (
                <option key={c.id} value={c.id} disabled={isLocked}>
                  {c.name} {isLocked ? '(🔒 Star Locked Solid)' : ''}
                </option>
              );
            })}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Optional Notice Board Link</label>
          <select value={selectedEventId} onChange={(e) => setSelectedEventId(e.target.value)} className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 bg-white outline-none">
            <option value="">Independent Operation (Not linked to notice board)</option>
            {events.map(e => <option key={e.id} value={e.id}>{e.title}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Field Activity Narrative (Proof Note)</label>
          <textarea required rows="3" value={proofNote} onChange={(e) => setProofNote(e.target.value)} placeholder="Provide contextual metadata describing operations performed..." className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
        </div>
        
        <button type="submit" className="w-full bg-indigo-600 text-white font-bold py-2 rounded-md hover:bg-indigo-700">Submit Verification</button>
      </form>
    </div>
  );
}