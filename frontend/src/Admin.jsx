import { useNavigate } from 'react-router-dom';
import { removeToken } from './auth';

export const Admin = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    removeToken(); // Elimina el token de localStorage
    navigate('/login'); // Redirige al login
  };

  return (
    <div
      style={{
        maxWidth: '800px',
        margin: '50px auto',
        padding: '20px',
      }}
    >
      <h1>Panel de Administración - Mantenimiento CampusNav3D</h1>

      <button
        type="button"
        onClick={handleLogout}
        style={{
          padding: '10px 20px',
          marginBottom: '20px',
          cursor: 'pointer',
        }}
      >
        Cerrar Sesión
      </button>

      <p>
        Bienvenido al área restringida. Desde aquí podrás añadir,
        editar y eliminar edificios y zonas del campus en PostGIS.
      </p>
    </div>
  );
};

