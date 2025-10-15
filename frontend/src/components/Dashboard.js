import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Upload, FileText, Image, Cube, TrendingUp, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { useQuery } from 'react-query';
import { fileService } from '../services/fileService';
import { digitalTwinService } from '../services/digitalTwinService';

const DashboardContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 20px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  }
`;

const QuickActions = styled(Card)`
  grid-column: 1 / -1;
`;

const QuickActionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
`;

const ActionButton = styled.button`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  border: 2px dashed #e9ecef;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    background: #f8f9ff;
    transform: translateY(-2px);
  }
`;

const ActionIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  background: ${props => props.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
`;

const ActionTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

const ActionDescription = styled.p`
  font-size: 14px;
  color: #666;
  text-align: center;
  margin: 0;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 16px;
`;

const StatCard = styled.div`
  background: ${props => props.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  color: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  font-size: 14px;
  opacity: 0.9;
`;

const RecentFiles = styled(Card)`
  grid-column: 1 / -1;
`;

const FileList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #e9ecef;
    transform: translateX(4px);
  }
`;

const FileIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  background: ${props => props.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
`;

const FileInfo = styled.div`
  flex: 1;
`;

const FileName = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
`;

const FileMeta = styled.div`
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const StatusBadge = styled.span`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => {
    switch (props.status) {
      case 'completed': return '#e8f5e8';
      case 'processing': return '#fff3e0';
      case 'failed': return '#ffebee';
      default: return '#e3f2fd';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'completed': return '#2e7d32';
      case 'processing': return '#f57c00';
      case 'failed': return '#c62828';
      default: return '#1976d2';
    }
  }};
`;

const ProcessingProgress = styled.div`
  width: 100%;
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 8px;
`;

const ProgressBar = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const Dashboard = ({ onFileSelect, onUploadClick, onFilesClick }) => {
  const [stats, setStats] = useState({
    totalFiles: 0,
    completedFiles: 0,
    processingFiles: 0,
    totalDigitalTwins: 0
  });

  // Fetch recent files
  const { data: recentFiles, isLoading: filesLoading } = useQuery(
    'recentFiles',
    fileService.getRecentFiles,
    {
      refetchInterval: 5000, // Refetch every 5 seconds
    }
  );

  // Fetch digital twin stats
  const { data: digitalTwinStats } = useQuery(
    'digitalTwinStats',
    digitalTwinService.getStats
  );

  useEffect(() => {
    if (recentFiles) {
      const completed = recentFiles.filter(f => f.status === 'completed').length;
      const processing = recentFiles.filter(f => f.status === 'processing').length;
      
      setStats(prev => ({
        ...prev,
        totalFiles: recentFiles.length,
        completedFiles: completed,
        processingFiles: processing,
        totalDigitalTwins: digitalTwinStats?.total || 0
      }));
    }
  }, [recentFiles, digitalTwinStats]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle size={16} />;
      case 'processing': return <Clock size={16} />;
      case 'failed': return <AlertCircle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <DashboardContainer>
      <QuickActions>
        <h2>Quick Actions</h2>
        <QuickActionsGrid>
          <ActionButton onClick={onUploadClick}>
            <ActionIcon gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
              <Upload size={24} />
            </ActionIcon>
            <ActionTitle>Upload Files</ActionTitle>
            <ActionDescription>Upload CAD files or 2D images</ActionDescription>
          </ActionButton>
          
          <ActionButton onClick={onFilesClick}>
            <ActionIcon gradient="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
              <Files size={24} />
            </ActionIcon>
            <ActionTitle>Browse Files</ActionTitle>
            <ActionDescription>View all uploaded files</ActionDescription>
          </ActionButton>
          
          <ActionButton>
            <ActionIcon gradient="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
              <Cube size={24} />
            </ActionIcon>
            <ActionTitle>Digital Twins</ActionTitle>
            <ActionDescription>Manage digital twins</ActionDescription>
          </ActionButton>
        </QuickActionsGrid>
      </QuickActions>

      <Card>
        <h3>File Statistics</h3>
        <StatsGrid>
          <StatCard>
            <StatValue>{stats.totalFiles}</StatValue>
            <StatLabel>Total Files</StatLabel>
          </StatCard>
          <StatCard gradient="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
            <StatValue>{stats.completedFiles}</StatValue>
            <StatLabel>Completed</StatLabel>
          </StatCard>
          <StatCard gradient="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
            <StatValue>{stats.processingFiles}</StatValue>
            <StatLabel>Processing</StatLabel>
          </StatCard>
          <StatCard gradient="linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
            <StatValue>{stats.totalDigitalTwins}</StatValue>
            <StatLabel>Digital Twins</StatLabel>
          </StatCard>
        </StatsGrid>
      </Card>

      <RecentFiles>
        <h3>Recent Files</h3>
        {filesLoading ? (
          <div>Loading recent files...</div>
        ) : recentFiles && recentFiles.length > 0 ? (
          <FileList>
            {recentFiles.slice(0, 5).map((file) => (
              <FileItem key={file.id} onClick={() => onFileSelect(file)}>
                <FileIcon gradient={file.file_type === 'cad' 
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
                }>
                  {file.file_type === 'cad' ? <FileText size={20} /> : <Image size={20} />}
                </FileIcon>
                <FileInfo>
                  <FileName>{file.filename}</FileName>
                  <FileMeta>
                    {formatFileSize(file.file_size)}
                    <StatusBadge status={file.status}>
                      {getStatusIcon(file.status)}
                      {file.status}
                    </StatusBadge>
                    {file.progress !== undefined && (
                      <ProcessingProgress>
                        <ProgressBar progress={file.progress} />
                      </ProcessingProgress>
                    )}
                  </FileMeta>
                </FileInfo>
              </FileItem>
            ))}
          </FileList>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            No files uploaded yet. Click "Upload Files" to get started.
          </div>
        )}
      </RecentFiles>
    </DashboardContainer>
  );
};

export default Dashboard;