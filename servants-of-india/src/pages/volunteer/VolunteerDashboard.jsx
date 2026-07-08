import React from 'react';
import StarTracker from '../../components/StarTracker';
import { CATEGORIES } from '../../App';

export default function VolunteerDashboard({ user, progress, submissions, setCurrentPage }) {
  const totalApprovedStars = progress.filter(p => p.volunteer_id === user.id && p.completed).length;

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-indigo-900 to-slate-900 text-white p-6 rounded-2xl shadow-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-widest text-indigo-300">Seasonal Active Quarter Window</h3>
          <p className="text-xl font-bold mt-1">Quarter 3 Tracking Cycle Resetting</p>
          <p className="text-xs text-slate-300 mt-1">Field-based operations require structured seasonal distribution to limit velocity spoofing.</p>
        </div>
        <div className="bg-white/10 backdrop-blur-xs px-4 py-3 rounded-xl border border-white/10 text-center self-stretch md:self-auto">
          <span className="block text-2xl font-black text-amber-400 font-mono">84 Days</span>
          <span className="text-3xs uppercase tracking-wider text-slate-300 font-bold">Remaining in Q3 Phase</span>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
        <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">Annual Service Progress Metrics (2026 Cycle)</h4>
        
        <StarTracker progress={progress} submissions={submissions} />

        {totalApprovedStars === 5 ? (
          <div className="mt-8 border-2 border-dashed border-indigo-500 bg-indigo-50 rounded-xl p-5 text-center">
            <h5 className="font-extrabold text-indigo-900 text-lg">🏆 Milestone Completed: 5/5 Stars Earned!</h5>
            <p className="text-xs text-indigo-700 mt-1 mb-4">Your core annual operations have successfully cleared decentralized validation protocols.</p>
            <button onClick={() => setCurrentPage('certificate')} className="bg-indigo-600 text-white text-xs font-bold px-5 py-2.5 rounded-lg hover:bg-indigo-700 transition shadow-sm">Customize and Issue Certificate</button>
          </div>
        ) : (
          <div className="mt-6 text-center text-xs text-slate-500 border-t pt-4">
            Complete all <strong>5 distinct categories</strong> to unlock automated QR Certificate production. Currently at <strong className="text-slate-800">{totalApprovedStars}/5 Stars</strong>.
          </div>
        )}
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
        <h4 className="text-sm font-bold text-slate-900 mb-4">Your Submission Audit History</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-100 text-slate-600 uppercase tracking-wider text-2xs border-b">
                <th className="p-3">Category</th>
                <th className="p-3">Note Detail</th>
                <th className="p-3">Quarter Matrix</th>
                <th className="p-3">Current Status</th>
                <th className="p-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {submissions.filter(s => s.volunteer_id === user.id).map(sub => (
                <tr key={sub.id} className="hover:bg-slate-50">
                  <td className="p-3 font-semibold text-slate-900">{CATEGORIES.find(c => c.id === sub.category_id)?.name}</td>
                  <td className="p-3 text-slate-600 max-w-xs truncate">{sub.note}</td>
                  <td className="p-3 font-mono">Q{sub.quarter} ({sub.service_year})</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded font-bold text-2xs ${sub.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' : sub.status === 'PENDING' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'}`}>
                      {sub.status}
                    </span>
                  </td>
                  <td className="p-3 text-slate-400 font-mono">{sub.submitted_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}