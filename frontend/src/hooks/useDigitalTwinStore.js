import { create } from 'zustand';
import { digitalTwinService } from '../services/digitalTwinService';

const useDigitalTwinStore = create((set, get) => ({
  digitalTwins: {},
  loading: false,
  error: null,
  
  // Actions
  setDigitalTwin: (fileId, digitalTwin) => set((state) => ({
    digitalTwins: {
      ...state.digitalTwins,
      [fileId]: digitalTwin
    }
  })),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  // Load digital twin data
  loadDigitalTwin: async (fileId) => {
    set({ loading: true, error: null });
    try {
      const digitalTwin = await digitalTwinService.getDigitalTwin(fileId);
      set((state) => ({
        digitalTwins: {
          ...state.digitalTwins,
          [fileId]: digitalTwin
        },
        loading: false
      }));
      return digitalTwin;
    } catch (error) {
      set({ error: error.message, loading: false });
      throw error;
    }
  },
  
  // Load all digital twins
  loadDigitalTwins: async () => {
    set({ loading: true, error: null });
    try {
      // This would need to be implemented in the API
      // For now, we'll just set loading to false
      set({ loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  // Update digital twin
  updateDigitalTwin: async (fileId, updates) => {
    try {
      await digitalTwinService.updateDigitalTwin(fileId, updates);
      set((state) => ({
        digitalTwins: {
          ...state.digitalTwins,
          [fileId]: {
            ...state.digitalTwins[fileId],
            ...updates
          }
        }
      }));
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
  
  // Update materials
  updateMaterials: async (fileId, materials) => {
    try {
      await digitalTwinService.updateMaterials(fileId, materials);
      set((state) => ({
        digitalTwins: {
          ...state.digitalTwins,
          [fileId]: {
            ...state.digitalTwins[fileId],
            materials
          }
        }
      }));
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
  
  // Update animations
  updateAnimations: async (fileId, animations) => {
    try {
      await digitalTwinService.updateAnimations(fileId, animations);
      set((state) => ({
        digitalTwins: {
          ...state.digitalTwins,
          [fileId]: {
            ...state.digitalTwins[fileId],
            animations
          }
        }
      }));
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
  
  // Update physics properties
  updatePhysicsProperties: async (fileId, physics) => {
    try {
      await digitalTwinService.updatePhysicsProperties(fileId, physics);
      set((state) => ({
        digitalTwins: {
          ...state.digitalTwins,
          [fileId]: {
            ...state.digitalTwins[fileId],
            physics_properties: physics
          }
        }
      }));
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
  
  // Add sensor data
  addSensorData: async (fileId, sensorData) => {
    try {
      await digitalTwinService.addSensorData(fileId, sensorData);
      set((state) => ({
        digitalTwins: {
          ...state.digitalTwins,
          [fileId]: {
            ...state.digitalTwins[fileId],
            sensor_data: {
              ...state.digitalTwins[fileId]?.sensor_data,
              [sensorData.sensor_id]: sensorData
            }
          }
        }
      }));
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },
  
  // Get digital twin by file ID
  getDigitalTwin: (fileId) => {
    const { digitalTwins } = get();
    return digitalTwins[fileId];
  },
  
  // Get all digital twins
  getAllDigitalTwins: () => {
    const { digitalTwins } = get();
    return Object.values(digitalTwins);
  },
  
  // Get digital twin statistics
  getStats: () => {
    const { digitalTwins } = get();
    const allTwins = Object.values(digitalTwins);
    
    return {
      total: allTwins.length,
      withMaterials: allTwins.filter(twin => twin.materials?.length > 0).length,
      withAnimations: allTwins.filter(twin => twin.animations?.length > 0).length,
      withPhysics: allTwins.filter(twin => twin.physics_properties).length,
      withSensorData: allTwins.filter(twin => twin.sensor_data).length,
    };
  },
  
  // Clear error
  clearError: () => set({ error: null }),
  
  // Reset store
  reset: () => set({ 
    digitalTwins: {}, 
    loading: false, 
    error: null 
  }),
}));

export { useDigitalTwinStore };