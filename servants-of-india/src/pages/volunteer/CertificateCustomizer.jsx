import React from 'react';

export default function CertificateCustomizer({ user, setCurrentPage, setVerificationCode }) {
  return (
    <div className="max-w-2xl mx-auto bg-white border border-slate-200 rounded-2xl shadow-xl p-6 my-4">
      <h3 className="text-xl font-bold text-slate-900 mb-2">Step 8.5: Automated Certificate Production Customizer</h3>
      <p className="text-xs text-slate-500 mb-6">Confirm parameters. Once committed to the schema ledger, this specific document structure locks permanently.</p>
      
      <div className="border p-6 bg-slate-900 text-white rounded-xl text-center space-y-4 relative overflow-hidden">
        <div className="absolute top-2 right-2 bg-indigo-600 text-white text-3xs font-mono font-bold px-2 py-0.5 rounded">PREVIEW WORKSPACE</div>
        <p className="text-amber-400 text-xs font-black tracking-widest uppercase">ANNUAL ACCREDITATION CERTIFICATE</p>
        <h4 className="text-2xl font-serif tracking-wide">{user.full_name}</h4>
        <p className="text-slate-400 text-2xs max-w-md mx-auto leading-relaxed">Has successfully driven distinct field-based operations across all 5 mandatory societal matrix categories during the 2026 program runtime.</p>
        <div className="border-t border-slate-800 pt-4 flex justify-between items-center px-6 text-3xs font-mono text-slate-500">
          <div>ID Sequence: SOB-2026-MOCK</div>
          <div className="w-12 h-12 bg-white flex items-center justify-center text-black font-black text-xs">QR</div>
        </div>
      </div>

      <div className="mt-6 flex justify-end gap-3">
        <button onClick={() => setCurrentPage('dashboard')} className="text-xs font-bold text-slate-500">Back</button>
        <button onClick={() => { alert("📜 PDF Generated successfully."); setCurrentPage('verify'); setVerificationCode('SOB-2026-MOCK'); }} className="bg-indigo-600 text-white font-bold text-xs px-4 py-2 rounded-lg hover:bg-indigo-700">
          Finalize & Generate Immutable Output
        </button>
      </div>
    </div>
  );
}