import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute, { homeForRole } from "./components/ProtectedRoute";
import { useAuth } from "./contexts/AuthContext";

// Public pages
import Landing from "./pages/public/Landing";
import Login from "./pages/public/Login";
import Register from "./pages/public/Register";
import VerifyCertificate from "./pages/public/VerifyCertificate";

// Shared
import Profile from "./pages/shared/Profile";

// Volunteer pages
import VolunteerDashboard from "./pages/volunteer/Dashboard";
import Events from "./pages/volunteer/Events";
import EventDetail from "./pages/volunteer/EventDetail";
import SubmitProof from "./pages/volunteer/SubmitProof";
import MySubmissions from "./pages/volunteer/MySubmissions";
import Progress from "./pages/volunteer/Progress";
import Notifications from "./pages/volunteer/Notifications";
import CertificatePage from "./pages/volunteer/Certificate";

// Event Manager pages
import EmDashboard from "./pages/manager/Dashboard";
import EmEvents from "./pages/manager/Events";
import ReviewQueue from "./pages/manager/ReviewQueue";
import SubmissionDetail from "./pages/manager/SubmissionDetail";

// Super Admin pages
import AdminDashboard from "./pages/admin/Dashboard";
import AdminUsers from "./pages/admin/Users";
import AdminEventManagers from "./pages/admin/EventManagers";
import AdminCertificates from "./pages/admin/Certificates";

const V = ["volunteer"];
const EM = ["event_manager", "super_admin"];
const ADMIN = ["super_admin"];

function RootRedirect() {
  const { isAuthenticated, user } = useAuth();
  return isAuthenticated ? <Navigate to={homeForRole(user.role)} replace /> : <Landing />;
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<RootRedirect />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/verify/:code" element={<VerifyCertificate />} />

      {/* Authenticated shell */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Shared */}
        <Route path="/profile" element={<Profile />} />

        {/* Volunteer */}
        <Route path="/dashboard" element={<ProtectedRoute roles={V}><VolunteerDashboard /></ProtectedRoute>} />
        <Route path="/events" element={<ProtectedRoute roles={V}><Events /></ProtectedRoute>} />
        <Route path="/events/:id" element={<ProtectedRoute roles={V}><EventDetail /></ProtectedRoute>} />
        <Route path="/submit-proof" element={<ProtectedRoute roles={V}><SubmitProof /></ProtectedRoute>} />
        <Route path="/my-submissions" element={<ProtectedRoute roles={V}><MySubmissions /></ProtectedRoute>} />
        <Route path="/progress" element={<ProtectedRoute roles={V}><Progress /></ProtectedRoute>} />
        <Route path="/notifications" element={<ProtectedRoute roles={V}><Notifications /></ProtectedRoute>} />
        <Route path="/certificate" element={<ProtectedRoute roles={V}><CertificatePage /></ProtectedRoute>} />

        {/* Event Manager (+ Super Admin) */}
        <Route path="/em/dashboard" element={<ProtectedRoute roles={EM}><EmDashboard /></ProtectedRoute>} />
        <Route path="/em/events" element={<ProtectedRoute roles={EM}><EmEvents /></ProtectedRoute>} />
        <Route path="/em/review-queue" element={<ProtectedRoute roles={EM}><ReviewQueue /></ProtectedRoute>} />
        <Route path="/em/submissions/:id" element={<ProtectedRoute roles={EM}><SubmissionDetail /></ProtectedRoute>} />

        {/* Super Admin */}
        <Route path="/admin/dashboard" element={<ProtectedRoute roles={ADMIN}><AdminDashboard /></ProtectedRoute>} />
        <Route path="/admin/users" element={<ProtectedRoute roles={ADMIN}><AdminUsers /></ProtectedRoute>} />
        <Route path="/admin/event-managers" element={<ProtectedRoute roles={ADMIN}><AdminEventManagers /></ProtectedRoute>} />
        <Route path="/admin/certificates" element={<ProtectedRoute roles={ADMIN}><AdminCertificates /></ProtectedRoute>} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
