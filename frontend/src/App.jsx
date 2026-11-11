import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { initApiConfig } from './config';
import { ProtectedRoute } from './ProtectedRoute';
import { Login } from './Login';
import { Admin } from './Admin';
import { CampusMap } from './CampusMap';
import { CampusesService, PlansService } from './api';

initApiConfig();

function Home() {
  const [campuses, setCampuses] = useState([]);
  const [availablePlans, setAvailablePlans] = useState([]); // Lista real de planos devueltos por PostGIS
  
  const [selectedCampusId, setSelectedCampusId] = useState('');
  const [selectedBuildingId, setSelectedBuildingId] = useState('');
  const [selectedFloorId, setSelectedFloorId] = useState('');
  
  const [buildings, setBuildings] = useState([]);
  const [floors, setFloors] = useState([]);
  
  const [activeGeoData, setActiveGeoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 1. Cargar Campus y la lista global de Planos desde Django al iniciar
  useEffect(() => {
    Promise.all([
      CampusesService.campusesList(),
      PlansService.plansList().catch((err) => {
        console.warn('No se pudieron obtener planos globales:', err);
        return [];
      }),
    ])
      .then(([campusResponse, plansResponse]) => {
        // Formatear la lista de campus
        const campusList = campusResponse?.features || (Array.isArray(campusResponse) ? campusResponse : []);
        setCampuses(campusList);

        if (campusResponse && campusResponse.type === 'FeatureCollection') {
          setActiveGeoData(campusResponse);
        } else if (Array.isArray(campusResponse)) {
          setActiveGeoData({ type: 'FeatureCollection', features: campusResponse });
        }

        // Guardar la lista de planos devueltos por PostGIS
        const planList = plansResponse?.features || (Array.isArray(plansResponse) ? plansResponse : plansResponse?.results || []);
        console.log('Planos reales encontrados en PostGIS:', planList);
        setAvailablePlans(planList);

        setLoading(false);
      })
      .catch((err) => {
        console.error('Error al inicializar datos:', err);
        setError('No se pudo conectar con el servidor espacial.');
        setLoading(false);
      });
  }, []);

  // 2. Al cambiar de Campus -> Enfocar en el mapa y filtrar edificios/planos disponibles
  const handleSelectCampus = (campusId) => {
    setSelectedCampusId(campusId);
    setSelectedBuildingId('');
    setSelectedFloorId('');
    setFloors([]);

    if (!campusId) return;

    // Buscar la geometría del campus seleccionado
    const selectedCampus = campuses.find((c) => String(c.id) === String(campusId));
    if (selectedCampus) {
      setActiveGeoData({
        type: 'FeatureCollection',
        features: [selectedCampus],
      });
    }

    // Extraer edificios o asociar los planos filtrados por campus
    const campusBuildings = selectedCampus?.properties?.buildings || [
      { id: `b_${campusId}`, name: 'Edificio Principal' },
    ];
    setBuildings(campusBuildings);
  };

  // 3. Al cambiar de Edificio -> Asignar los planos reales encontrados en la BBDD
  const handleSelectBuilding = (buildingId) => {
    setSelectedBuildingId(buildingId);
    setSelectedFloorId('');

    if (!buildingId) return;

    if (availablePlans.length > 0) {
      // Mapear los planos reales leídos desde PostGIS
      const realFloors = availablePlans.map((plan, index) => ({
        id: plan.id || index + 1,
        name: plan.properties?.name || plan.name || `Planta / Plano ${plan.id || index + 1}`,
        rawPlanData: plan,
      }));
      setFloors(realFloors);
    } else {
      setFloors([]);
      setError('No existen planos de interior registrados en la base de datos para este edificio.');
    }
  };

  // 4. Al cambiar de Planta -> Cargar el GeoJSON correspondiente
  const handleSelectFloor = (floorId) => {
    setSelectedFloorId(floorId);
    if (!floorId) return;

    setLoading(true);
    setError(null);

    // Buscar si el plano ya se encuentra cargado en memoria o realizar la consulta por ID
    const selectedFloorObj = floors.find((f) => String(f.id) === String(floorId));

    if (selectedFloorObj?.rawPlanData) {
      // Cargar la geometría GeoJSON directamente
      const geojsonPayload = selectedFloorObj.rawPlanData.type === 'Feature'
        ? { type: 'FeatureCollection', features: [selectedFloorObj.rawPlanData] }
        : selectedFloorObj.rawPlanData;

      setActiveGeoData(geojsonPayload);
      setLoading(false);
    } else {
      // Consulta a la API usando PlansService
      const fetchPlan = PlansService.plansRetrieve 
        ? PlansService.plansRetrieve({ id: floorId })
        : PlansService.plansList({ id: floorId });

      fetchPlan
        .then((planData) => {
          console.log('Plano devuelto por la API:', planData);
          setActiveGeoData(planData);
          setLoading(false);
        })
        .catch((err) => {
          console.error('Error al obtener el plano por ID:', err);
          setError(`No existe el plano con ID ${floorId} en la BBDD.`);
          setLoading(false);
        });
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h1 style={{ margin: 0, fontSize: '22px' }}>CampusNav3D</h1>

        {/* Desplegables en cascada: Campus -> Edificio -> Planta */}
        <div style={{ display: 'flex', gap: '10px' }}>
          <select 
            value={selectedCampusId} 
            onChange={(e) => handleSelectCampus(e.target.value)}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          >
            <option value="">-- Seleccionar Campus --</option>
            {campuses.map((c) => (
              <option key={c.id} value={c.id}>
                {c.properties?.name || c.name || `Campus ${c.id}`}
              </option>
            ))}
          </select>

          <select 
            value={selectedBuildingId} 
            onChange={(e) => handleSelectBuilding(e.target.value)}
            disabled={!selectedCampusId}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          >
            <option value="">-- Seleccionar Edificio --</option>
            {buildings.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name || `Edificio ${b.id}`}
              </option>
            ))}
          </select>

          <select 
            value={selectedFloorId} 
            onChange={(e) => handleSelectFloor(e.target.value)}
            disabled={!selectedBuildingId}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          >
            <option value="">-- Seleccionar Planta --</option>
            {floors.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </select>
        </div>
      </header>

      {loading && <p style={{ fontSize: '14px', color: '#666' }}>Cargando capa espacial...</p>}
      {error && <p style={{ color: 'red', fontSize: '14px' }}>{error}</p>}

      {!loading && activeGeoData && (
        <CampusMap geojson={activeGeoData} />
      )}
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/admin" element={<Admin />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}