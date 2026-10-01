import { OpenAPI } from './api'; // Importado del cliente generado
import { getAuthToken } from './auth'; // Tu módulo de autenticación existente

export const setupApiClient = () => {
    // Configura la dirección base del servidor Django
    OpenAPI.BASE = 'http://localhost:8000';

    // Inyecta dinámicamente el Token si existe en localStorage
    OpenAPI.TOKEN = async () => {
        const token = getAuthToken();
        return token ? token : '';
    };
};