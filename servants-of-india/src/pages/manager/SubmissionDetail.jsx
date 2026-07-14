import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { submissionApi } from "../../services/endpoints";
import { useToast } from "../../contexts/ToastContext";
import { useAsync } from "../../hooks/useAsync";
import { PageLoader, Spinner, StatusBadge } from "../../components/ui";
import { formatDateTime } from "../../utils/datetime";

export default function SubmissionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const { data: s, loading, error, reload } = useAsync(() => submissionApi.get(id), [id]);
  const [remarks, setRemarks] = useState("");
  const [busy, setBusy] = useState(false);

  const act = async (kind) => {
    if (kind === "reject" && !remarks.trim()) {
      return toast.error("A rejection reason is required");
    }
    setBusy(true);
    try {
      if (kind === "approve") {
        await submissionApi.approve(id, remarks.trim() || undefined);
        toast.success("Submission approved");
      } else {
        await submissionApi.reject(id, remarks.trim());
        toast.success("Submission rejected");
      }
      reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <PageLoader />;
  if (error) return <p className="text-red-600">{error}</p>;

  const pending = s.status === "pending";

  return (
    <div className="max-w-3xl">
      <button onClick={() => navigate(-1)} className="btn-ghost mb-4 text-sm">← Back to queue</button>

      <div className="card">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-brand-900">{s.category_name}</h1>
          <StatusBadge status={s.status} />
        </div>
        <p className="mt-1 text-sm text-slate-500">
          By <b>{s.volunteer_name}</b> · {formatDateTime(s.submitted_at)} IST
        </p>

        <img src={s.image_url} alt="proof" className="mt-4 max-h-96 w-full rounded-lg border border-slate-200 object-contain bg-slate-50" />

        <div className="mt-4">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Description</p>
          <p className="mt-1 whitespace-pre-line text-slate-700">{s.description}</p>
        </div>

        {s.event_title && (
          <p className="mt-3 text-sm text-slate-500">Linked event: <b>{s.event_title}</b></p>
        )}

        {s.review && !pending && (
          <div className={`mt-4 rounded-lg px-3 py-2 text-sm ${s.status === "approved" ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"}`}>
            <b>{s.review.decision === "approved" ? "Approved" : "Rejected"}</b>
            {s.review.remarks && <> — {s.review.remarks}</>}
            <span className="block text-xs opacity-70">by {s.review.reviewer_name} on {formatDateTime(s.review.reviewed_at)} IST</span>
          </div>
        )}

        {pending && (
          <div className="mt-6 border-t border-slate-100 pt-5">
            <label className="label">Remarks (required to reject, optional to approve)</label>
            <textarea
              className="input min-h-[80px]"
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="Reason for rejection, or a note on approval…"
            />
            <div className="mt-3 flex gap-3">
              <button onClick={() => act("approve")} disabled={busy} className="btn-primary flex-1">
                {busy ? <Spinner /> : "Approve"}
              </button>
              <button onClick={() => act("reject")} disabled={busy} className="btn-danger flex-1">
                {busy ? <Spinner /> : "Reject"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
