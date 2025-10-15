import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF, Text, Box, Sphere } from '@react-three/drei';
import { ArrowLeft, RotateCcw, ZoomIn, ZoomOut, Play, Pause, Settings, Download, Share } from 'lucide-react';
import { useQuery } from 'react-query';
import { digitalTwinService } from '../services/digitalTwinService';
import { fileService } from '../services/fileService';
import * as THREE from 'three';

const ViewerContainer = styled.div`
  display: flex;
  height: calc(100vh - 90px);
  background: #f0f0f0;
`;

const Sidebar = styled.div`
  width: 300px;
  background: white;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
`;

const SidebarHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
`;

const FileInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const FileName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
`;

const FileMeta = styled.div`
  font-size: 14px;
  color: #666;
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

const SidebarContent = styled.div`
  flex: 1;
  padding: 20px;
`;

const Section = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h4`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
`;

const ControlGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ControlButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #f8f9fa;
    border-color: #667eea;
  }
  
  &.active {
    background: #667eea;
    color: white;
    border-color: #667eea;
  }
`;

const Slider = styled.input`
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: #e9ecef;
  outline: none;
  -webkit-appearance: none;
  
  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
  }
  
  &::-moz-range-thumb {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
    border: none;
  }
`;

const SliderLabel = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
`;

const MaterialList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const MaterialItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: #e9ecef;
  }
  
  &.selected {
    background: #667eea;
    color: white;
  }
`;

const MaterialColor = styled.div`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: ${props => props.color || '#ccc'};
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const ViewerArea = styled.div`
  flex: 1;
  position: relative;
  background: #f0f0f0;
`;

const ViewerControls = styled.div`
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 10;
`;

const ControlButtonSmall = styled.button`
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  
  &:hover {
    background: rgba(255, 255, 255, 1);
    transform: scale(1.05);
  }
`;

const ViewerInfo = styled.div`
  position: absolute;
  bottom: 16px;
  left: 16px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 10;
  backdrop-filter: blur(10px);
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
`;

const LoadingSpinner = styled.div`
  width: 40px;
  height: 40px;
  border: 4px solid #e9ecef;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// 3D Model Component
function Model({ url, onLoad }) {
  const { scene } = useGLTF(url);
  
  useEffect(() => {
    if (scene && onLoad) {
      onLoad(scene);
    }
  }, [scene, onLoad]);
  
  return <primitive object={scene} />;
}

// Placeholder model for when no model is loaded
function PlaceholderModel() {
  return (
    <group>
      <Box args={[1, 1, 1]} position={[0, 0, 0]}>
        <meshStandardMaterial color="#667eea" />
      </Box>
      <Text
        position={[0, 1.5, 0]}
        fontSize={0.2}
        color="#666"
        anchorX="center"
        anchorY="middle"
      >
        No model loaded
      </Text>
    </group>
  );
}

