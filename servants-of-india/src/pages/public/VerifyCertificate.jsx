import { Link, useParams } from "react-router-dom";
import { certificateApi } from "../../services/endpoints";
import { useAsync } from "../../hooks/useAsync";
import { PageLoader } from "../../components/ui";

export default function VerifyCertificate() {
  const { code } = useParams();
  const { data, loading, error } = useAsync(() => certificateApi.verify(code), [code]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-lg">
        <Link to="/" className="mb-6 flex items-center justify-center gap-2">
          <div className="grid h-9 w-9 place-items-center rounded-lg bg-brand-700 text-saffron-400">
            <span className="text-lg font-black">✦</span>
          </div>
          <span className="text-lg font-bold text-brand-900">Servants of Bharat</span>
        </Link>

        <div className="card text-center">
          <h1 className="text-lg font-semibold text-slate-500">Certificate Verification</h1>

          {loading && <PageLoader />}
          {error && <p className="mt-6 text-red-600">{error}</p>}

          {!loading && !error && data && (
            data.valid ? (
              <div className="mt-6">
                <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-emerald-100 text-3xl text-emerald-600">
                  ✓
                </div>
                <p className="mt-4 text-xl font-bold text-emerald-700">Valid Certificate</p>
                <dl className="mt-6 space-y-3 text-left">
                  <Row label="Volunteer" value={data.certificate.volunteer_name} />
                  <Row label="Certificate No." value={data.certificate.certificate_number} />
                  <Row
                    label="Issued"
                    value={
                      data.certificate.issued_at
                        ? new Date(data.certificate.issued_at).toLocaleDateString()
                        : "—"
                    }
                  />
                </dl>
              </div>
            ) : (
              <div className="mt-6">
                <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-red-100 text-3xl text-red-600">
                  ✕
                </div>
                <p className="mt-4 text-xl font-bold text-red-700">Invalid or Not Found</p>
                <p className="mt-2 text-sm text-slate-500">
                  No certificate matches this verification code.
                </p>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between border-b border-slate-100 pb-2">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd className="text-sm font-semibold text-slate-800">{value}</dd>
    </div>
  );
}
