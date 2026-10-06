import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LoginService } from './api';
import { setToken } from './auth';

export const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Pasamos las credenciales directamente
      // como objeto de la petición.
      const response = await LoginService.loginCreate({
        username,
        password,
      });

      console.log('Respuesta de Login recibida:', response);

      const token = response?.token;

      if (token) {
        // Almacenar el token en localStorage
        setToken(token);

        // Redirigir al panel privado
        navigate('/admin');
      } else {
        setError(
          'El servidor no devolvió un token válido.'
        );
      }
    } catch (err) {
      console.error('Error al iniciar sesión:', err);

      if (err.response?.data) {
        // Mostrar el error concreto devuelto por Django
        setError(
          JSON.stringify(err.response.data)
        );
      } else {
        setError(
          'Usuario o contraseña incorrectos.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: '400px',
        margin: '50px auto',
        padding: '20px',
      }}
    >
      <h1>Acceso Mantenimiento - CampusNav3D</h1>

      {error && (
        <p
          role="alert"
          style={{
            color: 'red',
            marginBottom: '15px',
          }}
        >
          {error}
        </p>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="username">
            Usuario:
          </label>

          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) =>
              setUsername(e.target.value)
            }
            required
            style={{
              width: '100%',
              padding: '8px',
              boxSizing: 'border-box',
            }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="password">
            Contraseña:
          </label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required
            style={{
              width: '100%',
              padding: '8px',
              boxSizing: 'border-box',
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '10px',
            cursor: loading
              ? 'not-allowed'
              : 'pointer',
          }}
        >
          {loading
            ? 'Verificando...'
            : 'Iniciar Sesión'}
        </button>
      </form>
    </div>
  );
};
