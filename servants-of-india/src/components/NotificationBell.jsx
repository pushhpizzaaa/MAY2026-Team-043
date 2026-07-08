import React from 'react';

export default function NotificationBell({ notifications }) {
  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="relative group cursor-pointer">
      <span className="text-lg">🔔</span>
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-2 bg-red-500 text-white text-3xs w-4 h-4 rounded-full flex items-center justify-center font-bold">
          {unreadCount}
        </span>
      )}
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
  );
}