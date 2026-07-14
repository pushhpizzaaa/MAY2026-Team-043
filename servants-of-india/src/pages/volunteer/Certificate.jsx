import { useState } from "react";
import { Link } from "react-router-dom";
import { certificateApi, progressApi } from "../../services/endpoints";
import { useToast } from "../../contexts/ToastContext";
import { useAsync } from "../../hooks/useAsync";
import { PageHeader, PageLoader, Spinner } from "../../components/ui";

export default function CertificatePage() {
  const toast = useToast();
  const progress = useAsync(() => progressApi.me(), []);
  // 404 (no cert yet) is expected — swallow it into null.
  const cert = useAsync(() => certificateApi.me().catch(() => null), []);
  const [generating, setGenerating] = useState(false);

  const verifyUrl = (code) => `${window.location.origin}/verify/${code}`;

  const generate = async () => {
    setGenerating(true);
    try {
      const c = await certificateApi.generate();
      cert.setData(c);
      toast.success("Certificate generated!");
    } catch (err) {
      toast.error(err.message);
    } finally {
      setGenerating(false);
    }
  };

  if (progress.loading || cert.loading) return <PageLoader />;

  const allDone = progress.data?.all_completed;
  const c = cert.data;

  return (
    <div className="max-w-2xl">
      <PageHeader title="Certificate" subtitle="Your proof of completed service." />

      {c ? (
        <div className="card">
          <div className="rounded-xl border-2 border-brand-700 bg-gradient-to-br from-white to-brand-50 p-8 text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-saffron-500">
              Servants of Bharat
            </p>
            <h2 className="mt-3 text-2xl font-bold text-brand-900">Certificate of Completion</h2>
            <p className="mt-4 text-slate-500">Awarded for completing all five service categories.</p>
            <p className="mt-6 text-lg font-semibold text-brand-800">{c.certificate_number}</p>
            <p className="mt-1 text-xs text-slate-400">
              Issued {new Date(c.issued_at).toLocaleDateString()}
            </p>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            {c.pdf_url && (
              <a href={c.pdf_url} target="_blank" rel="noreferrer" className="btn-primary">
                Download PDF
              </a>
            )}
            <Link to={`/verify/${c.verification_code}`} className="btn-ghost border border-slate-200">
              View public verification
            </Link>
          </div>

          <div className="mt-4 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-500">
            Shareable verification link:{" "}
            <span className="break-all font-mono text-slate-700">{verifyUrl(c.verification_code)}</span>
          </div>
        </div>
      ) : allDone ? (
        <div className="card text-center">
          <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-saffron-100 text-3xl">🏆</div>
          <h3 className="mt-4 text-lg font-bold text-brand-900">You're eligible!</h3>
          <p className="mt-1 text-sm text-slate-500">
            You've completed all five categories. Generate your certificate now.
          </p>
          <button onClick={generate} disabled={generating} className="btn-accent mt-5">
            {generating ? <Spinner /> : "Generate certificate"}
          </button>
        </div>
      ) : (
        <div className="card text-center">
          <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-slate-100 text-3xl">🔒</div>
          <h3 className="mt-4 text-lg font-bold text-brand-900">Not yet eligible</h3>
          <p className="mt-1 text-sm text-slate-500">
            Complete all five categories to unlock your certificate.
            You've completed {progress.data?.stars ?? 0} of {progress.data?.total_categories ?? 5}.
          </p>
          <Link to="/progress" className="btn-primary mt-5">View progress</Link>
        </div>
      )}
    </div>
  );
}
