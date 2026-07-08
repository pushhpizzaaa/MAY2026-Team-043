import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getLocalStorageData, saveLocalStorageData } from '../../data/mockData';

export default function AuthPage() {
  const navigate = useNavigate();
  const [view, setView] = useState('login'); // 'login' or 'register'
  
  // Shared state fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [bloodGroup, setBloodGroup] = useState('O+');
  const [organization, setOrganization] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    const cleanEmail = email.trim().toLowerCase();
    const storedUsers = getLocalStorageData('sob_users', []);

    const user = storedUsers.find(
      u => u.email.trim().toLowerCase() === cleanEmail && u.password === password
    );

    if (!user) {
      alert('Invalid email or password credentials.');
      return;
    }

    if (user.role === 'admin') {
      navigate('/admin', { state: { user } });
    } else {
      navigate('/dashboard', { state: { user } });
    }
  };

  const handleRegister = (e) => {
    e.preventDefault();
    if (!fullName || !email || !password) {
      alert('Please fill out all mandatory fields.');
      return;
    }

    const storedUsers = getLocalStorageData('sob_users', []);
    const cleanEmail = email.trim().toLowerCase();

    if (storedUsers.some(u => u.email.trim().toLowerCase() === cleanEmail)) {
      alert('This email address is already registered.');
      return;
    }

    const newVolunteer = {
      id: 'vol-' + Date.now(),
      role: 'volunteer',
      name: fullName,
      email: cleanEmail,
      password: password,
      phone,
      location,
      bloodGroup,
      organization
    };

    storedUsers.push(newVolunteer);
    saveLocalStorageData('sob_users', storedUsers);
    alert('Registration successful! Please log in with your new credentials.');
    setView('login');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto w-full max-w-md">
        <h2 className="text-center text-3xl font-extrabold text-slate-900 tracking-tight">
          Servants of Bharat
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          {view === 'login' ? "Volunteer platform coordination" : "Join the structured civic year initiative"}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-slate-200">
          {view === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">Email Address</label>
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1 block w-full p-2 border border-slate-300 rounded shadow-sm focus:ring-amber-500 focus:border-amber-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Password</label>
                <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1 block w-full p-2 border border-slate-300 rounded shadow-sm focus:ring-amber-500 focus:border-amber-500" />
              </div>
              <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded shadow-sm text-sm font-medium text-white bg-amber-600 hover:bg-amber-700 focus:outline-none">
                Sign In
              </button>
              <p className="text-center text-xs text-slate-500 mt-4">
                Don't have an account? <span onClick={() => setView('register')} className="text-amber-600 font-semibold cursor-pointer underline">Register here</span>
              </p>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-slate-700">Full Name *</label>
                <input type="text" required value={fullName} onChange={(e) => setFullName(e.target.value)} className="mt-1 block w-full p-1.5 border border-slate-300 rounded shadow-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Email Address *</label>
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1 block w-full p-1.5 border border-slate-300 rounded shadow-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Password *</label>
                <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1 block w-full p-1.5 border border-slate-300 rounded shadow-sm" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium text-slate-700">Phone</label>
                  <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} className="mt-1 block w-full p-1.5 border border-slate-300 rounded shadow-sm" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Blood Group</label>
                  <select value={bloodGroup} onChange={(e) => setBloodGroup(e.target.value)} className="mt-1 block w-full p-1.5 border border-slate-300 rounded shadow-sm">
                    <option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>O+</option><option>O-</option><option>AB+</option><option>AB-</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Location (City, State)</label>
                <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} className="mt-1 block w-full p-1.5 border border-slate-300 rounded shadow-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Organization (Optional)</label>
                <input type="text" value={organization} onChange={(e) => setOrganization(e.target.value)} className="mt-1 block w-full p-1.5 border border-slate-300 rounded shadow-sm" placeholder="College or Company Name" />
              </div>
              <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded shadow-sm text-sm font-medium text-white bg-slate-800 hover:bg-slate-900 focus:outline-none mt-2">
                Create Account
              </button>
              <p className="text-center text-xs text-slate-500 mt-2">
                Already registered? <span onClick={() => setView('login')} className="text-amber-600 font-semibold cursor-pointer underline">Log in here</span>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}