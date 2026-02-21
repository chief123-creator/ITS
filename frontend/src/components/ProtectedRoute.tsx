// src/components/ProtectedRoute.tsx
import { Navigate } from "react-router-dom";
import { useAppStore } from "@/store/useAppStore";

interface Props {
  children: React.ReactNode;
  requireVerified?: boolean;
}

export default function ProtectedRoute({ children, requireVerified = true }: Props) {
  const { isAuthenticated, user } = useAppStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (requireVerified && user?.aadhaar_status !== 'verified') {
    return <Navigate to="/verify" replace />;
  }
  return <>{children}</>;
}