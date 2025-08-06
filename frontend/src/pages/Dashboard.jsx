import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();



  const handleBestOfStats = () => {
    navigate('/best-of');
  };

  const handleUmpireAccuracy = () => {
    navigate('/umpire-accuracy');
  };

  const handleAdminPanel = () => {
    navigate('/admin');
  };

  const handleRosterManagement = () => {
    navigate('/roster');
  };

  const handleDevelopment = () => {
    navigate('/development');
  };

  const isAdmin = user?.role === 'admin';

  return (
    <div className="dashboard-container">
      <div className="dashboard-main">
        <div className="dashboard-header">
          <h1>Analytics Dashboard</h1>
          <p>Upload your CSV data and generate comprehensive reports</p>
        </div>

        <div className="dashboard-cards">
          <div className="dashboard-card">
            <div className="card-icon">📅</div>
            <h3>Game Calendar</h3>
            <p>View your season schedule with wins, losses, and game results</p>
            <button onClick={() => navigate('/calendar')} className="card-button">
              View Calendar
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">📊</div>
            <h3>CSV Data Management</h3>
            <p>Upload, manage, and analyze your team's Trackman CSV files</p>
            <button onClick={() => navigate('/csv-management')} className="card-button">
              Manage CSV Files
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🏆</div>
            <h3>Best of Stats</h3>
            <p>View top performers across different metrics and time periods</p>
            <button onClick={handleBestOfStats} className="card-button">
              View Best of Stats
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">⚖️</div>
            <h3>Umpire Accuracy</h3>
            <p>Analyze umpire performance and call accuracy</p>
            <button onClick={handleUmpireAccuracy} className="card-button">
              Analyze Umpire Accuracy
            </button>
          </div>

          {isAdmin && (
            <div className="dashboard-card">
              <div className="card-icon">👑</div>
              <h3>Admin Panel</h3>
              <p>Manage users and system settings</p>
              <button onClick={handleAdminPanel} className="card-button admin-button">
                Access Admin Panel
              </button>
            </div>
          )}

          <div className="dashboard-card">
            <div className="card-icon">👥</div>
            <h3>Team Roster</h3>
            <p>View and manage your team's roster of players</p>
            <button onClick={handleRosterManagement} className="card-button">
              Manage Roster
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">📈</div>
            <h3>Player Development</h3>
            <p>Identify improvement areas and get actionable training recommendations</p>
            <button onClick={handleDevelopment} className="card-button">
              View Development
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">🎯</div>
            <h3>Metric Targets</h3>
            <p>Set custom target values for performance metrics to match your team's goals</p>
            <button onClick={() => navigate('/metric-targets')} className="card-button">
              Manage Targets
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">📱</div>
            <h3>Social Media Generator</h3>
            <p>Create a shareable stat graphic for your team or player</p>
            <button onClick={() => navigate('/social-media-generator')} className="card-button">
              Create Social Post
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">📈</div>
            <h3>View Reports</h3>
            <p>Access previously generated reports and analytics</p>
            <button className="card-button" disabled>
              Coming Soon
            </button>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">⚙️</div>
            <h3>Settings</h3>
            <p>Manage your account and preferences</p>
            <button className="card-button" disabled>
              Coming Soon
            </button>
          </div>
        </div>

        <div className="dashboard-info">
          <h3>Getting Started</h3>
          <ol>
            <li>Upload your Trackman CSV files using "CSV Data Management"</li>
            <li>View your team's roster and player information in "Team Roster"</li>
            <li>Explore "Best of Stats" to see top performers across all metrics</li>
            <li>Generate game reports and player profiles for detailed analysis</li>
            <li>Create social media graphics to showcase player achievements</li>
            <li>Use "Player Development" to identify improvement areas and training recommendations</li>
            <li>Set custom metric targets in "Metric Targets" to match your team's goals</li>
            {isAdmin && <li>Access the Admin Panel to manage users and system settings</li>}
          </ol>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 