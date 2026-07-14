import { certificateApi } from "../../services/endpoints";
import { useAsync } from "../../hooks/useAsync";
import { EmptyState, PageHeader, PageLoader } from "../../components/ui";
import { formatDate } from "../../utils/datetime";

export default function AdminCertificates() {
  const { data, loading, error } = useAsync(() => certificateApi.list(), []);

  return (
    <div>
      <PageHeader
        title="Certificates"
        subtitle="Every volunteer who has earned a completion certificate."
      />

      {loading ? (
        <PageLoader />
      ) : error ? (
        <p className="text-red-600">{error}</p>
      ) : data.length === 0 ? (
        <EmptyState
          title="No certificates issued yet"
          subtitle="Certificates appear here once volunteers complete all five categories."
        />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Certificate No.</th>
                <th className="px-4 py-3">Volunteer</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Issued</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.map((c) => (
                <tr key={c.id}>
                  <td className="px-4 py-3 font-mono text-xs text-brand-800">{c.certificate_number}</td>
                  <td className="px-4 py-3 font-medium text-slate-700">{c.volunteer_name}</td>
                  <td className="px-4 py-3 text-slate-500">{c.volunteer_email || "—"}</td>
                  <td className="px-4 py-3 text-slate-500">{formatDate(c.issued_at)}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-3 text-xs">
                      <a
                        href={`/verify/${c.verification_code}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-brand-700 hover:underline"
                      >
                        Verify
                      </a>
                      {c.pdf_url && (
                        <a
                          href={c.pdf_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-saffron-600 hover:underline"
                        >
                          PDF
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
