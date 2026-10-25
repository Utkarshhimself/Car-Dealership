import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

function LoadingRoute() {
  return <main className="centered-message">Restoring your session…</main>;
}

export function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) return <LoadingRoute />;
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}

export function AdminRoute() {
  const { user, loading } = useAuth();
  if (loading) return <LoadingRoute />;
  return user?.role === "admin" ? <Outlet /> : <Navigate to="/inventory" replace />;
}
