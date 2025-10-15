import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import styled from 'styled-components';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import FileList from './components/FileList';
import DigitalTwinViewer from './components/DigitalTwinViewer';
import Dashboard from './components/Dashboard';
import { useFileStore } from './hooks/useFileStore';
import { useDigitalTwinStore } from './hooks/useDigitalTwinStore';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const MainContent = styled.main`
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
`;

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedFile, setSelectedFile] = useState(null);
  
  const { files, loadFiles } = useFileStore();
  const { digitalTwins, loadDigitalTwins } = useDigitalTwinStore();

  useEffect(() => {
    // Load initial data
    loadFiles();
    loadDigitalTwins();
  }, [loadFiles, loadDigitalTwins]);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setCurrentView('viewer');
  };

  const handleBackToDashboard = () => {
    setSelectedFile(null);
    setCurrentView('dashboard');
  };

  const renderContent = () => {
    switch (currentView) {
      case 'upload':
        return <FileUpload onUploadComplete={() => setCurrentView('dashboard')} />;
      case 'viewer':
        return (
          <DigitalTwinViewer 
            file={selectedFile} 
            onBack={handleBackToDashboard}
          />
        );
      case 'files':
        return <FileList onFileSelect={handleFileSelect} />;
      default:
        return (
          <Dashboard 
            onFileSelect={handleFileSelect}
            onUploadClick={() => setCurrentView('upload')}
            onFilesClick={() => setCurrentView('files')}
          />
        );
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <AppContainer>
        <Router>
          <Header 
            currentView={currentView}
            onViewChange={setCurrentView}
            onBack={currentView !== 'dashboard' ? handleBackToDashboard : null}
          />
          <MainContent>
            {renderContent()}
          </MainContent>
        </Router>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#fff',
              color: '#333',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
              borderRadius: '8px',
            },
          }}
        />
      </AppContainer>
    </QueryClientProvider>
  );
}

export default App;