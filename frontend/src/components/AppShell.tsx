import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <Link className="brand" to="/inventory">Motorhouse</Link>
        <nav aria-label="Primary navigation">
          <NavLink to="/inventory">Inventory</NavLink>
          {user?.role === "admin" && <NavLink to="/admin/vehicles">Manage vehicles</NavLink>}
        </nav>
        <div className="account-menu">
          <span>{user?.email}</span>
          <button className="button button-quiet" onClick={handleLogout}>Log out</button>
        </div>
      </header>
      <main className="page-content">{children}</main>
    </div>
  );
}
