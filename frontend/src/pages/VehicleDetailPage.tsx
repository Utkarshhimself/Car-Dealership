import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, uploadsUrl } from "../api/client";
import { AppShell } from "../components/AppShell";
import { useAuth } from "../hooks/useAuth";
import type { Vehicle } from "../types/vehicle";
export function VehicleDetailPage() { const { vehicleId } = useParams(); const { token } = useAuth(); const [vehicle, setVehicle] = useState<Vehicle | null>(null); const [error, setError] = useState<string | null>(null); useEffect(() => { if (vehicleId) api<Vehicle>(`/vehicles/${vehicleId}`, {}, token).then(setVehicle).catch((e: unknown) => setError(e instanceof Error ? e.message : "Unable to load vehicle")); }, [token, vehicleId]); return <AppShell>{error ? <p className="form-error">{error}</p> : !vehicle ? <p>Loading vehicle…</p> : <section className="detail-card">{vehicle.image_filename && <img src={uploadsUrl(vehicle.image_filename)} alt={`${vehicle.make} ${vehicle.model}`} />}<div><Link to="/inventory">← Back to inventory</Link><p className="eyebrow">{vehicle.category}</p><h1>{vehicle.make} {vehicle.model}</h1><p className="price">${Number(vehicle.price).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p><p>{vehicle.quantity} in stock</p></div></section>}</AppShell>; }
