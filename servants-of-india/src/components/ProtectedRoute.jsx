import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

/**
 * Guards routes by auth + role. `roles` is an optional array of allowed roles.
 * Unauthenticated users go to /login; wrong-role users go to their home.
 */
export default function ProtectedRoute({ roles, children }) {
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to={homeForRole(user.role)} replace />;
  }
  return children;
}

export function homeForRole(role) {
  switch (role) {
    case "super_admin":
      return "/admin/dashboard";
    case "event_manager":
      return "/em/dashboard";
    default:
      return "/dashboard";
  }
}
