import React, { useState } from 'react';
import { CATEGORIES } from '../../App';

export default function CreateEvent({ events, setEvents, setCurrentPage }) {
  const [formData, setFormData] = useState({
    title: '',
    category_id: 1,
    venue: '',
    city: '',
    state: '',
    event_date: '',
    start_time: '',
    end_time: '',
    description: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    const createdEvent = {
      id: "e-" + Date.now(),
      ...formData,
      category_id: Number(formData.category_id),
      status: "UPCOMING"
    };

    setEvents([createdEvent, ...events]);
    alert("📢 Event broadcast successfully to the public notice board matrix!");
    setCurrentPage('events');
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="max-w-2xl mx-auto bg-white border border-slate-200 rounded-2xl shadow-md p-6">
      <div className="border-b pb-4 mb-6">
        <h3 className="text-xl font-bold text-slate-900">Broadcast New Field Operation Notice</h3>
        <p className="text-xs text-slate-500 mt-1">This populates directly on the decentralized public Notice Board replacing WhatsApp announcements.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Event Operation Title</label>
          <input type="text" name="title" required value={formData.title} onChange={handleChange} placeholder="e.g. Area-Wide Blood Collection Unit 3" className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Milestone Category Tag</label>
            <select name="category_id" value={formData.category_id} onChange={handleChange} className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 bg-white outline-none">
              {CATEGORIES.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Operation Date</label>
            <input type="date" name="event_date" required value={formData.event_date} onChange={handleChange} className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-1">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Venue / Building</label>
            <input type="text" name="venue" required value={formData.venue} onChange={handleChange} placeholder="Red Cross Hall" className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">City</label>
            <input type="text" name="city" required value={formData.city} onChange={handleChange} placeholder="Mumbai" className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">State Code</label>
            <input type="text" name="state" required maxLength="2" value={formData.state} onChange={handleChange} placeholder="MH" className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 text-center uppercase outline-none" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Start Time</label>
            <input type="time" name="start_time" required value={formData.start_time} onChange={handleChange} className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Expected End Time</label>
            <input type="time" name="end_time" required value={formData.end_time} onChange={handleChange} className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Operational Instructions & Scope</label>
          <textarea name="description" required rows="4" value={formData.description} onChange={handleChange} placeholder="State core assignment objective rules, parameters, and required items to verify volunteer attendance..." className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
        </div>

        <div className="flex justify-end gap-3 border-t pt-4">
          <button type="button" onClick={() => setCurrentPage('events')} className="text-xs font-bold text-slate-500 hover:underline">Cancel</button>
          <button type="submit" className="bg-indigo-600 text-white font-bold text-xs px-5 py-2.5 rounded-lg hover:bg-indigo-700 transition shadow-sm">
            Publish Event Stream
          </button>
        </div>
      </form>
    </div>
  );
}