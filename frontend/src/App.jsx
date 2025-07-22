import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UploadCSV from './pages/UploadCSV';
import SelectTeam from './pages/SelectTeam';
import SelectPitcher from './pages/SelectPitcher';
import ViewReport from './pages/ViewReport';
import BestOfStats from './pages/BestOfStats';
import UmpireAccuracy from './pages/UmpireAccuracy';
import AdminPanel from './pages/AdminPanel';
import SocialMediaGenerator from './pages/SocialMediaGenerator';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';
import logo from './assets/moundvision_logo.png';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Admin Route component
const AdminRoute = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  if (user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
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
            <Route 
              path="/best-of" 
              element={
                <ProtectedRoute>
                  <BestOfStats />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/umpire-accuracy" 
              element={
                <ProtectedRoute>
                  <UmpireAccuracy />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/social-media-generator" 
              element={
                <ProtectedRoute>
                  <SocialMediaGenerator />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin" 
              element={
                <AdminRoute>
                  <AdminPanel />
                </AdminRoute>
              } 
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
