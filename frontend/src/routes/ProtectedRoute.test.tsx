import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthProvider } from "../hooks/useAuth";
import { AdminRoute, ProtectedRoute } from "./ProtectedRoute";

function renderRoutes(route: string, admin = false) {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(admin ? { id: "1", email: "admin@example.com", role: "admin", created_at: "2026-01-01" } : { id: "1", email: "customer@example.com", role: "customer", created_at: "2026-01-01" }), { status: 200 })));
  return render(<AuthProvider><MemoryRouter initialEntries={[route]}><Routes><Route path="/login" element={<p>Login page</p>} /><Route path="/inventory" element={<p>Inventory page</p>} /><Route element={<ProtectedRoute />}><Route path="/protected" element={<p>Protected page</p>} /><Route element={<AdminRoute />}><Route path="/admin" element={<p>Admin page</p>} /></Route></Route></Routes></MemoryRouter></AuthProvider>);
}

describe("route guards", () => {
  beforeEach(() => localStorage.clear());
  it("redirects signed-out users to login", async () => { renderRoutes("/protected"); expect(await screen.findByText("Login page")).toBeInTheDocument(); });
  it("redirects regular users away from admin pages", async () => { localStorage.setItem("car_dealership_token", "token"); renderRoutes("/admin"); expect(await screen.findByText("Inventory page")).toBeInTheDocument(); });
  it("allows admins into admin pages", async () => { localStorage.setItem("car_dealership_token", "token"); renderRoutes("/admin", true); expect(await screen.findByText("Admin page")).toBeInTheDocument(); });
});
