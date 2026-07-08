import React, { useState, useEffect } from 'react';

// --- MOCK DATABASE SEED DATA (Per Section 9 & 6 of PRD) ---
const CATEGORIES = [
  { id: 1, name: "Women's Care", description: "Empowerment and care initiatives" },
  { id: 2, name: "Child Welfare", description: "Education and support frameworks" },
  { id: 3, name: "Elder Care & Orphanage", description: "Support for senior homes and orphanages" },
  { id: 4, name: "Environmental Plantation", description: "Tree plantation and green drives" },
  { id: 5, name: "Blood Donation", description: "Lifesaving blood donation camps" }
];

const INITIAL_EVENTS = [
  { id: "e1", title: "Mega Blood Donation Camp 2026", category_id: 5, venue: "Red Cross Hall", city: "Mumbai", state: "MH", event_date: "2026-07-15", start_time: "09:00", end_time: "17:00", description: "Urgent need for O negative and B positive donors.", status: "UPCOMING" },
  { id: "e2", title: "Green Plantation Drive", category_id: 4, venue: "Sanjay Gandhi National Park", city: "Mumbai", state: "MH", event_date: "2026-07-20", start_time: "07:00", end_time: "11:00", description: "Planting 500 indigenous saplings.", status: "UPCOMING" },
  { id: "e3", title: "Digital Literacy for Children", category_id: 2, venue: "Community Center", city: "Delhi", state: "DL", event_date: "2026-06-10", start_time: "10:00", end_time: "13:00", description: "Teaching basic computer skills.", status: "COMPLETED" }
];

