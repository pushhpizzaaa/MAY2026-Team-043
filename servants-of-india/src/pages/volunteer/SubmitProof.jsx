import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { eventApi, progressApi, submissionApi } from "../../services/endpoints";
import { useToast } from "../../contexts/ToastContext";
import { useAsync } from "../../hooks/useAsync";
import { PageHeader, PageLoader, Spinner, StatusBadge } from "../../components/ui";
import { formatDate } from "../../utils/datetime";

const MAX_BYTES = 5 * 1024 * 1024;

export default function SubmitProof() {
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  // Categories (with status) come from the progress endpoint — no separate list API.
  const { data, loading } = useAsync(() => progressApi.me(), []);
  // All completed events; we filter to the chosen category below.
  const { data: completedEvents } = useAsync(() => eventApi.list({ status: "completed" }), []);

  const [categoryId, setCategoryId] = useState(location.state?.categoryId || "");
  const [eventId, setEventId] = useState(location.state?.eventId || "");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Completed events belonging to the selected category.
  const categoryEvents = useMemo(
    () => (completedEvents || []).filter((e) => e.category_id === categoryId),
    [completedEvents, categoryId]
  );

  // Whenever the category changes, drop any event selection that no longer fits.
  useEffect(() => {
    if (eventId && !categoryEvents.some((e) => e.id === eventId)) setEventId("");
  }, [categoryId]); // eslint-disable-line react-hooks/exhaustive-deps

  const onFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    if (!["image/jpeg", "image/png"].includes(f.type)) {
      toast.error("Only JPG and PNG images are allowed");
      return;
    }
    if (f.size > MAX_BYTES) {
      toast.error("Image must be under 5 MB");
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!categoryId) return toast.error("Please choose a category");
    if (!eventId) return toast.error("Please select the completed event you attended");
    if (!file) return toast.error("Please attach a proof image");
    if (!description.trim()) return toast.error("Please add a description");

    const fd = new FormData();
    fd.append("category_id", categoryId);
    fd.append("description", description.trim());
    fd.append("image", file);
    fd.append("event_id", eventId);

    setSubmitting(true);
    try {
      await submissionApi.create(fd);
      toast.success("Proof submitted — awaiting review");
      navigate("/my-submissions");
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <PageLoader />;

  const categories = data?.categories || [];

  return (
    <div className="max-w-2xl">
      <PageHeader title="Submit Proof of Service" subtitle="Upload a photo and describe your work." />
      <div className="card">
        <form onSubmit={submit} className="space-y-5">
          <div>
            <label className="label">Category</label>
            <div className="grid gap-2 sm:grid-cols-2">
              {categories.map((c) => {
                const done = c.status === "completed";
                const pending = c.status === "pending";
                const disabled = done || pending;
                return (
                  <button
                    type="button"
                    key={c.category_id}
                    disabled={disabled}
                    onClick={() => setCategoryId(c.category_id)}
                    className={`flex items-center justify-between rounded-lg border px-3 py-2.5 text-left text-sm transition ${
                      categoryId === c.category_id
                        ? "border-brand-500 bg-brand-50"
                        : "border-slate-200 hover:border-slate-300"
                    } ${disabled ? "cursor-not-allowed opacity-60" : ""}`}
                  >
                    <span className="font-medium text-slate-700">{c.category_name}</span>
                    {c.status !== "not_started" && <StatusBadge status={c.status} />}
                  </button>
                );
              })}
            </div>
            <p className="mt-1.5 text-xs text-slate-400">
              Completed and pending categories cannot be submitted again.
            </p>
          </div>

          {/* Completed events for the chosen category */}
          {categoryId && (
            <div>
              <label className="label">Completed event you attended</label>
              {categoryEvents.length === 0 ? (
                <p className="rounded-lg bg-slate-50 px-3 py-2.5 text-sm text-slate-500">
                  No completed events in this category yet. You can submit once an event you
                  attended is marked completed.
                </p>
              ) : (
                <select
                  className="input"
                  value={eventId}
                  onChange={(e) => setEventId(e.target.value)}
                >
                  <option value="">Select an event…</option>
                  {categoryEvents.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.title} — {e.city} · {formatDate(e.event_date)}
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}

          <div>
            <label className="label">Proof image (JPG/PNG, max 5 MB)</label>
            <input type="file" accept="image/jpeg,image/png" onChange={onFile} className="input" />
            {preview && (
              <img src={preview} alt="preview" className="mt-3 max-h-56 rounded-lg border border-slate-200 object-cover" />
            )}
          </div>

          <div>
            <label className="label">Description</label>
            <textarea
              className="input min-h-[110px]"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what you did, where, and when…"
            />
          </div>

          <button
            type="submit"
            disabled={submitting || (categoryId && categoryEvents.length === 0)}
            className="btn-accent w-full"
          >
            {submitting ? <Spinner /> : "Submit for review"}
          </button>
        </form>
      </div>
    </div>
  );
}
