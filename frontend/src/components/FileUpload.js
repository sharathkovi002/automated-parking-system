import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Image, X, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { useMutation, useQueryClient } from 'react-query';
import { fileService } from '../services/fileService';
import toast from 'react-hot-toast';

const UploadContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const UploadCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
`;

const Dropzone = styled.div`
  border: 2px dashed ${props => props.isDragActive ? '#667eea' : props.isDragReject ? '#dc3545' : '#ccc'};
  border-radius: 12px;
  padding: 60px 40px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => props.isDragActive ? '#f8f9ff' : props.isDragReject ? '#fff5f5' : 'white'};
  
  &:hover {
    border-color: #667eea;
    background: #f8f9ff;
  }
`;

const DropzoneContent = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
`;

const UploadIcon = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  margin-bottom: 16px;
`;

const UploadTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
`;

const UploadDescription = styled.p`
  font-size: 16px;
  color: #666;
  margin: 0 0 24px 0;
`;

const SupportedFormats = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
`;

const FormatTag = styled.span`
  padding: 4px 12px;
  background: #f8f9fa;
  border-radius: 16px;
  font-size: 14px;
  color: #666;
  border: 1px solid #e9ecef;
`;

const FileList = styled.div`
  margin-top: 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
`;

const FileIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  background: ${props => props.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
`;

const FileInfo = styled.div`
  flex: 1;
  text-align: left;
`;

const FileName = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
`;

const FileSize = styled.div`
  font-size: 14px;
  color: #666;
`;

const FileStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
`;

const StatusIcon = styled.div`
  color: ${props => {
    switch (props.status) {
      case 'completed': return '#28a745';
      case 'processing': return '#ffc107';
      case 'failed': return '#dc3545';
      default: return '#6c757d';
    }
  }};
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 8px;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.3s ease;
  
  &:hover {
    background: #fff5f5;
  }
`;

const UploadButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 24px auto 0;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const FileUpload = ({ onUploadComplete }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const queryClient = useQueryClient();

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0
    }));
    
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/step': ['.step', '.stp'],
      'application/iges': ['.iges', '.igs'],
      'application/sla': ['.stl'],
      'application/obj': ['.obj'],
      'application/ply': ['.ply'],
      'application/x-3ds': ['.3ds'],
      'application/x-fbx': ['.fbx'],
      'application/x-collada': ['.dae'],
      'model/gltf+json': ['.gltf'],
      'model/gltf-binary': ['.glb'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif'],
      'image/bmp': ['.bmp'],
      'image/webp': ['.webp']
    },
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: true
  });

  const uploadMutation = useMutation(fileService.uploadFile, {
    onSuccess: (data) => {
      toast.success(`File ${data.filename} uploaded successfully!`);
      queryClient.invalidateQueries('recentFiles');
      queryClient.invalidateQueries('files');
    },
    onError: (error) => {
      toast.error(`Upload failed: ${error.message}`);
    }
  });

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    
    try {
      for (const fileItem of files) {
        if (fileItem.status === 'pending') {
          fileItem.status = 'uploading';
          fileItem.progress = 0;
          
          // Simulate progress
          const progressInterval = setInterval(() => {
            if (fileItem.progress < 90) {
              fileItem.progress += Math.random() * 10;
              setFiles([...files]);
            }
          }, 200);
          
          try {
            const formData = new FormData();
            formData.append('file', fileItem.file);
            
            const result = await uploadMutation.mutateAsync(formData);
            
            clearInterval(progressInterval);
            fileItem.status = 'completed';
            fileItem.progress = 100;
            fileItem.fileId = result.file_id;
            
            setFiles([...files]);
          } catch (error) {
            clearInterval(progressInterval);
            fileItem.status = 'failed';
            setFiles([...files]);
          }
        }
      }
      
      // Wait a bit then redirect
      setTimeout(() => {
        onUploadComplete();
      }, 2000);
      
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) {
      return <Image size={24} />;
    }
    return <FileText size={24} />;
  };

  const getFileGradient = (fileType) => {
    if (fileType.startsWith('image/')) {
      return 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
    }
    return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle size={16} />;
      case 'failed': return <AlertCircle size={16} />;
      case 'uploading': return <Clock size={16} />;
      default: return <Clock size={16} />;
    }
  };

  return (
    <UploadContainer>
      <UploadCard>
        <UploadTitle>Upload Files</UploadTitle>
        <UploadDescription>
          Drag and drop your CAD files or 2D images here, or click to browse
        </UploadDescription>
        
        <Dropzone {...getRootProps()} isDragActive={isDragActive} isDragReject={isDragReject}>
          <input {...getInputProps()} />
          <DropzoneContent>
            <UploadIcon>
              <Upload size={32} />
            </UploadIcon>
            <div>
              <h3>
                {isDragActive 
                  ? 'Drop the files here...' 
                  : isDragReject 
                    ? 'Some files are not supported'
                    : 'Choose files or drag them here'
                }
              </h3>
              <p>Supports CAD files and 2D images up to 100MB each</p>
            </div>
          </DropzoneContent>
        </Dropzone>
        
        <SupportedFormats>
          <FormatTag>STEP (.step, .stp)</FormatTag>
          <FormatTag>IGES (.iges, .igs)</FormatTag>
          <FormatTag>STL (.stl)</FormatTag>
          <FormatTag>OBJ (.obj)</FormatTag>
          <FormatTag>PLY (.ply)</FormatTag>
          <FormatTag>3DS (.3ds)</FormatTag>
          <FormatTag>FBX (.fbx)</FormatTag>
          <FormatTag>JPEG (.jpg, .jpeg)</FormatTag>
          <FormatTag>PNG (.png)</FormatTag>
          <FormatTag>TIFF (.tiff, .tif)</FormatTag>
        </SupportedFormats>
        
        {files.length > 0 && (
          <>
            <FileList>
              {files.map((fileItem) => (
                <FileItem key={fileItem.id}>
                  <FileIcon gradient={getFileGradient(fileItem.type)}>
                    {getFileIcon(fileItem.type)}
                  </FileIcon>
                  <FileInfo>
                    <FileName>{fileItem.name}</FileName>
                    <FileSize>{formatFileSize(fileItem.size)}</FileSize>
                    <FileStatus>
                      <StatusIcon status={fileItem.status}>
                        {getStatusIcon(fileItem.status)}
                      </StatusIcon>
                      {fileItem.status}
                    </FileStatus>
                    {fileItem.progress > 0 && fileItem.progress < 100 && (
                      <ProgressBar>
                        <ProgressFill progress={fileItem.progress} />
                      </ProgressBar>
                    )}
                  </FileInfo>
                  {fileItem.status === 'pending' && (
                    <RemoveButton onClick={() => removeFile(fileItem.id)}>
                      <X size={16} />
                    </RemoveButton>
                  )}
                </FileItem>
              ))}
            </FileList>
            
            <UploadButton 
              onClick={handleUpload} 
              disabled={uploading || files.every(f => f.status !== 'pending')}
            >
              <Upload size={20} />
              {uploading ? 'Uploading...' : 'Upload Files'}
            </UploadButton>
          </>
        )}
      </UploadCard>
    </UploadContainer>
  );
};

export default FileUpload;