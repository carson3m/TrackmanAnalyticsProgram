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
import RosterManagement from './pages/RosterManagement';
import CSVManagement from './pages/CSVManagement';
import GameCalendar from './pages/GameCalendar';
import GameReport from './pages/GameReport';
import PlayerProfile from './pages/PlayerProfile';
import Development from './pages/Development';
import MetricTargets from './pages/MetricTargets';
import LandingPage from './pages/LandingPage';
import AboutUs from './pages/AboutUs';
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

// Authenticated App Layout
const AuthenticatedApp = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="authenticated-app">
      <div className="app-header">
        <div className="logo-container">
          <img src={logo} alt="MoundVision Analytics Logo" className="logo-img" />
          <div>
            <div className="brand-title">MOUNDVISION ANALYTICS</div>
            <div className="tagline">Sharper vision. Better results.</div>
          </div>
        </div>
        <div className="user-section">
          <span className="welcome-text">Welcome, {user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
      <div className="main-content">
        {children}
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/about" element={<AboutUs />} />
          <Route path="/login" element={<Login />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <AuthenticatedApp>
                  <Dashboard />
                </AuthenticatedApp>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/upload" 
            element={
              <ProtectedRoute>
                <AuthenticatedApp>
                  <UploadCSV />
                </AuthenticatedApp>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/select-team" 
            element={
              <ProtectedRoute>
                <AuthenticatedApp>
                  <SelectTeam />
                </AuthenticatedApp>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/select-pitcher" 
            element={
              <ProtectedRoute>
                <AuthenticatedApp>
                  <SelectPitcher />
                </AuthenticatedApp>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/report" 
            element={
              <ProtectedRoute>
                <AuthenticatedApp>
                  <ViewReport />
                </AuthenticatedApp>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/best-of" 
            element={
              <ProtectedRoute>
                <AuthenticatedApp>
                  <BestOfStats />
                </AuthenticatedApp>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/umpire-accuracy" 
            element={
              <ProtectedRoute>
                <AuthenticatedApp>
                  <UmpireAccuracy />
                </AuthenticatedApp>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/social-media-generator" 
            element={
              <ProtectedRoute>
                <AuthenticatedApp>
                  <SocialMediaGenerator />
                </AuthenticatedApp>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/roster" 
            element={
              <ProtectedRoute>
                <AuthenticatedApp>
                  <RosterManagement />
                </AuthenticatedApp>
              </ProtectedRoute>
            } 
          />
                            <Route 
                    path="/csv-management" 
                    element={
                      <ProtectedRoute>
                        <AuthenticatedApp>
                          <CSVManagement />
                        </AuthenticatedApp>
                      </ProtectedRoute>
                    } 
                  />
                                      <Route 
                      path="/calendar" 
                      element={
                        <ProtectedRoute>
                          <AuthenticatedApp>
                            <GameCalendar />
                          </AuthenticatedApp>
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/game-report/:fileId" 
                      element={
                        <ProtectedRoute>
                          <AuthenticatedApp>
                            <GameReport />
                          </AuthenticatedApp>
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/game-report/:fileId/pitcher/:pitcherName" 
                      element={
                        <ProtectedRoute>
                          <AuthenticatedApp>
                            <GameReport />
                          </AuthenticatedApp>
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/player-profile/:playerName/:playerType" 
                      element={
                        <ProtectedRoute>
                          <AuthenticatedApp>
                            <PlayerProfile />
                          </AuthenticatedApp>
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/development" 
                      element={
                        <ProtectedRoute>
                          <AuthenticatedApp>
                            <Development />
                          </AuthenticatedApp>
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/metric-targets" 
                      element={
                        <ProtectedRoute>
                          <AuthenticatedApp>
                            <MetricTargets />
                          </AuthenticatedApp>
                        </ProtectedRoute>
                      } 
                    />
          <Route 
            path="/admin" 
            element={
              <AdminRoute>
                <AuthenticatedApp>
                  <AdminPanel />
                </AuthenticatedApp>
              </AdminRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
