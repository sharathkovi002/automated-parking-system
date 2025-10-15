import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
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

export const digitalTwinService = {
  // Get digital twin data
  getDigitalTwin: async (fileId) => {
    const response = await api.get(`/api/digital-twin/${fileId}`);
    return response.data;
  },

  // Update digital twin data
  updateDigitalTwin: async (fileId, updates) => {
    const response = await api.put(`/api/digital-twin/${fileId}`, {
      file_id: fileId,
      updates
    });
    return response.data;
  },

  // Get materials for a digital twin
  getMaterials: async (fileId) => {
    const response = await api.get(`/api/models/${fileId}/materials`);
    return response.data;
  },

  // Update materials
  updateMaterials: async (fileId, materials) => {
    const response = await api.put(`/api/models/${fileId}/materials`, materials);
    return response.data;
  },

  // Get animations
  getAnimations: async (fileId) => {
    const response = await api.get(`/api/models/${fileId}/animations`);
    return response.data;
  },

  // Update animations
  updateAnimations: async (fileId, animations) => {
    const response = await api.put(`/api/models/${fileId}/animations`, animations);
    return response.data;
  },

  // Get physics properties
  getPhysicsProperties: async (fileId) => {
    const response = await api.get(`/api/models/${fileId}/physics`);
    return response.data;
  },

  // Update physics properties
  updatePhysicsProperties: async (fileId, physics) => {
    const response = await api.put(`/api/models/${fileId}/physics`, physics);
    return response.data;
  },

  // Add sensor data
  addSensorData: async (fileId, sensorData) => {
    const response = await api.post(`/api/digital-twin/${fileId}/sensor-data`, sensorData);
    return response.data;
  },

  // Get sensor data
  getSensorData: async (fileId) => {
    const response = await api.get(`/api/digital-twin/${fileId}/sensor-data`);
    return response.data;
  },

  // Start simulation
  startSimulation: async (fileId, parameters) => {
    const response = await api.post(`/api/digital-twin/${fileId}/simulate`, parameters);
    return response.data;
  },

  // Export digital twin
  exportDigitalTwin: async (fileId, format = 'gltf') => {
    const response = await api.get(`/api/digital-twin/${fileId}/export?format=${format}`);
    return response.data;
  },

  // Get digital twin statistics
  getStats: async () => {
    const response = await api.get('/api/digital-twin/stats');
    return response.data;
  },

  // WebSocket connection for real-time updates
  createWebSocketConnection: (fileId, onMessage) => {
    const wsUrl = `ws://localhost:8000/api/digital-twin/${fileId}/ws`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return ws;
  },
};

export default digitalTwinService;