const DigitalTwinViewer = ({ file, onBack }) => {
  const [selectedMaterial, setSelectedMaterial] = useState(null);
  const [animationPlaying, setAnimationPlaying] = useState(false);
  const [rotationSpeed, setRotationSpeed] = useState(0.01);
  const [zoom, setZoom] = useState(1);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const controlsRef = useRef();

  // Fetch digital twin data
  const { data: digitalTwinData, isLoading: digitalTwinLoading } = useQuery(
    ['digitalTwin', file?.id],
    () => digitalTwinService.getDigitalTwin(file.id),
    {
      enabled: !!file?.id,
      onSuccess: (data) => {
        setLoading(false);
        if (data?.materials?.length > 0) {
          setSelectedMaterial(data.materials[0]);
        }
      }
    }
  );

  // Fetch file status
  const { data: fileStatus } = useQuery(
    ['fileStatus', file?.id],
    () => fileService.getFileStatus(file.id),
    {
      enabled: !!file?.id,
      refetchInterval: 2000, // Poll every 2 seconds
    }
  );

  const handleModelLoad = (scene) => {
    // Calculate bounding box
    const box = new THREE.Box3().setFromObject(scene);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    
    setModelInfo({
      vertexCount: scene.children.reduce((count, child) => {
        if (child.geometry) {
          return count + (child.geometry.attributes.position?.count || 0);
        }
        return count;
      }, 0),
      boundingBox: {
        width: size.x,
        height: size.y,
        depth: size.z
      },
      center: center
    });
  };

  const handleResetView = () => {
    if (controlsRef.current) {
      controlsRef.current.reset();
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.1, 2));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.1, 0.5));
  };

  const handleDownload = () => {
    if (file?.processed_path) {
      const link = document.createElement('a');
      link.href = `/api/download/${file.id}`;
      link.download = `${file.filename}_processed.gltf`;
      link.click();
    }
  };

  if (digitalTwinLoading || loading) {
    return (
      <ViewerContainer>
        <LoadingOverlay>
          <LoadingSpinner />
        </LoadingOverlay>
      </ViewerContainer>
    );
  }

  return (
    <ViewerContainer>
      <Sidebar>
        <SidebarHeader>
          <FileInfo>
            <FileName>{file?.filename}</FileName>
            <FileMeta>
              {file?.file_type?.toUpperCase()} • {file?.file_size ? `${(file.file_size / 1024 / 1024).toFixed(2)} MB` : 'Unknown size'}
              <StatusBadge status={fileStatus?.status || 'unknown'}>
                {fileStatus?.status || 'Unknown'}
              </StatusBadge>
            </FileMeta>
          </FileInfo>
        </SidebarHeader>
        
        <SidebarContent>
          <Section>
            <SectionTitle>View Controls</SectionTitle>
            <ControlGroup>
              <ControlButton onClick={handleResetView}>
                <RotateCcw size={16} />
                Reset View
              </ControlButton>
              <ControlButton onClick={() => setAnimationPlaying(!animationPlaying)}>
                {animationPlaying ? <Pause size={16} /> : <Play size={16} />}
                {animationPlaying ? 'Pause' : 'Play'} Animation
              </ControlButton>
            </ControlGroup>
          </Section>
          
          <Section>
            <SectionTitle>Rotation Speed</SectionTitle>
            <SliderLabel>
              <span>Slow</span>
              <span>Fast</span>
            </SliderLabel>
            <Slider
              type="range"
              min="0"
              max="0.05"
              step="0.005"
              value={rotationSpeed}
              onChange={(e) => setRotationSpeed(parseFloat(e.target.value))}
            />
          </Section>
          
          <Section>
            <SectionTitle>Materials</SectionTitle>
            <MaterialList>
              {digitalTwinData?.materials?.map((material, index) => (
                <MaterialItem
                  key={material.id || index}
                  className={selectedMaterial?.id === material.id ? 'selected' : ''}
                  onClick={() => setSelectedMaterial(material)}
                >
                  <MaterialColor color={material.color} />
                  <span>{material.name}</span>
                </MaterialItem>
              ))}
            </MaterialList>
          </Section>
          
          <Section>
            <SectionTitle>Actions</SectionTitle>
            <ControlGroup>
              <ControlButton onClick={handleDownload}>
                <Download size={16} />
                Download Model
              </ControlButton>
              <ControlButton>
                <Share size={16} />
                Share
              </ControlButton>
            </ControlGroup>
          </Section>
        </SidebarContent>
      </Sidebar>
      
      <ViewerArea>
        <Canvas
          camera={{ position: [5, 5, 5], fov: 50 }}
          style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
        >
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <Environment preset="sunset" />
          
          <OrbitControls
            ref={controlsRef}
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            autoRotate={animationPlaying}
            autoRotateSpeed={rotationSpeed * 100}
          />
          
          <group scale={[zoom, zoom, zoom]}>
            {file?.processed_path ? (
              <Model 
                url={`/api/download/${file.id}`}
                onLoad={handleModelLoad}
              />
            ) : (
              <PlaceholderModel />
            )}
          </group>
        </Canvas>
        
        <ViewerControls>
          <ControlButtonSmall onClick={handleZoomIn}>
            <ZoomIn size={20} />
          </ControlButtonSmall>
          <ControlButtonSmall onClick={handleZoomOut}>
            <ZoomOut size={20} />
          </ControlButtonSmall>
          <ControlButtonSmall onClick={handleResetView}>
            <RotateCcw size={20} />
          </ControlButtonSmall>
        </ViewerControls>
        
        {modelInfo && (
          <ViewerInfo>
            <div>Vertices: {modelInfo.vertexCount.toLocaleString()}</div>
            <div>Size: {modelInfo.boundingBox.width.toFixed(2)} × {modelInfo.boundingBox.height.toFixed(2)} × {modelInfo.boundingBox.depth.toFixed(2)}</div>
          </ViewerInfo>
        )}
      </ViewerArea>
    </ViewerContainer>
  );
};

export default DigitalTwinViewer;