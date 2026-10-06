import { OpenAPI } from './api';
import { getToken } from './auth';

export const initApiConfig = () => {
  // Dirección del backend Django en Docker
  OpenAPI.BASE = 'http://localhost:8000';

  // Inyección del token para peticiones autenticadas
  OpenAPI.TOKEN = async () => {
    const token = getToken();
    return token ? token : '';
  };
};