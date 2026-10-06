import { useEffect, useState } from 'react';
import { initApiConfig } from './config';
import { CampusesService } from './api';

// Inicializar la configuración global de la API
initApiConfig();

function App() {
  const [campuses, setCampuses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    CampusesService.campusesList()
      .then((response) => {
        console.log('GeoJSON recibido:', response);

        let list = [];

        if (Array.isArray(response)) {
          list = response;
        } else if (response && Array.isArray(response.features)) {
          // GeoJSON FeatureCollection
          list = response.features;
        } else if (response && Array.isArray(response.results)) {
          list = response.results;
        }

        setCampuses(list);
        setLoading(false);
      })
      .catch((err) => {
        console.error(
          'Error al conectar con Django en Docker:',
          err
        );
        setError('No se pudo conectar con el servidor backend.');
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h1>CampusNav3D - Cliente API y Frontend</h1>

      {loading && (
        <p>Cargando datos desde Django (Docker)...</p>
      )}

      {error && (
        <p role="alert">{error}</p>
      )}

      {!loading && !error && (
        <section>
          <h2>Lista de Campus Disponibles:</h2>

          {campuses.length === 0 ? (
            <p>
              No hay campus registrados en la base de datos.
            </p>
          ) : (
            <ul>
              {campuses.map((campus, index) => {
                // Si es un Feature GeoJSON, los datos suelen estar
                // dentro de "properties".
                const props = campus?.properties || campus;

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

export default App;
