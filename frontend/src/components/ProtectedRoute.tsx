import { Navigate, Outlet } from 'react-router-dom';
import { useAppStore } from '@/store/useAppStore';

interface ProtectedRouteProps {
  requireVerified?: boolean;
}

const ProtectedRoute = ({ requireVerified = true }: ProtectedRouteProps) => {
  const { isAuthenticated, user } = useAppStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireVerified && user && user.aadhaar_status !== 'verified') {
    return <Navigate to="/verify" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
