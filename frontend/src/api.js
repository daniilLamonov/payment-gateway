import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

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

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_username');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await axios.post(`${API_URL}/auth/login`, formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
  return response.data;
};


export const verifyAuth = async () => {
  const response = await api.get('/auth/verify');
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/auth/logout');
  localStorage.removeItem('admin_token');
  localStorage.removeItem('admin_username');
  return response.data;
};

export const generateQR = async () => {
  const response = await axios.get(`${API_URL}/generate-qr`);
  return response.data;
};

export const getPaymentLink = async () => {
  const response = await axios.get(`${API_URL}/payment-link`);
  return response.data;
};

export const updateDynamicRedirect = async (data) => {
  const response = await api.post('/admin/dynamic-redirect', data);
  return response.data;
};

export const getAllRedirects = async () => {
  const response = await api.get('/admin/dynamic-redirects');
  return response.data;
};

export const getCurrentRedirect = async () => {
  const response = await api.get('/admin/current-redirect');
  return response.data;
};

export const updateWorkingHours = async (data) => {
  const response = await api.put('/admin/working-hours', data);
  return response.data;
};

export const getAllWorkingHours = async () => {
  const response = await api.get('/admin/working-hours');
  return response.data;
};
export const toggleRedirectStatus = async (redirectId) => {
  const response = await api.patch(`/admin/dynamic-redirect/${redirectId}/toggle`);
  return response.data;
};

