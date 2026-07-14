import { Link } from "react-router-dom";

const CATEGORIES = [
  "Women's Care",
  "Child Welfare",
  "Elder Care & Orphanage",
  "Environmental Plantation",
  "Blood Donation",
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      {/* Nav */}
      <header className="border-b border-slate-200">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2">
            <div className="grid h-9 w-9 place-items-center rounded-lg bg-brand-700 text-saffron-400">
              <span className="text-lg font-black">✦</span>
            </div>
            <span className="text-lg font-bold text-brand-900">Servants of Bharat</span>
          </div>
          <div className="flex items-center gap-2">
            <Link to="/login" className="btn-ghost">Login</Link>
            <Link to="/register" className="btn-accent">Get Started</Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center">
          <span className="badge bg-saffron-500/10 text-saffron-600">Volunteer Management, simplified</span>
          <h1 className="mx-auto mt-5 max-w-3xl text-4xl font-extrabold leading-tight text-brand-900 sm:text-5xl">
            Turn everyday service into
            <span className="text-saffron-500"> recognised impact</span>
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-slate-500">
            One platform to join events, submit proof of your service across five
            categories, track your progress, and earn a verifiable certificate — no more
            scattered WhatsApp groups.
          </p>
          <div className="mt-8 flex justify-center gap-3">
            <Link to="/register" className="btn-accent px-6 py-3 text-base">Become a Volunteer</Link>
            <Link to="/login" className="btn-primary px-6 py-3 text-base">Sign in</Link>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="bg-slate-50 py-16">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="text-center text-2xl font-bold text-brand-900">Five ways to serve</h2>
          <p className="mt-2 text-center text-slate-500">Complete all five to earn your certificate.</p>
          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {CATEGORIES.map((c, i) => (
              <div key={c} className="card text-center">
                <div className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-brand-100 text-xl font-bold text-brand-700">
                  {i + 1}
                </div>
                <p className="mt-3 text-sm font-semibold text-slate-700">{c}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16">
        <div className="mx-auto max-w-5xl px-4">
          <h2 className="text-center text-2xl font-bold text-brand-900">How it works</h2>
          <div className="mt-8 grid gap-6 sm:grid-cols-3">
            {[
              ["Register & join events", "Sign up as a volunteer and browse upcoming service events."],
              ["Submit proof", "Upload a photo and description for each of the five categories."],
              ["Get certified", "Once all five are approved, generate a publicly verifiable certificate."],
            ].map(([t, d], i) => (
              <div key={t} className="card">
                <div className="text-sm font-bold text-saffron-500">STEP {i + 1}</div>
                <h3 className="mt-1 font-semibold text-brand-900">{t}</h3>
                <p className="mt-1 text-sm text-slate-500">{d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 py-8 text-center text-sm text-slate-400">
        © {new Date().getFullYear()} Servants of Bharat
      </footer>
    </div>
  );
}
