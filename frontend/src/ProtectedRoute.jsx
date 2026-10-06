import { Navigate, Outlet } from 'react-router-dom';
import { isAuthenticated } from './auth';

export const ProtectedRoute = () => {
  if (!isAuthenticated()) {
    // Si NO hay token, redirige inmediatamente a /login
    return <Navigate to="/login" replace />;
  }

  // Si SÍ hay token, renderiza la ruta hija correspondiente
  return <Outlet />;
};

