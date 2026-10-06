// Clave para guardar el token en el almacenamiento local
const TOKEN_KEY = 'campusnav_auth_token';

export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

export const isAuthenticated = () => {
  const token = getToken();
  return !!token && token !== 'null' && token !== 'undefined';
};