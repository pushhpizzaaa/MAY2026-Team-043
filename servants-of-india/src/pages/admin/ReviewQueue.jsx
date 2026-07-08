import React, { useState } from 'react';
import { CATEGORIES } from '../../App';

export default function ReviewQueue({ submissions, setSubmissions, setProgress, progress, notifications, setNotifications }) {
  const [activeReview, setActiveReview] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('Blurry Image');
  const [rejectionRemarks, setRejectionRemarks] = useState('');

  const handleAdminReview = (subId, decision) => {
    setSubmissions(submissions.map(sub => sub.id === subId ? { ...sub, status: decision } : sub));
    const targetedSub = submissions.find(s => s.id === subId);

    if (decision === 'APPROVED') {
      setProgress([...progress, { volunteer_id: targetedSub.volunteer_id, category_id: targetedSub.category_id, service_year: 2026, completed: true }]);
      setNotifications([{
        id: "n-" + Date.now(),
        user_id: targetedSub.volunteer_id,
        title: "Submission Approved ✨",
        message: `Your proof for ${CATEGORIES.find(c => c.id === targetedSub.category_id).name} matches rules. Star issued!`,
        is_read: false
      }, ...notifications]);
    } else {
      setNotifications([{
        id: "n-" + Date.now(),
        user_id: targetedSub.volunteer_id,
        title: "Submission Rejected ❌",
        message: `Reason: ${rejectionReason}. Remarks: ${rejectionRemarks}`,
        is_read: false
      }, ...notifications]);
    }
    setActiveReview(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-2xl font-extrabold text-slate-900">Centralized Proof Processing Queue</h3>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-3">
          {submissions.filter(s => s.status === 'PENDING').map(sub => (
            <div key={sub.id} onClick={() => setActiveReview(sub)} className={`bg-white border p-4 rounded-xl cursor-pointer ${activeReview?.id === sub.id ? 'ring-2 ring-indigo-500' : 'border-slate-200'}`}>
              <p className="text-sm font-semibold text-indigo-900">{CATEGORIES.find(c => c.id === sub.category_id)?.name}</p>
              <p className="text-xs text-slate-600 mt-1 italic">"{sub.note}"</p>
            </div>
          ))}
        </div>

        <div className="bg-white border rounded-2xl p-4 shadow-sm h-fit space-y-4">
          {activeReview ? (
            <div className="space-y-4">
              <img src={activeReview.image_url} alt="Proof" className="w-full h-40 object-cover rounded-lg border" />
              <button onClick={() => handleAdminReview(activeReview.id, 'APPROVED')} className="w-full bg-emerald-600 text-white font-bold text-xs py-2 rounded-lg">✓ Grant Milestone Star</button>
              <div className="border p-2 rounded bg-slate-50 space-y-2">
                <select value={rejectionReason} onChange={(e) => setRejectionReason(e.target.value)} className="w-full text-2xs border rounded p-1">
                  <option value="Blurry Image">Blurry Image</option>
                  <option value="Wrong Quarter">Wrong Quarter boundary</option>
                </select>
                <input type="text" placeholder="Remarks..." value={rejectionRemarks} onChange={(e) => setRejectionRemarks(e.target.value)} className="w-full text-2xs border p-1 rounded" />
                <button onClick={() => handleAdminReview(activeReview.id, 'REJECTED')} className="w-full bg-red-600 text-white font-bold text-2xs py-1.5 rounded">⚠️ Reject Proof</button>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic text-center py-12">Select an item from the queue list to inspect details.</p>
          )}
        </div>
      </div>
    </div>
  );
}