import React from 'react';
import { CATEGORIES } from '../../App';

export default function LandingPage({ setCurrentPage, setCurrentRole }) {
  return (
    <div className="py-12 text-center max-w-3xl mx-auto">
      <span className="bg-indigo-50 text-indigo-700 font-bold px-3 py-1 rounded-full text-xs uppercase tracking-wider">Replacing fragmented WhatsApp Coordination</span>
      <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mt-4 mb-6">One Verified Framework for Nationwide Impact</h2>
      <p className="text-lg text-slate-600 mb-8 leading-relaxed">Discover localized service operations, submit bulletproof visual documentation, unlock annual milestone stars, and get instant QR-verifiable certification upon completion.</p>
      <div className="flex justify-center gap-4">
        <button onClick={() => { setCurrentRole('VOLUNTEER'); setCurrentPage('dashboard'); }} className="bg-indigo-600 text-white font-semibold px-6 py-3 rounded-lg shadow-md hover:bg-indigo-700 transition">Sign Up as Volunteer</button>
        <button onClick={() => setCurrentPage('verify')} className="bg-white border border-slate-300 text-slate-700 font-semibold px-6 py-3 rounded-lg hover:bg-slate-50 transition">Verify a QR Certificate</button>
      </div>
      
      <div className="mt-16 grid grid-cols-2 md:grid-cols-5 gap-4">
        {CATEGORIES.map(c => (
          <div key={c.id} className="bg-white p-4 border border-slate-200 rounded-xl text-center shadow-xs">
            <div className="text-2xl mb-2">⭐</div>
            <p className="font-bold text-xs text-slate-900">{c.name}</p>
          </div>
        ))}
      </div>
    </div>
  );
}