import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for consistent error extraction
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const customError = {
      message: error.response?.data?.detail || error.message || 'An unexpected network error occurred.',
      status: error.response?.status || 0,
      original: error,
    };
    return Promise.reject(customError);
  }
);

export const apiService = {
  // System Health
  checkHealth: () => api.get('/health'),

  // Dashboard API
  getDashboardSummary: () => api.get('/api/dashboard/summary'),

  // Customers API
  getCustomers: (params = {}) => api.get('/api/customers', { params }),
  getCustomer: (id) => api.get(`/api/customers/${id}`),
  getTopSpenders: (limit = 10) => api.get('/api/customers/top-spenders', { params: { limit } }),
  searchCustomers: (query, cluster = null, limit = 20) =>
    api.get('/api/customers/search', { params: { query, cluster, limit } }),
  getCustomerProfile: (id) => api.get(`/api/customers/${id}/profile`),

  // Products API
  getProducts: (params = {}) => api.get('/api/products', { params }),
  getProduct: (id) => api.get(`/api/products/${id}`),
  getProductsByCategory: (category, params = {}) =>
    api.get(`/api/products/category/${encodeURIComponent(category)}`, { params }),
  getTopProducts: (limit = 10) => api.get('/api/products/top', { params: { limit } }),

  // Orders API
  getOrders: (params = {}) => api.get('/api/orders', { params }),
  getOrder: (id) => api.get(`/api/orders/${id}`),
  getOrdersByStatus: (status, params = {}) =>
    api.get(`/api/orders/status/${encodeURIComponent(status)}`, { params }),
  getRecentOrders: (limit = 10) => api.get('/api/orders/recent', { params: { limit } }),

  // Segments API
  getSegments: () => api.get('/api/segments'),
  getSegmentProfiles: () => api.get('/api/segments/profiles'),
  getSegmentDetails: (clusterId) => api.get(`/api/segments/${clusterId}`),
  getSegmentCustomers: (clusterId, params = {}) =>
    api.get(`/api/segments/${clusterId}/customers`, { params }),

  // Recommendations API
  getRecommendations: (params = {}) => api.get('/api/recommendations', { params }),
  getCustomerRecommendations: (customerId, limit = 10) =>
    api.get(`/api/recommendations/${customerId}`, { params: { limit } }),

  // Association Rules API
  getAssociationRules: (params = {}) => api.get('/api/association-rules', { params }),
  getTopAssociationRules: (limit = 10) =>
    api.get('/api/association-rules/top', { params: { limit } }),

  // Sales & Analytics API
  getSalesSummary: () => api.get('/api/sales/summary'),
  getMonthlySales: () => api.get('/api/sales/monthly'),
  getCategorySales: (limit = 10) => api.get('/api/sales/categories', { params: { limit } }),
  getProductSales: (limit = 10) => api.get('/api/sales/products', { params: { limit } }),
  getSellerSales: (limit = 10) => api.get('/api/sales/sellers', { params: { limit } }),
  getOrderStatus: () => api.get('/api/sales/order-status'),
};

export default apiService;
