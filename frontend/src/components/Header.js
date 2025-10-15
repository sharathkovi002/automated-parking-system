import React from 'react';
import styled from 'styled-components';
import { Upload, Home, Files, Settings, ArrowLeft } from 'lucide-react';

const HeaderContainer = styled.header`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
`;

const HeaderContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #333;
`;

const LogoIcon = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const NavButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  background: ${props => props.active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent'};
  color: ${props => props.active ? 'white' : '#666'};
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: ${props => props.active ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'rgba(102, 126, 234, 0.1)'};
    color: ${props => props.active ? 'white' : '#333'};
  }
`;

const BackButton = styled.button`
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

const Header = ({ currentView, onViewChange, onBack }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'files', label: 'Files', icon: Files },
  ];

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo>
          <LogoIcon>DT</LogoIcon>
          Digital Twin Platform
        </Logo>
        
        <Nav>
          {onBack && (
            <BackButton onClick={onBack}>
              <ArrowLeft size={20} />
              Back
            </BackButton>
          )}
          
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <NavButton
                key={item.id}
                active={currentView === item.id}
                onClick={() => onViewChange(item.id)}
              >
                <Icon size={20} />
                {item.label}
              </NavButton>
            );
          })}
        </Nav>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header;