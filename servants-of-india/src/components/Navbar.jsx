import React from 'react';
import NotificationBell from './NotificationBell';

export default function Navbar({ currentRole, currentPage, setCurrentPage, user, submissions, notifications }) {
  return (
    <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 h-16 flex justify-between items-center">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentPage('landing')}>
          <div className="w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center text-white font-black text-xl">🇮🇳</div>
          <div>
            <h1 className="font-bold text-lg leading-tight tracking-tight text-slate-900">SERVANTS OF BHARAT</h1>
            <p className="text-2xs uppercase tracking-widest text-indigo-600 font-bold">National Service Tracker</p>
          </div>
        </div>

        <nav className="flex items-center gap-6 text-sm font-medium">
          {currentRole === 'PUBLIC' && (
            <>
              <button onClick={() => setCurrentPage('landing')} className="text-slate-600 hover:text-indigo-600">Home</button>
              <button onClick={() => setCurrentPage('verify')} className="text-slate-600 hover:text-indigo-600">Verify Certificate</button>
              <button onClick={() => setCurrentPage('auth')} className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition">Portal Login</button>
            </>
          )}

          {currentRole === 'VOLUNTEER' && (
            <>
              <button onClick={() => setCurrentPage('dashboard')} className={`transition ${currentPage === 'dashboard' ? 'text-indigo-600 underline' : 'text-slate-600 hover:text-indigo-600'}`}>Milestones</button>
              <button onClick={() => setCurrentPage('events')} className={`transition ${currentPage === 'events' ? 'text-indigo-600 underline' : 'text-slate-600 hover:text-indigo-600'}`}>Notice Board</button>
              <button onClick={() => setCurrentPage('submit')} className="bg-indigo-600 text-white px-3 py-1.5 rounded-md hover:bg-indigo-700 text-xs">Submit Field Proof</button>
              <NotificationBell notifications={notifications} />
            </>
          )}

          {currentRole === 'ADMIN' && (
            <>
              <button onClick={() => setCurrentPage('review')} className={`relative transition ${currentPage === 'review' ? 'text-indigo-600 underline' : 'text-slate-600 hover:text-indigo-600'}`}>
                Review Queue
                {submissions.filter(s => s.status === 'PENDING').length > 0 && (
                  <span className="ml-1.5 bg-indigo-600 text-white text-3xs px-1.5 py-0.5 rounded-full font-bold">
                    {submissions.filter(s => s.status === 'PENDING').length}
                  </span>
                )}
              </button>
              <button onClick={() => setCurrentPage('events')} className={`transition ${currentPage === 'events' ? 'text-indigo-600 underline' : 'text-slate-600 hover:text-indigo-600'}`}>Manage Notice Board</button>
              <button onClick={() => setCurrentPage('users')} className={`transition ${currentPage === 'users' ? 'text-indigo-600 underline' : 'text-slate-600 hover:text-indigo-600'}`}>Volunteers Audit</button>
              <div className="bg-slate-100 px-3 py-1 rounded text-xs text-slate-700 font-mono">👑 {user.role}</div>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}