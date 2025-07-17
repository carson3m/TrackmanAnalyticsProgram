import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UploadCSV from './pages/UploadCSV';
import SelectTeam from './pages/SelectTeam';
import SelectPitcher from './pages/SelectPitcher';
import ViewReport from './pages/ViewReport';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';
import logo from './assets/moundvision_logo.png';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-header">
          <div className="logo-container">
            <img src={logo} alt="MoundVision Analytics Logo" className="logo-img" />
            <div>
              <div className="brand-title">MOUNDVISION ANALYTICS</div>
              <div className="tagline">Sharper vision. Better results.</div>
            </div>
          </div>
        </div>
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<Login />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/upload" 
              element={
                <ProtectedRoute>
                  <UploadCSV />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/select-team" 
              element={
                <ProtectedRoute>
                  <SelectTeam />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/select-pitcher" 
              element={
                <ProtectedRoute>
                  <SelectPitcher />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/report" 
              element={
                <ProtectedRoute>
                  <ViewReport />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
