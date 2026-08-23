import { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

// Role-specific navigation definitions.
const NAV = {
  volunteer: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/events", label: "Events" },
    { to: "/submit-proof", label: "Submit Proof" },
    { to: "/my-submissions", label: "My Submissions" },
    { to: "/progress", label: "Progress" },
    { to: "/certificate", label: "Certificate" },
    { to: "/notifications", label: "Notifications" },
    { to: "/profile", label: "Profile" },
  ],
  event_manager: [
    { to: "/em/dashboard", label: "Dashboard" },
    { to: "/em/events", label: "Events" },
    { to: "/em/review-queue", label: "Review Queue" },
    { to: "/profile", label: "Profile" },
  ],
  super_admin: [
    { to: "/admin/dashboard", label: "Dashboard" },
    { to: "/admin/users", label: "Users" },
    { to: "/admin/event-managers", label: "Event Managers" },
    { to: "/admin/certificates", label: "Certificates" },
    { to: "/em/events", label: "Events" },
    { to: "/em/review-queue", label: "Review Queue" },
    { to: "/profile", label: "Profile" },
  ],
};

const ROLE_LABEL = {
  volunteer: "Volunteer",
  event_manager: "Event Manager",
  super_admin: "Super Admin",
};

function Brand() {
  return (
    <Link to="/" className="flex items-center gap-2">
      <div className="grid h-9 w-9 place-items-center rounded-lg bg-brand-700 text-saffron-400">
        <span className="text-lg font-black">✦</span>
      </div>
      <span className="text-lg font-bold text-brand-900">Servants of Bharat</span>
    </Link>
  );
}

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const links = NAV[user?.role] || [];

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const linkClass = ({ isActive }) =>
    `block rounded-lg px-3 py-2 text-sm font-medium transition ${
      isActive ? "bg-brand-700 text-white" : "text-slate-600 hover:bg-slate-100"
    }`;

  return (
    <div className="min-h-screen">
      {/* Top bar */}
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <button
              className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
              onClick={() => setOpen((o) => !o)}
              aria-label="Toggle menu"
            >
              ☰
            </button>
            <Brand />
          </div>
          <div className="flex items-center gap-3 rounded-full border border-slate-200 bg-slate-50/80 py-1 pl-4 pr-1.5">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-semibold text-slate-700">{user?.full_name}</p>
              <p className="text-xs text-slate-400">{ROLE_LABEL[user?.role]}</p>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-full bg-brand-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-600"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6">
        {/* Sidebar */}
        <aside
          className={`${
            open ? "block" : "hidden"
          } fixed inset-x-0 top-[57px] z-20 border-b border-slate-200 bg-white p-3 lg:static lg:block lg:w-60 lg:shrink-0 lg:border-0 lg:bg-transparent lg:p-0`}
        >
          <nav className="space-y-1" onClick={() => setOpen(false)}>
            {links.map((l) => (
              <NavLink key={l.to} to={l.to} className={linkClass} end>
                {l.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Main content */}
        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
