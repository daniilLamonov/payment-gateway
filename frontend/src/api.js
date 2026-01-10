import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// ============================================
// AXIOS INSTANCE С АВТОМАТИЧЕСКИМ ТОКЕНОМ
// ============================================

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Интерсептор для добавления токена ко всем запросам
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерсептор для обработки ошибок аутентификации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен невалидный или истёк
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_username');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================
// AUTHENTICATION API
// ============================================

export const login = async (username, password) => {
  const response = await axios.post(`${API_URL}/api/auth/login`, {
    username,
    password
  });
  return response.data;
};

export const verifyAuth = async () => {
  const response = await api.get('/api/auth/verify');
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/api/auth/logout');
  localStorage.removeItem('admin_token');
  localStorage.removeItem('admin_username');
  return response.data;
};

// ============================================
// PAYMENT API (без аутентификации)
// ============================================

export const generateQR = async () => {
  const response = await axios.get(`${API_URL}/api/generate-qr`);
  return response.data;
};

export const getPaymentLink = async () => {
  const response = await axios.get(`${API_URL}/api/payment-link`);
  return response.data;
};

// ============================================
// ADMIN API (требует аутентификацию)
// ============================================

export const updateDynamicRedirect = async (data) => {
  const response = await api.post('/api/admin/dynamic-redirect', data);
  return response.data;
};

export const getAllRedirects = async () => {
  const response = await api.get('/api/admin/dynamic-redirects');
  return response.data;
};

export const getCurrentRedirect = async () => {
  const response = await api.get('/api/admin/current-redirect');
  return response.data;
};

export const updateWorkingHours = async (data) => {
  const response = await api.put('/api/admin/working-hours', data);
  return response.data;
};

export const getAllWorkingHours = async () => {
  const response = await api.get('/api/admin/working-hours');
  return response.data;
};
