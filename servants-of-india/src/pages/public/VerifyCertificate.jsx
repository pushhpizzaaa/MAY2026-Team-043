import React from 'react';

export default function VerifyCertificate({ verificationCode, setVerificationCode }) {
  return (
    <div className="max-w-xl mx-auto bg-white border border-slate-200 rounded-2xl shadow-md p-6 my-8 text-center">
      <h3 className="text-2xl font-black text-slate-900 mb-2">Immutable Certificate Audit Matrix</h3>
      <p className="text-sm text-slate-500 mb-6">Enter the validation sequence printed adjacent to the tracking QR code.</p>
      
      <div className="flex gap-2 max-w-md mx-auto mb-6">
        <input type="text" value={verificationCode} onChange={(e) => setVerificationCode(e.target.value)} placeholder="e.g. SOB-2026-991A2" className="flex-1 uppercase font-mono text-sm border rounded-lg p-2.5 text-center focus:ring-2 focus:ring-indigo-500 outline-none" />
        <button onClick={() => setVerificationCode('SOB-2026-MOCK')} className="bg-slate-900 text-white px-4 text-xs font-bold rounded-lg hover:bg-slate-800">Fill Sample</button>
      </div>

      {verificationCode === 'SOB-2026-MOCK' && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 text-left animate-fadeIn">
          <div className="flex items-center gap-2 text-emerald-800 font-bold mb-3 text-sm">
            <span className="text-base">✅</span> CRYPTOGRAPHICALLY VALID DOCUMENT RECORD
          </div>
          <div className="grid grid-cols-2 gap-y-3 text-xs border-t border-emerald-100 pt-3">
            <div><span className="text-slate-500 block">Accredited Volunteer</span> <strong className="text-slate-800 text-sm">Rajesh Kumar</strong></div>
            <div><span className="text-slate-500 block">Accredited Body</span> <strong className="text-slate-800 text-sm">Bharat Youth Club</strong></div>
            <div><span className="text-slate-500 block">Service Program Cycle</span> <strong className="text-slate-800 text-sm">Calendar Year 2026</strong></div>
            <div><span className="text-slate-500 block">Status Structure</span> <strong className="text-emerald-700 text-sm">5 / 5 Stars Verified</strong></div>
          </div>
        </div>
      )}
    </div>
  );
}