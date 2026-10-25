import { describe, expect, it, vi } from "vitest";

import { api } from "./client";

describe("api client", () => {
  it("sends JSON and bearer credentials", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ id: "vehicle-1" }), { status: 200 }),
    );

    await expect(api<{ id: string }>("/vehicles", { method: "GET" }, "token")).resolves.toEqual({ id: "vehicle-1" });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/vehicles",
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: "Bearer token" }) }),
    );
  });

  it("surfaces API error details", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "Incorrect email or password" }), { status: 401 }),
    );
    await expect(api("/auth/login")).rejects.toEqual(expect.objectContaining({ name: "ApiError", message: "Incorrect email or password", status: 401 }));
  });
});
