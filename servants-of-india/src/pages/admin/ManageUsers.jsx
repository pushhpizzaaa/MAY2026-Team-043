import React from 'react';

export default function ManageUsers() {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-slate-900">Super Admin User Enforcement Portal</h3>
        <p className="text-xs text-slate-500">Perform account status overrides (Rule 15 constraint enforcement layer).</p>
      </div>
      <table className="w-full text-left text-xs">
        <thead>
          <tr className="bg-slate-100 border-b font-bold text-slate-600">
            <th className="p-3">Full Identity Block</th>
            <th className="p-3">Electronic Coordinates</th>
            <th className="p-3">Assigned Role Context</th>
            <th className="p-3 text-right">Enforcement Directives</th>
          </tr>
        </thead>
        <tbody className="divide-y text-slate-700">
          <tr className="hover:bg-slate-50">
            <td className="p-3 font-semibold text-slate-900">Rajesh Kumar</td>
            <td className="p-3">rajesh@bharat.org</td>
            <td className="p-3"><span className="bg-slate-100 px-2 py-0.5 rounded font-mono text-2xs">VOLUNTEER</span></td>
            <td className="p-3 text-right">
              <button onClick={() => alert("User frozen.")} className="text-red-600 font-bold text-2xs">Block Account</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}