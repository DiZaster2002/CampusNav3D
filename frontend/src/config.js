import { OpenAPI } from './api';

export const getAuthToken = () => localStorage.getItem('auth_token');
export const setAuthToken = (token) => localStorage.setItem('auth_token', token);
export const removeAuthToken = () => localStorage.removeItem('auth_token');

export const initApiConfig = () => {
  // Dirección del backend Django en Docker
  OpenAPI.BASE = 'http://localhost:8000';

  // Inyección del token para peticiones autenticadas
  OpenAPI.TOKEN = async () => {
    return getAuthToken() || '';
  };
};