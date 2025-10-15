import { create } from 'zustand';
import { fileService } from '../services/fileService';

const useFileStore = create((set, get) => ({
  files: [],
  loading: false,
  error: null,
  
  // Actions
  setFiles: (files) => set({ files }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  // Load files from API
  loadFiles: async () => {
    set({ loading: true, error: null });
    try {
      const files = await fileService.getAllFiles();
      set({ files, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  // Add a new file
  addFile: (file) => set((state) => ({ 
    files: [file, ...state.files] 
  })),
  
  // Update file status
  updateFileStatus: (fileId, status, progress) => set((state) => ({
    files: state.files.map(file => 
      file.id === fileId 
        ? { ...file, status, progress }
        : file
    )
  })),
  
  // Remove a file
  removeFile: (fileId) => set((state) => ({
    files: state.files.filter(file => file.id !== fileId)
  })),
  
  // Get file by ID
  getFile: (fileId) => {
    const { files } = get();
    return files.find(file => file.id === fileId);
  },
  
  // Get files by status
  getFilesByStatus: (status) => {
    const { files } = get();
    return files.filter(file => file.status === status);
  },
  
  // Get files by type
  getFilesByType: (type) => {
    const { files } = get();
    return files.filter(file => file.file_type === type);
  },
  
  // Get completed files
  getCompletedFiles: () => {
    const { files } = get();
    return files.filter(file => file.status === 'completed');
  },
  
  // Get processing files
  getProcessingFiles: () => {
    const { files } = get();
    return files.filter(file => file.status === 'processing');
  },
  
  // Get file statistics
  getFileStats: () => {
    const { files } = get();
    return {
      total: files.length,
      completed: files.filter(f => f.status === 'completed').length,
      processing: files.filter(f => f.status === 'processing').length,
      failed: files.filter(f => f.status === 'failed').length,
      cad: files.filter(f => f.file_type === 'cad').length,
      image: files.filter(f => f.file_type === 'image').length,
    };
  },
}));

export { useFileStore };