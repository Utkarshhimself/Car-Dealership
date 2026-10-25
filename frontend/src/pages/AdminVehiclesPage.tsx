import { FormEvent, useEffect, useState } from "react";

import { api, uploadImage, uploadsUrl } from "../api/client";
import { AppShell } from "../components/AppShell";
import { useAuth } from "../hooks/useAuth";
import type { Vehicle, VehicleInput, VehiclePage } from "../types/vehicle";

const empty: VehicleInput = { make: "", model: "", category: "", price: 0, quantity: 0 };

export function AdminVehiclesPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<Vehicle[]>([]);
  const [form, setForm] = useState<VehicleInput>(empty);
  const [image, setImage] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const refresh = () => api<VehiclePage>("/vehicles?page_size=100", {}, token)
    .then((response) => setItems(response.items))
    .catch((requestError: unknown) => setError(requestError instanceof Error ? requestError.message : "Unable to load vehicles"));

  useEffect(() => { void refresh(); }, [token]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null); setSubmitting(true);
    try {
      const vehicle = await api<Vehicle>("/vehicles", { method: "POST", body: JSON.stringify(form) }, token);
      if (image) await uploadImage<Vehicle>(`/vehicles/${vehicle.id}/image`, image, token);
      setForm(empty); setImage(null); await refresh();
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to create vehicle"); }
    finally { setSubmitting(false); }
  }
  async function remove(id: string) { try { await api<void>(`/vehicles/${id}`, { method: "DELETE" }, token); await refresh(); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "Unable to delete vehicle"); } }

  return <AppShell>
    <section className="page-heading"><p className="eyebrow">Administration</p><h1>Curate the collection.</h1><p>Add a vehicle and attach a showroom-ready PNG, JPEG, or WebP image.</p></section>
    <form className="admin-form" onSubmit={submit}>
      {(["make", "model", "category"] as const).map((key) => <label key={key}>{key}<input required value={form[key]} onChange={(event) => setForm({ ...form, [key]: event.target.value })} /></label>)}
      <label>Price<input required min="0.01" step="0.01" type="number" value={form.price || ""} onChange={(event) => setForm({ ...form, price: Number(event.target.value) })} /></label>
      <label>Quantity<input required min="0" type="number" value={form.quantity} onChange={(event) => setForm({ ...form, quantity: Number(event.target.value) })} /></label>
      <label className="image-upload">Vehicle image <input accept="image/png,image/jpeg,image/webp" type="file" onChange={(event) => setImage(event.target.files?.[0] ?? null)} /><span>{image ? image.name : "PNG, JPEG, or WebP — 5 MB maximum"}</span></label>
      <button className="button" disabled={submitting}>{submitting ? "Adding vehicle…" : "Add vehicle"}</button>
    </form>
    {error && <p className="form-error">{error}</p>}
    <section className="admin-list">{items.map((vehicle) => <article key={vehicle.id}>
      {vehicle.image_filename ? <img src={uploadsUrl(vehicle.image_filename)} alt="" /> : <div className="vehicle-placeholder">{vehicle.make.slice(0, 1)}{vehicle.model.slice(0, 1)}</div>}
      <span><strong>{vehicle.make} {vehicle.model}</strong><small>{vehicle.category} · ${vehicle.price} · {vehicle.quantity} in stock</small></span>
      <button className="text-button" onClick={() => void remove(vehicle.id)}>Delete</button>
    </article>)}</section>
  </AppShell>;
}
