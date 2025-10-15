import React, { useState } from 'react';
import styled from 'styled-components';
import { FileText, Image, Download, Trash2, Eye, Clock, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { fileService } from '../services/fileService';
import toast from 'react-hot-toast';

const FileListContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
`;

const Title = styled.h2`
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0;
`;

const RefreshButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  background: white;
  color: #666;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    color: #667eea;
  }
`;

const FilterTabs = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
`;

const FilterTab = styled.button`
  padding: 8px 16px;
  border: 2px solid #e9ecef;
  border-radius: 20px;
  background: white;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #667eea;
    color: #667eea;
  }
  
  &.active {
    background: #667eea;
    color: white;
    border-color: #667eea;
  }
`;

const FileGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const FileCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  }
`;

const FileHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
`;

const FileIcon = styled.div`
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

const FileInfo = styled.div`
  flex: 1;
`;

const FileName = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const FileMeta = styled.div`
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
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

const FileDetails = styled.div`
  margin-bottom: 16px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
`;

const DetailLabel = styled.span`
  color: #666;
`;

const DetailValue = styled.span`
  color: #333;
  font-weight: 500;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 16px;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const FileActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: white;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #f8f9fa;
    border-color: #667eea;
    color: #667eea;
  }
  
  &.primary {
    background: #667eea;
    color: white;
    border-color: #667eea;
  }
  
  &.primary:hover {
    background: #5a6fd8;
  }
  
  &.danger {
    color: #dc3545;
    border-color: #dc3545;
  }
  
  &.danger:hover {
    background: #fff5f5;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #666;
`;

const EmptyIcon = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  color: #ccc;
  font-size: 32px;
`;

const FileList = ({ onFileSelect }) => {
  const [filter, setFilter] = useState('all');
  const queryClient = useQueryClient();

  // Fetch files
  const { data: files, isLoading, error } = useQuery(
    'files',
    fileService.getAllFiles,
    {
      refetchInterval: 5000, // Poll every 5 seconds for updates
    }
  );

  // Delete file mutation
  const deleteMutation = useMutation(fileService.deleteFile, {
    onSuccess: () => {
      toast.success('File deleted successfully');
      queryClient.invalidateQueries('files');
      queryClient.invalidateQueries('recentFiles');
    },
    onError: (error) => {
      toast.error(`Failed to delete file: ${error.message}`);
    }
  });

  const handleDelete = (fileId, event) => {
    event.stopPropagation();
    if (window.confirm('Are you sure you want to delete this file?')) {
      deleteMutation.mutate(fileId);
    }
  };

  const handleDownload = (file, event) => {
    event.stopPropagation();
    if (file.status === 'completed' && file.processed_path) {
      const link = document.createElement('a');
      link.href = `/api/download/${file.id}`;
      link.download = `${file.filename}_processed.gltf`;
      link.click();
    } else {
      toast.error('File is not ready for download');
    }
  };

  const filteredFiles = files?.filter(file => {
    switch (filter) {
      case 'completed':
        return file.status === 'completed';
      case 'processing':
        return file.status === 'processing';
      case 'failed':
        return file.status === 'failed';
      case 'cad':
        return file.file_type === 'cad';
      case 'image':
        return file.file_type === 'image';
      default:
        return true;
    }
  }) || [];

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFileIcon = (fileType) => {
    return fileType === 'cad' ? <FileText size={24} /> : <Image size={24} />;
  };

  const getFileGradient = (fileType) => {
    return fileType === 'cad' 
      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle size={16} />;
      case 'processing': return <Clock size={16} />;
      case 'failed': return <AlertCircle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  if (isLoading) {
    return (
      <FileListContainer>
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <RefreshCw size={32} className="loading-spinner" />
          <p>Loading files...</p>
        </div>
      </FileListContainer>
    );
  }

  if (error) {
    return (
      <FileListContainer>
        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#dc3545' }}>
          <AlertCircle size={32} />
          <p>Failed to load files: {error.message}</p>
        </div>
      </FileListContainer>
    );
  }

  return (
    <FileListContainer>
      <Header>
        <Title>Files</Title>
        <RefreshButton onClick={() => queryClient.invalidateQueries('files')}>
          <RefreshCw size={20} />
          Refresh
        </RefreshButton>
      </Header>

      <FilterTabs>
        <FilterTab 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All ({files?.length || 0})
        </FilterTab>
        <FilterTab 
          className={filter === 'completed' ? 'active' : ''}
          onClick={() => setFilter('completed')}
        >
          Completed ({files?.filter(f => f.status === 'completed').length || 0})
        </FilterTab>
        <FilterTab 
          className={filter === 'processing' ? 'active' : ''}
          onClick={() => setFilter('processing')}
        >
          Processing ({files?.filter(f => f.status === 'processing').length || 0})
        </FilterTab>
        <FilterTab 
          className={filter === 'cad' ? 'active' : ''}
          onClick={() => setFilter('cad')}
        >
          CAD ({files?.filter(f => f.file_type === 'cad').length || 0})
        </FilterTab>
        <FilterTab 
          className={filter === 'image' ? 'active' : ''}
          onClick={() => setFilter('image')}
        >
          Images ({files?.filter(f => f.file_type === 'image').length || 0})
        </FilterTab>
      </FilterTabs>

      {filteredFiles.length === 0 ? (
        <EmptyState>
          <EmptyIcon>
            <FileText size={32} />
          </EmptyIcon>
          <h3>No files found</h3>
          <p>
            {filter === 'all' 
              ? 'Upload some files to get started'
              : `No files match the "${filter}" filter`
            }
          </p>
        </EmptyState>
      ) : (
        <FileGrid>
          {filteredFiles.map((file) => (
            <FileCard key={file.id} onClick={() => onFileSelect(file)}>
              <FileHeader>
                <FileIcon gradient={getFileGradient(file.file_type)}>
                  {getFileIcon(file.file_type)}
                </FileIcon>
                <FileInfo>
                  <FileName title={file.filename}>{file.filename}</FileName>
                  <FileMeta>
                    {formatFileSize(file.file_size)}
                    <StatusBadge status={file.status}>
                      {getStatusIcon(file.status)}
                      {file.status}
                    </StatusBadge>
                  </FileMeta>
                </FileInfo>
              </FileHeader>

              <FileDetails>
                <DetailRow>
                  <DetailLabel>Type:</DetailLabel>
                  <DetailValue>{file.file_type.toUpperCase()}</DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Uploaded:</DetailLabel>
                  <DetailValue>{formatDate(file.created_at)}</DetailValue>
                </DetailRow>
                {file.metadata && (
                  <DetailRow>
                    <DetailLabel>Vertices:</DetailLabel>
                    <DetailValue>
                      {file.metadata.vertex_count?.toLocaleString() || 'Unknown'}
                    </DetailValue>
                  </DetailRow>
                )}
              </FileDetails>

              {file.status === 'processing' && file.progress !== undefined && (
                <ProgressBar>
                  <ProgressFill progress={file.progress} />
                </ProgressBar>
              )}

              <FileActions>
                <ActionButton 
                  className="primary"
                  onClick={(e) => onFileSelect(file)}
                >
                  <Eye size={16} />
                  View
                </ActionButton>
                {file.status === 'completed' && (
                  <ActionButton 
                    onClick={(e) => handleDownload(file, e)}
                  >
                    <Download size={16} />
                    Download
                  </ActionButton>
                )}
                <ActionButton 
                  className="danger"
                  onClick={(e) => handleDelete(file.id, e)}
                >
                  <Trash2 size={16} />
                  Delete
                </ActionButton>
              </FileActions>
            </FileCard>
          ))}
        </FileGrid>
      )}
    </FileListContainer>
  );
};

export default FileList;