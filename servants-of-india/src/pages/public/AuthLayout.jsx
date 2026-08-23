import { Link } from "react-router-dom";

/** Split-screen shell shared by Login and Register. */
export default function AuthLayout({ title, subtitle, children, footer }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden flex-col justify-between bg-brand-700 p-12 text-white lg:flex">
        <Link to="/" className="flex items-center gap-2">
          <div className="grid h-10 w-10 place-items-center rounded-lg bg-white/10 text-saffron-400">
            <span className="text-xl font-black">✦</span>
          </div>
          <span className="text-lg font-bold">Servants of Bharat</span>
        </Link>
        <div>
          <h2 className="text-3xl font-extrabold leading-tight">
            Service, recognised.
          </h2>
          <p className="mt-4 max-w-md text-brand-100">
            Join events, submit proof of your volunteer work, and earn a verifiable
            certificate of completion.
          </p>
        </div>
        <p className="text-sm text-brand-100/70">Servants of Bharat</p>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <h1 className="text-2xl font-bold text-brand-900">{title}</h1>
          {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
          <div className="mt-6">{children}</div>
          {footer && <div className="mt-6 text-center text-sm text-slate-500">{footer}</div>}
        </div>
      </div>
    </div>
  );
}
