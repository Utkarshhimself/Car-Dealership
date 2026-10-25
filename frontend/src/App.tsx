import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import { LoginPage, RegisterPage } from "./pages/AuthPage";
import { AdminVehiclesPage } from "./pages/AdminVehiclesPage";
import { InventoryPage } from "./pages/InventoryPage";
import { VehicleDetailPage } from "./pages/VehicleDetailPage";
import { AdminRoute, ProtectedRoute } from "./routes/ProtectedRoute";
export function App() { return <AuthProvider><BrowserRouter><Routes><Route path="/login" element={<LoginPage />} /><Route path="/register" element={<RegisterPage />} /><Route element={<ProtectedRoute />}><Route path="/inventory" element={<InventoryPage />} /><Route path="/vehicles/:vehicleId" element={<VehicleDetailPage />} /><Route element={<AdminRoute />}><Route path="/admin/vehicles" element={<AdminVehiclesPage />} /></Route></Route><Route path="/" element={<Navigate to="/inventory" replace />} /><Route path="*" element={<Navigate to="/inventory" replace />} /></Routes></BrowserRouter></AuthProvider>; }