export default function App() {
  // Global View Swapper for Client Demo
  const [currentRole, setCurrentRole] = useState('PUBLIC'); // PUBLIC, VOLUNTEER, ADMIN
  const [currentPage, setCurrentPage] = useState('landing'); // landing, auth, verify, dashboard, events, submit, review, users
  
  // App States
  const [user, setUser] = useState({
    id: "u-vol-1",
    full_name: "Rajesh Kumar",
    email: "rajesh@bharat.org",
    role: "VOLUNTEER",
    organization_name: "Bharat Youth Club",
    location: "Mumbai"
  });

  const [events, setEvents] = useState(INITIAL_EVENTS);
  const [submissions, setSubmissions] = useState([
    { id: "s1", volunteer_id: "u-vol-1", event_id: "e3", category_id: 2, image_url: "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=400", note: "Conducted 3-hour scratch programming workshop.", service_year: 2026, quarter: 2, status: "APPROVED", submitted_at: "2026-06-10" }
  ]);
  
  const [progress, setProgress] = useState([
    { volunteer_id: "u-vol-1", category_id: 2, service_year: 2026, completed: true }
  ]);

  const [notifications, setNotifications] = useState([
    { id: "n1", user_id: "u-vol-1", title: "Submission Approved 🎉", message: "Your submission for Child Welfare has been approved. 1 Star Added!", type: "APPROVAL", is_read: false }
  ]);

  const [verificationCode, setVerificationCode] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(1);
  const [selectedEventId, setSelectedEventId] = useState('');
  const [proofNote, setProofNote] = useState('');
  const [proofImage, setProofImage] = useState('https://images.unsplash.com/photo-1593113598332-cd288d649433?w=500');

  // New Event Form State
  const [newEvent, setNewEvent] = useState({ title: '', category_id: 1, venue: '', city: '', state: '', event_date: '', start_time: '', end_time: '', description: '' });

  // Admin Review State
  const [activeReview, setActiveReview] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('Blurry Image');
  const [rejectionRemarks, setRejectionRemarks] = useState('');

  // --- BUSINESS RULES & COMPUTE CONTROLLERS ---
  const daysLeftInQuarter = () => {
    const now = new Date('2026-07-08');
    const q3End = new Date('2026-09-30');
    return Math.ceil((q3End - now) / (1000 * 60 * 60 * 24));
  };

  const handleVolunteerSubmitProof = (e) => {
    e.preventDefault();
    
    // Check Rule 10: Seasonal Quarterly Limits
    const currentQuarter = 3; // July is Q3
    const isFieldBased = selectedCategory !== 5; // 5 is Blood Donation (Exempt)
    const alreadySubmittedThisQuarter = submissions.some(s => 
      s.volunteer_id === user.id && 
      s.category_id === Number(selectedCategory) && 
      s.quarter === currentQuarter && 
      s.status !== 'REJECTED'
    );

    if (isFieldBased && alreadySubmittedThisQuarter) {
      alert("❌ PRD Business Rule Warning: You have already made a submission for this field-based milestone category this quarter!");
      return;
    }

    const newSub = {
      id: "s-" + Date.now(),
      volunteer_id: user.id,
      event_id: selectedEventId || null,
      category_id: Number(selectedCategory),
      image_url: proofImage,
      note: proofNote,
      service_year: 2026,
      quarter: currentQuarter,
      status: "PENDING",
      submitted_at: new Date().toISOString().split('T')[0]
    };

    setSubmissions([newSub, ...submissions]);
    setNotifications([{
      id: "n-" + Date.now(),
      user_id: user.id,
      title: "Proof Uploaded",
      message: "Your verification request is pending human admin review.",
      type: "SYSTEM",
      is_read: false
    }, ...notifications]);

    alert("✅ Proof submitted successfully to the centralized Admin Queue!");
    setCurrentPage('dashboard');
    setProofNote('');
  };

  const handleAdminReview = (subId, decision) => {
    const updatedSubmissions = submissions.map(sub => {
      if (sub.id === subId) {
        return { ...sub, status: decision };
      }
      return sub;
    });
    setSubmissions(updatedSubmissions);

    const targetedSub = submissions.find(s => s.id === subId);

    if (decision === 'APPROVED') {
      // Add progress entry
      setProgress([...progress, { volunteer_id: targetedSub.volunteer_id, category_id: targetedSub.category_id, service_year: 2026, completed: true }]);
      
      // Notify Volunteer
      setNotifications([{
        id: "n-" + Date.now(),
        user_id: targetedSub.volunteer_id,
        title: "Submission Approved ✨",
        message: `Your proof for ${CATEGORIES.find(c => c.id === targetedSub.category_id).name} matches standard procedures. Star issued!`,
        type: "APPROVAL",
        is_read: false
      }, ...notifications]);
    } else {
      // Notify with strict structured reason (Rule 16)
      setNotifications([{
        id: "n-" + Date.now(),
        user_id: targetedSub.volunteer_id,
        title: "Submission Rejected ❌",
        message: `Reason: ${rejectionReason}. Remarks: ${rejectionRemarks || 'None Provided'}`,
        type: "REJECTION",
        is_read: false
      }, ...notifications]);
    }
    setActiveReview(null);
    setRejectionRemarks('');
  };

  const totalApprovedStars = progress.filter(p => p.volunteer_id === user.id && p.completed).length;

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800 flex flex-col">
      
      {/* --- TOP ENVIRONMENT TOGGLE SWITCHER (FOR CLIENT DEMO PRESENTATIONS) --- */}
      <div className="bg-amber-500 text-white px-4 py-2 flex flex-wrap justify-between items-center text-xs font-semibold gap-2 border-b border-amber-600 shadow-inner">
        <div> </div>
        <div className="flex gap-2">
          <button onClick={() => { setCurrentRole('PUBLIC'); setCurrentPage('landing'); }} className={`px-3 py-1 rounded transition ${currentRole === 'PUBLIC' ? 'bg-slate-900 text-white' : 'bg-amber-600 hover:bg-amber-700'}`}>🌐 Public Portal View</button>
          <button onClick={() => { setCurrentRole('VOLUNTEER'); setCurrentPage('dashboard'); setUser(p => ({...p, role: 'VOLUNTEER'})); }} className={`px-3 py-1 rounded transition ${currentRole === 'VOLUNTEER' ? 'bg-slate-900 text-white' : 'bg-amber-600 hover:bg-amber-700'}`}>🤝 Volunteer Dashboard</button>
          <button onClick={() => { setCurrentRole('ADMIN'); setCurrentPage('review'); setUser(p => ({...p, role: 'SUPER ADMIN'})); }} className={`px-3 py-1 rounded transition ${currentRole === 'ADMIN' ? 'bg-slate-900 text-white' : 'bg-amber-600 hover:bg-amber-700'}`}>🛠️ Admin Command Desk</button>
        </div>
      </div>

      {/* --- SITE HEADER --- */}
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
                
                {/* Notification Badge Widget */}
                <div className="relative group cursor-pointer">
                  <span className="text-lg">🔔</span>
                  {notifications.filter(n => !n.is_read).length > 0 && (
                    <span className="absolute -top-1 -right-2 bg-red-500 text-white text-3xs w-4 h-4 rounded-full flex items-center justify-center font-bold">
                      {notifications.filter(n => !n.is_read).length}
                    </span>
                  )}
                  {/* Quick Preview Dropdown */}
                  <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-lg shadow-xl py-2 hidden group-hover:block z-50">
                    <p className="px-4 py-1 font-bold text-xs border-b text-slate-500">Live In-App Updates</p>
                    {notifications.map(n => (
                      <div key={n.id} className="p-3 text-xs border-b hover:bg-slate-50">
                        <p className="font-semibold text-slate-900">{n.title}</p>
                        <p className="text-slate-600 mt-0.5">{n.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
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

      {/* --- CORE ROUTING CONTAINER --- */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">
        
        {/* ========================================================= */}
        {/* PUBLIC: LANDING PAGE                                      */}
        {/* ========================================================= */}
        {currentRole === 'PUBLIC' && currentPage === 'landing' && (
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
        )}

        {/* ========================================================= */}
        {/* PUBLIC: AUTH PAGE                                         */}
        {/* ========================================================= */}
        {currentPage === 'auth' && (
          <div className="max-w-md mx-auto bg-white border border-slate-200 rounded-2xl shadow-xl p-6 my-8">
            <h3 className="text-xl font-bold text-slate-900 mb-2">Access the Servants of Bharat Grid</h3>
            <p className="text-xs text-slate-500 mb-6">Open open-signup layer — no corporate or collegiate pre-approval necessary.</p>
            <form onSubmit={(e) => { e.preventDefault(); setCurrentRole('VOLUNTEER'); setCurrentPage('dashboard'); }} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Email Coordinates</label>
                <input type="email" required placeholder="volunteer@bharat.org" className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Password</label>
                <input type="password" required placeholder="••••••••" className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
              </div>
              <button type="submit" className="w-full bg-indigo-600 text-white font-bold py-2.5 rounded-lg text-sm hover:bg-indigo-700 transition shadow-sm">Secure Authentication</button>
            </form>
          </div>
        )}

        {/* ========================================================= */}
        {/* PUBLIC: CERTIFICATE VERIFICATION PAGE                     */}
        {/* ========================================================= */}
        {currentPage === 'verify' && (
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
        )}

        {/* ========================================================= */}
        {/* VOLUNTEER: DASHBOARD & PROGRESS MAP                      */}
        {/* ========================================================= */}
        {currentRole === 'VOLUNTEER' && currentPage === 'dashboard' && (
          <div className="space-y-6">
            
            {/* Countdown Widget Section */}
            <div className="bg-gradient-to-r from-indigo-900 to-slate-900 text-white p-6 rounded-2xl shadow-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-widest text-indigo-300">Seasonal Active Quarter Window</h3>
                <p className="text-xl font-bold mt-1">Quarter 3 Tracking Cycle Resetting</p>
                <p className="text-xs text-slate-300 mt-1">Field-based operations require structured seasonal distribution to limit velocity spoofing.</p>
              </div>
              <div className="bg-white/10 backdrop-blur-xs px-4 py-3 rounded-xl border border-white/10 text-center self-stretch md:self-auto">
                <span className="block text-2xl font-black text-amber-400 font-mono">{daysLeftInQuarter()} Days</span>
                <span className="text-3xs uppercase tracking-wider text-slate-300 font-bold">Remaining in Q3 Phase</span>
              </div>
            </div>

            {/* 5-Star Milestone Tracker Box */}
            <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
              <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-6">Annual Service Progress Metrics (2026 Cycle)</h4>
              
              <div className="grid grid-cols-1 sm:grid-cols-5 gap-4">
                {CATEGORIES.map(cat => {
                  const isApproved = progress.some(p => p.category_id === cat.id && p.completed);
                  const isPending = !isApproved && submissions.some(s => s.category_id === cat.id && s.status === 'PENDING');
                  
                  let cardStyle = "border-slate-200 bg-slate-50 text-slate-400";
                  let starSymbol = "☆";
                  let statusLabel = "Not Started";

                  if (isApproved) {
                    cardStyle = "border-emerald-300 bg-emerald-50 text-emerald-700 shadow-xs";
                    starSymbol = "★";
                    statusLabel = "Locked Solid";
                  } else if (isPending) {
                    cardStyle = "border-amber-300 bg-amber-50 text-amber-700 animate-pulse";
                    starSymbol = "⏳";
                    statusLabel = "Pending Admin Review";
                  }

                  return (
                    <div key={cat.id} className={`border-2 rounded-xl p-4 text-center flex flex-col items-center transition-all ${cardStyle}`}>
                      <div className="text-3xl mb-1">{starSymbol}</div>
                      <p className="font-bold text-xs text-slate-900 leading-tight min-h-[32px] flex items-center justify-center">{cat.name}</p>
                      <span className="text-3xs uppercase font-extrabold tracking-wider mt-2 px-2 py-0.5 rounded bg-white/60">{statusLabel}</span>
                    </div>
                  );
                })}
              </div>

              {/* Automatic Certificate Reward Trigger View */}
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

            {/* Past Verification Records Ledger */}
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
        )}

        {/* ========================================================= */}
        {/* GENERAL: PUBLIC / VOLUNTEER NOTICE BOARD                   */}
        {/* ========================================================= */}
        {currentPage === 'events' && (
          <div className="space-y-6">
            <div className="flex flex-wrap justify-between items-center gap-4">
              <div>
                <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">Public Field Operations Desk</h3>
                <p className="text-xs text-slate-500">Chronological real-world active events registry replacing ad-hoc chat channels.</p>
              </div>
              {currentRole === 'ADMIN' && (
                <button onClick={() => {
                  const title = prompt("Enter Event Title:");
                  if(!title) return;
                  const catId = Number(prompt("Enter Category ID (1 to 5):", "1"));
                  const venue = prompt("Enter Venue/Location:");
                  const date = prompt("Enter Date (YYYY-MM-DD):", "2026-07-12");
                  
                  const created = {
                    id: "e-" + Date.now(),
                    title,
                    category_id: catId,
                    venue,
                    city: "Local Grid",
                    state: "IN",
                    event_date: date,
                    start_time: "10:00",
                    end_time: "14:00",
                    description: "Admin posted operating protocol.",
                    status: "UPCOMING"
                  };
                  setEvents([created, ...events]);
                }} className="bg-indigo-600 text-white font-bold text-xs px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
                  + Broadcast New Event
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {events.map(ev => (
                <div key={ev.id} className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden flex flex-col">
                  <div className="p-4 bg-slate-50 border-b flex justify-between items-center">
                    <span className="text-3xs uppercase font-extrabold tracking-widest bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded">
                      {CATEGORIES.find(c => c.id === ev.category_id)?.name}
                    </span>
                    <span className="text-2xs font-mono text-slate-500 font-bold">{ev.event_date}</span>
                  </div>
                  <div className="p-4 flex-1 space-y-2">
                    <h4 className="font-bold text-slate-900 text-base leading-snug">{ev.title}</h4>
                    <p className="text-xs text-slate-600 line-clamp-3">{ev.description}</p>
                    <div className="text-xs bg-slate-50 p-2 rounded text-slate-500 font-medium">
                      📍 <strong>Venue:</strong> {ev.venue}, {ev.city} ({ev.state})
                    </div>
                  </div>
                  <div className="p-4 border-t bg-slate-50/50 flex justify-end gap-2">
                    {currentRole === 'VOLUNTEER' && ev.status === 'UPCOMING' && (
                      <button onClick={() => { setSelectedCategory(ev.category_id); setSelectedEventId(ev.id); setCurrentPage('submit'); }} className="bg-indigo-600 text-white text-2xs font-bold px-3 py-1.5 rounded hover:bg-indigo-700">
                        Attend & File Proof
                      </button>
                    )}
                    {currentRole === 'ADMIN' && (
                      <button onClick={() => setEvents(events.filter(e => e.id !== ev.id))} className="text-red-600 hover:bg-red-50 text-2xs px-3 py-1.5 rounded font-bold transition">
                        Archive Notice
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* VOLUNTEER: SUBMIT PROOF FORM                              */}
        {/* ========================================================= */}
        {currentRole === 'VOLUNTEER' && currentPage === 'submit' && (
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
                <textarea required rows="3" value={proofNote} onChange={(e) => setProofNote(e.target.value)} placeholder="Provide contextual metadata describing operations performed, times, and measurable data points..." className="w-full text-sm border rounded-lg p-2.5 focus:ring-2 focus:ring-indigo-500 outline-none" />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">Simulated Image Upload (Mock URI)</label>
                <input type="text" value={proofImage} onChange={(e) => setProofImage(e.target.value)} className="w-full text-xs border rounded-lg p-2.5 font-mono bg-slate-50" />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setCurrentPage('dashboard')} className="text-xs font-bold text-slate-500 hover:underline">Cancel</button>
                <button type="submit" className="bg-indigo-600 text-white font-bold text-xs px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
                  Dispatch to Centralized Review Queue
                </button>
              </div>
            </form>
          </div>
        )}

        {/* ========================================================= */}
        {/* VOLUNTEER: CERTIFICATE CUSTOMIZATION SCREEN              */}
        {/* ========================================================= */}
        {currentPage === 'certificate' && (
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
              <button onClick={() => { alert("📜 PDF Generated & Dispatched to your profile registration coordinates via simulated SendGrid script."); setCurrentPage('verify'); setVerificationCode('SOB-2026-MOCK'); }} className="bg-indigo-600 text-white font-bold text-xs px-4 py-2 rounded-lg hover:bg-indigo-700">
                Finalize & Generate Immutable Output
              </button>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* ADMIN: ENHANCED REVIEW WORKSPACE QUEUE                     */}
        {/* ========================================================= */}
        {currentRole === 'ADMIN' && currentPage === 'review' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-2xl font-extrabold text-slate-900">Centralized Proof Processing Queue</h3>
              <p className="text-xs text-slate-500">Consolidated review interface replacing decentralized WhatsApp phone directories.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Queue Listing */}
              <div className="lg:col-span-2 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Awaiting Decision Ledger</h4>
                
                {submissions.filter(s => s.status === 'PENDING').length === 0 ? (
                  <div className="bg-white border border-dashed rounded-xl p-8 text-center text-slate-400 text-xs font-medium">
                    ✨ Clean Queue. All incoming operational proof files have been successfully audited!
                  </div>
                ) : (
                  submissions.filter(s => s.status === 'PENDING').map(sub => (
                    <div key={sub.id} onClick={() => setActiveReview(sub)} className={`bg-white border p-4 rounded-xl cursor-pointer shadow-2xs hover:border-indigo-400 transition ${activeReview?.id === sub.id ? 'ring-2 ring-indigo-500 border-transparent' : 'border-slate-200'}`}>
                      <div className="flex justify-between text-xs mb-2">
                        <span className="font-bold text-slate-900">Volunteer ID: {sub.volunteer_id}</span>
                        <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-bold text-3xs font-mono">Q{sub.quarter}</span>
                      </div>
                      <p className="text-sm font-semibold text-indigo-900">{CATEGORIES.find(c => c.id === sub.category_id)?.name}</p>
                      <p className="text-xs text-slate-600 mt-1 line-clamp-1 italic">"{sub.note}"</p>
                    </div>
                  ))
                )}
              </div>

              {/* Enhanced Interactive Review Sidebar Drawer */}
              <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm h-fit space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Live Inspection Sandbox</h4>
                
                {activeReview ? (
                  <div className="space-y-4 animate-fadeIn">
                    <img src={activeReview.image_url} alt="Proof Asset" className="w-full h-40 object-cover rounded-lg border bg-slate-100" />
                    
                    {/* Phase 2: Mock Gen AI Review Assistant Panel Preview */}
                    <div className="bg-purple-50 border border-purple-200 p-3 rounded-lg">
                      <p className="text-3xs uppercase font-extrabold tracking-widest text-purple-800 flex items-center gap-1">✨ Phase 2 Gen-AI Agent Advisory Note</p>
                      <p className="text-2xs text-purple-950 mt-1 font-medium">"Visual array maps cleanly to category. Core text parameters indicate genuine field presence. No pixel duplicates located in existing database arrays."</p>
                    </div>

                    <div>
                      <span className="text-3xs font-bold text-slate-400 uppercase block">Field Statement</span>
                      <p className="text-xs bg-slate-50 p-2 rounded text-slate-700 font-medium">"{activeReview.note}"</p>
                    </div>

                    <div className="border-t pt-3 space-y-3">
                      <button onClick={() => handleAdminReview(activeReview.id, 'APPROVED')} className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs py-2 rounded-lg transition shadow-xs">
                        ✓ Grant Category Milestone Star
                      </button>
                      
                      <div className="border p-2.5 rounded-lg bg-slate-50 space-y-2">
                        <span className="text-3xs font-bold text-slate-500 uppercase block">Structured Rejection Routing</span>
                        <select value={rejectionReason} onChange={(e) => setRejectionReason(e.target.value)} className="w-full text-2xs border rounded bg-white p-1 outline-none">
                          <option value="Blurry Image">Blurry Image / Artifacting</option>
                          <option value="Wrong Season/Quarter">Wrong Season / Out of Quarter Boundary</option>
                          <option value="Not Related to Category">Target Action Disconnected from Category Matrix</option>
                          <option value="Duplicate Submission">Data Duplication Sequence Found</option>
                          <option value="Other">Other Exception Protocol</option>
                        </select>
                        <input type="text" placeholder="Add specific feedback remarks here..." value={rejectionRemarks} onChange={(e) => setRejectionRemarks(e.target.value)} className="w-full text-2xs border p-1 rounded outline-none" />
                        <button onClick={() => handleAdminReview(activeReview.id, 'REJECTED')} className="w-full bg-red-600 hover:bg-red-700 text-white font-bold text-2xs py-1.5 rounded transition">
                          ⚠️ Reject with Exact Reason String
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic text-center py-12">Select an operational queue node to invoke structural audit commands.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* ADMIN: SUPER ADMIN USER AUDIT MANAGEMENT                  */}
        {/* ========================================================= */}
        {currentRole === 'ADMIN' && currentPage === 'users' && (
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-slate-900">Super Admin User Enforcement Portal</h3>
              <p className="text-xs text-slate-500">Perform account status overrides (Rule 15 constraint enforcement layer).</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="bg-slate-100 border-b font-bold uppercase tracking-wider text-2xs text-slate-600">
                    <th className="p-3">Full Identity Block</th>
                    <th className="p-3">Electronic Coordinates</th>
                    <th className="p-3">Assigned Role Context</th>
                    <th className="p-3">Operational Status</th>
                    <th className="p-3 text-right">Enforcement Directives</th>
                  </tr>
                </thead>
                <tbody className="divide-y text-slate-700">
                  <tr className="hover:bg-slate-50">
                    <td className="p-3 font-semibold text-slate-900">Rajesh Kumar</td>
                    <td className="p-3">rajesh@bharat.org</td>
                    <td className="p-3"><span className="bg-slate-100 text-slate-800 px-2 py-0.5 rounded font-mono font-bold text-2xs">VOLUNTEER</span></td>
                    <td className="p-3"><span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-2xs">ACTIVE</span></td>
                    <td className="p-3 text-right">
                      <button onClick={() => alert("User account frozen in schema directory.")} className="text-red-600 hover:bg-red-50 px-2 py-1 rounded font-bold text-2xs">Block User Access</button>
                    </td>
                  </tr>
                  <tr className="hover:bg-slate-50">
                    <td className="p-3 font-semibold text-slate-900">Amina Al-Noor</td>
                    <td className="p-3">amina@bharat.org</td>
                    <td className="p-3"><span className="bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded font-mono font-bold text-2xs">EVENT MANAGER</span></td>
                    <td className="p-3"><span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-2xs">ACTIVE</span></td>
                    <td className="p-3 text-right">
                      <button onClick={() => alert("Permissions revoked.")} className="text-slate-500 hover:bg-slate-100 px-2 py-1 rounded text-2xs">Demote to Volunteer</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

      </main>

      {/* --- SITE FOOTER --- */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400 font-medium">
        Servants of Bharat Core Operations Layout • Fully Interactive Proto Layer
      </footer>
    </div>
  );
}