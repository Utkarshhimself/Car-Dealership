const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export const uploadsUrl = (filename: string) =>
  `${API_URL.replace(/\/api$/, "")}/uploads/${filename}`;

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

export async function uploadImage<T>(path: string, image: File, token: string | null): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: (() => { const form = new FormData(); form.append("image", image); return form; })(),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(body?.detail ?? "Unable to upload image", response.status);
  }
  return response.json() as Promise<T>;
}

export async function api<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(body?.detail ?? "Something went wrong", response.status);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
