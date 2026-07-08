import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getLocalStorageData, saveLocalStorageData } from '../../data/mockData';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState([]);
  const [events, setEvents] = useState([]);
  
  // Event Creation Form State
  const [eventTitle, setEventTitle] = useState('');
  const [eventCat, setEventCat] = useState("Women's Care");
  const [eventDate, setEventDate] = useState('2026-07-25');
  const [eventDesc, setEventDesc] = useState('');

  useEffect(() => {
    setSubmissions(getLocalStorageData('sob_submissions', []));
    setEvents(getLocalStorageData('sob_events', []));
  }, []);

  const handleReviewAction = (submissionId, actionResult) => {
    const updated = submissions.map(sub => 
      sub.id === submissionId ? { ...sub, status: actionResult } : sub
    );
    setSubmissions(updated);
    saveLocalStorageData('sob_submissions', updated);
  };

  const handlePostEvent = (e) => {
    e.preventDefault();
    if (!eventTitle.trim() || !eventDesc.trim()) {
      alert('Please fill out all missing fields.');
      return;
    }

    const newEvent = {
      id: 'evt-' + Date.now(),
      title: eventTitle,
      description: eventDesc,
      category_name: eventCat,
      venue: "Central Main Grounds",
      city: "Hyderabad",
      state: "Telangana",
      event_date: eventDate,
      status: "UPCOMING"
    };

    const updatedEvents = [...events, newEvent];
    setEvents(updatedEvents);
    saveLocalStorageData('sob_events', updatedEvents);
    
    setEventTitle('');
    setEventDesc('');
    alert('New active notice board item posted successfully!');
  };

  const pendingItems = submissions.filter(s => s.status === 'PENDING');

  return (
    <div className="min-h-screen bg-slate-100 text-slate-800">
      <header className="bg-slate-900 text-white px-6 py-4 flex justify-between items-center shadow-md">
        <div>
          <h1 className="text-xl font-extrabold tracking-tight">Super-Admin Centralized Desk</h1>
          <p className="text-xs text-slate-400">Servants of Bharat Verification Engine</p>
        </div>
        <button onClick={() => navigate('/')} className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 rounded font-semibold">
          Exit Operations
        </button>
      </header>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* CENTRAL PENDING QUEUE */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-lg font-bold text-slate-900 mb-2 flex items-center justify-between">
              <span>Incoming Evidence Verification Queue</span>
              <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-0.5 rounded-full">{pendingItems.length} Pending</span>
            </h2>
            <p className="text-xs text-slate-500 mb-4">Evaluate structural photo evidence assets and notes submitted by field coordinators.</p>

            {pendingItems.length === 0 ? (
              <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-xl bg-slate-50 text-slate-400 font-medium text-sm">
                No pipeline validation actions waiting in queue.
              </div>
            ) : (
              <div className="space-y-4">
                {pendingItems.map(sub => (
                  <div key={sub.id} className="p-4 rounded-xl border border-slate-200 bg-white shadow-sm grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <img src={sub.imageUrl} alt="Proof Asset" className="w-full h-32 object-cover rounded-lg border border-slate-200 bg-slate-100" />
                    <div className="sm:col-span-2 flex flex-col justify-between">
                      <div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-amber-700 uppercase bg-amber-50 px-2 py-0.5 rounded">{sub.categoryName}</span>
                          <span className="text-xs text-slate-400">{sub.timestamp}</span>
                        </div>
                        <h4 className="font-bold text-slate-900 mt-1 text-sm">By: {sub.volunteerName}</h4>
                        <p className="text-xs text-slate-600 mt-1 italic">"{sub.note}"</p>
                      </div>
                      <div className="flex space-x-2 mt-3">
                        <button onClick={() => handleReviewAction(sub.id, 'APPROVED')} className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold py-1.5 rounded transition shadow-sm">
                          Approve Milestone
                        </button>
                        <button onClick={() => handleReviewAction(sub.id, 'REJECTED')} className="flex-1 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold py-1.5 rounded transition shadow-sm">
                          Reject Proof
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* POST EVENT MANAGEMENT */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="text-base font-bold text-slate-900 mb-3">Broadcast Notice Board Event</h3>
            <form onSubmit={handlePostEvent} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase">Event Heading Title</label>
                <input type="text" required value={eventTitle} onChange={(e) => setEventTitle(e.target.value)} placeholder="e.g., Blood Donation Camp Setup" className="mt-1 block w-full p-2 border border-slate-300 rounded text-sm shadow-sm" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase">Target Core Category</label>
                <select value={eventCat} onChange={(e) => setEventCat(e.target.value)} className="mt-1 block w-full p-2 border border-slate-300 rounded text-sm bg-white shadow-sm">
                  <option>Women's Care</option><option>Child Welfare</option><option>Elder Care & Orphanage</option><option>Environmental Plantation</option><option>Blood Donation</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase">Event Date</label>
                <input type="date" required value={eventDate} onChange={(e) => setEventDate(e.target.value)} className="mt-1 block w-full p-2 border border-slate-300 rounded text-sm shadow-sm" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase">Operational Description Details</label>
                <textarea rows="3" required value={eventDesc} onChange={(e) => setEventDesc(e.target.value)} placeholder="Provide venue context, instructions, time allocations..." className="mt-1 block w-full p-2 border border-slate-300 rounded text-sm shadow-sm" />
              </div>
              <button type="submit" className="w-full py-2 bg-slate-900 text-white font-bold rounded text-xs uppercase tracking-wider hover:bg-slate-800 transition shadow-md">
                Publish Event
              </button>
            </form>
          </div>

          {/* AGGREGATE STATS SYSTEM */}
          <div className="bg-slate-900 text-slate-100 p-4 rounded-xl shadow-md border border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">System Metrics Overview</h4>
            <div className="grid grid-cols-2 gap-2 text-center">
              <div className="bg-slate-800 p-3 rounded-lg">
                <div className="text-lg font-extrabold text-amber-400">{getLocalStorageData('sob_users', []).length}</div>
                <div className="text-[10px] uppercase text-slate-400 font-medium">Volunteers</div>
              </div>
              <div className="bg-slate-800 p-3 rounded-lg">
                <div className="text-lg font-extrabold text-emerald-400">{submissions.filter(s => s.status === 'APPROVED').length}</div>
                <div className="text-[10px] uppercase text-slate-400 font-medium">Stars Awarded</div>
              </div>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}