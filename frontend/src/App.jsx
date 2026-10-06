import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { initApiConfig } from './config';
import { ProtectedRoute } from './ProtectedRoute';
import { Login } from './Login';
import { Admin } from './Admin';
import { useEffect, useState } from 'react';
import { CampusesService } from './api';

// Inicializar la configuración global de la API
initApiConfig();

// Componente para la Vista Pública Principal
// (Pública para Alumnos y Visitantes)
function Home() {
  const [campuses, setCampuses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    CampusesService.campusesList()
      .then((response) => {
        const list = Array.isArray(response)
          ? response
          : (
              response?.features ||
              response?.results ||
              []
            );

        setCampuses(list);
        setLoading(false);
      })
      .catch((error) => {
        console.error(
          'Error al cargar los campus:',
          error
        );
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h1>CampusNav3D - Vista Pública</h1>

      {loading ? (
        <p>Cargando datos del mapa...</p>
      ) : (
        <section>
          <h2>Lista de Campus Disponibles:</h2>

          {campuses.length === 0 ? (
            <p>
              No hay campus registrados en la base de datos.
            </p>
          ) : (
            <ul>
              {campuses.map((campus, index) => {
                const props =
                  campus?.properties || campus;

                const id =
                  campus?.id ??
                  props?.id ??
                  index;

                const name =
                  props?.name ??
                  props?.nombre ??
                  campus?.name ??
                  campus?.nombre;

                return (
                  <li key={id}>
                    <strong>ID: {id}</strong>
                    {' — '}
                    {name
                      ? name
                      : `Atributos: ${JSON.stringify(props)}`}
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}

// Configuración Global de Rutas
export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Ruta Pública Principal (Alumnos / Visitantes) */}
        <Route
          path="/"
          element={<Home />}
        />

        {/* Ruta Pública de Login */}
        <Route
          path="/login"
          element={<Login />}
        />

        {/* Rutas Protegidas (Solo accesibles con Token) */}
        <Route element={<ProtectedRoute />}>
          <Route
            path="/admin"
            element={<Admin />}
          />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}
