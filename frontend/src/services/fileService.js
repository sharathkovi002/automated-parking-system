import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for file uploads
});

// Request interceptor to add auth headers if needed
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

export const fileService = {
  // Upload a file
  uploadFile: async (formData) => {
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get all files
  getAllFiles: async () => {
    const response = await api.get('/api/files/');
    return response.data;
  },

  // Get recent files
  getRecentFiles: async (limit = 10) => {
    const response = await api.get(`/api/files/?limit=${limit}`);
    return response.data;
  },

  // Get file by ID
  getFile: async (fileId) => {
    const response = await api.get(`/api/files/${fileId}`);
    return response.data;
  },

  // Get file status
  getFileStatus: async (fileId) => {
    const response = await api.get(`/api/files/${fileId}/status`);
    return response.data;
  },

  // Delete file
  deleteFile: async (fileId) => {
    const response = await api.delete(`/api/files/${fileId}`);
    return response.data;
  },

  // Download processed file
  downloadFile: async (fileId) => {
    const response = await api.get(`/api/download/${fileId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Get file processing progress
  getProcessingProgress: async (fileId) => {
    const response = await api.get(`/api/files/${fileId}/status`);
    return response.data;
  },
};

export default fileService;