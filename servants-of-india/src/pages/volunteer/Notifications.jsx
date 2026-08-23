import { notificationApi } from "../../services/endpoints";
import { useToast } from "../../contexts/ToastContext";
import { useAsync } from "../../hooks/useAsync";
import { EmptyState, PageHeader, PageLoader } from "../../components/ui";

const ICON = { approval: "✅", rejection: "❌", certificate: "🏆", system: "🔔" };

export default function Notifications() {
  const toast = useToast();
  const { data, loading, error, reload } = useAsync(() => notificationApi.list(), []);

  const markRead = async (id) => {
    try {
      await notificationApi.markRead(id);
      reload();
    } catch (err) {
      toast.error(err.message);
    }
  };

  if (loading) return <PageLoader />;
  if (error) return <p className="text-red-600">{error}</p>;

  const notes = data.notifications;

  return (
    <div className="max-w-2xl">
      <PageHeader
        title="Notifications"
        subtitle={data.unread_count ? `${data.unread_count} unread` : "You're all caught up."}
      />
      {notes.length === 0 ? (
        <EmptyState title="No notifications yet" />
      ) : (
        <div className="space-y-2">
          {notes.map((n) => (
            <div
              key={n.id}
              className={`card flex items-start gap-3 ${n.is_read ? "" : "border-brand-200 bg-brand-50/40"}`}
            >
              <span className="text-xl">{ICON[n.type] || "🔔"}</span>
              <div className="flex-1">
                <p className="text-sm text-slate-700">{n.message}</p>
                <p className="mt-1 text-xs text-slate-400">{new Date(n.created_at).toLocaleString()}</p>
              </div>
              {!n.is_read && (
                <button onClick={() => markRead(n.id)} className="text-xs font-semibold text-brand-700 hover:underline">
                  Mark read
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
