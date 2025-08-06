import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config';
import './AdminPanel.css';

const AdminPanel = () => {
  const [users, setUsers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showCreateTeamForm, setShowCreateTeamForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'user',
    team_id: ''
  });
  const [teamFormData, setTeamFormData] = useState({
    name: '',
    organization: ''
  });
  const { token, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
    fetchTeams();
    fetchStats();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.ADMIN_USERS, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Failed to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeams = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.ADMIN_TEAMS, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch teams');
      }

      const data = await response.json();
      setTeams(data);
    } catch (error) {
      console.error('Error fetching teams:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.ADMIN_STATS, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch stats');
      }

      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(API_ENDPOINTS.ADMIN_USERS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create user');
      }

      setShowCreateForm(false);
      setFormData({ name: '', email: '', password: '', role: 'user', team_id: '' });
      fetchUsers();
      fetchTeams();
      fetchStats();
    } catch (error) {
      console.error('Error creating user:', error);
      setError(error.message);
    }
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();
    try {
      const updateData = {};
      if (formData.name) updateData.name = formData.name;
      if (formData.email) updateData.email = formData.email;
      if (formData.password) updateData.password = formData.password;
      if (formData.role) updateData.role = formData.role;
      if (formData.team_id !== undefined) updateData.team_id = formData.team_id || null;

      const response = await fetch(`${API_ENDPOINTS.ADMIN_USERS}/${editingUser.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(updateData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update user');
      }

      setEditingUser(null);
      setFormData({ name: '', email: '', password: '', role: 'user', team_id: '' });
      fetchUsers();
      fetchTeams();
      fetchStats();
    } catch (error) {
      console.error('Error updating user:', error);
      setError(error.message);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      const response = await fetch(`${API_ENDPOINTS.ADMIN_USERS}/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete user');
      }

      fetchUsers();
      fetchTeams();
      fetchStats();
    } catch (error) {
      console.error('Error deleting user:', error);
      setError(error.message);
    }
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setFormData({
      name: user.name,
      email: user.email,
      password: '',
      role: user.role,
      team_id: user.team_id || ''
    });
  };

  const handleCancelEdit = () => {
    setEditingUser(null);
    setFormData({ name: '', email: '', password: '', role: 'user', team_id: '' });
  };

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(API_ENDPOINTS.ADMIN_TEAMS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(teamFormData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create team');
      }

      setShowCreateTeamForm(false);
      setTeamFormData({ name: '', organization: '' });
      fetchTeams();
    } catch (error) {
      console.error('Error creating team:', error);
      setError(error.message);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  const StatCard = ({ title, value, color = 'primary' }) => (
    <div className={`stat-card ${color}`}>
      <h3>{title}</h3>
      <div className="stat-value">{value}</div>
    </div>
  );

  if (loading) {
    return (
      <div className="admin-container">
        <div className="admin-card">
          <div className="loading">Loading admin panel...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <div className="admin-card">
        <div className="admin-header">
          <h1>👑 Admin Panel</h1>
          <p>Manage users and system settings</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        {stats && (
          <div className="stats-section">
            <h2>📊 User Statistics</h2>
            <div className="stats-grid">
              <StatCard title="Total Users" value={stats.total_users} color="primary" />
              <StatCard title="Admins" value={stats.admin_users} color="danger" />
              <StatCard title="Coaches" value={stats.coach_users} color="warning" />
              <StatCard title="Regular Users" value={stats.regular_users} color="success" />
            </div>
          </div>
        )}

        <div className="teams-section">
          <div className="section-header">
            <h2>🏟️ Team Management</h2>
            <button
              onClick={() => setShowCreateTeamForm(true)}
              className="create-button"
            >
              + Add New Team
            </button>
          </div>

          <div className="teams-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Team Name</th>
                  <th>Organization</th>
                  <th>Users</th>
                </tr>
              </thead>
              <tbody>
                {teams.map((team) => (
                  <tr key={team.id}>
                    <td>{team.id}</td>
                    <td>{team.name}</td>
                    <td>{team.organization || '-'}</td>
                    <td>{team.user_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="users-section">
          <div className="section-header">
            <h2>👥 User Management</h2>
            <button
              onClick={() => setShowCreateForm(true)}
              className="create-button"
            >
              + Add New User
            </button>
          </div>

          {showCreateTeamForm && (
            <div className="form-overlay">
              <div className="form-modal">
                <h3>Create New Team</h3>
                <form onSubmit={handleCreateTeam}>
                  <div className="form-group">
                    <label>Team Name:</label>
                    <input
                      type="text"
                      value={teamFormData.name}
                      onChange={(e) => setTeamFormData({...teamFormData, name: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Organization:</label>
                    <input
                      type="text"
                      value={teamFormData.organization}
                      onChange={(e) => setTeamFormData({...teamFormData, organization: e.target.value})}
                    />
                  </div>
                  <div className="form-actions">
                    <button type="submit" className="submit-button">Create Team</button>
                    <button
                      type="button"
                      onClick={() => setShowCreateTeamForm(false)}
                      className="cancel-button"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {showCreateForm && (
            <div className="form-overlay">
              <div className="form-modal">
                <h3>Create New User</h3>
                <form onSubmit={handleCreateUser}>
                  <div className="form-group">
                    <label>Name:</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Email:</label>
                    <input
                      type="text"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Password:</label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Role:</label>
                    <select
                      value={formData.role}
                      onChange={(e) => setFormData({...formData, role: e.target.value})}
                    >
                      <option value="user">User</option>
                      <option value="coach">Coach</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Team:</label>
                    <select
                      value={formData.team_id}
                      onChange={(e) => setFormData({...formData, team_id: e.target.value ? parseInt(e.target.value) : ''})}
                    >
                      <option value="">No Team</option>
                      {teams.map((team) => (
                        <option key={team.id} value={team.id}>
                          {team.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-actions">
                    <button type="submit" className="submit-button">Create User</button>
                    <button
                      type="button"
                      onClick={() => setShowCreateForm(false)}
                      className="cancel-button"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {editingUser && (
            <div className="form-overlay">
              <div className="form-modal">
                <h3>Edit User: {editingUser.email}</h3>
                <form onSubmit={handleUpdateUser}>
                  <div className="form-group">
                    <label>Name:</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Email:</label>
                    <input
                      type="text"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Password (leave blank to keep current):</label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                    />
                  </div>
                  <div className="form-group">
                    <label>Role:</label>
                    <select
                      value={formData.role}
                      onChange={(e) => setFormData({...formData, role: e.target.value})}
                    >
                      <option value="user">User</option>
                      <option value="coach">Coach</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Team:</label>
                    <select
                      value={formData.team_id}
                      onChange={(e) => setFormData({...formData, team_id: e.target.value ? parseInt(e.target.value) : ''})}
                    >
                      <option value="">No Team</option>
                      {teams.map((team) => (
                        <option key={team.id} value={team.id}>
                          {team.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-actions">
                    <button type="submit" className="submit-button">Update User</button>
                    <button
                      type="button"
                      onClick={handleCancelEdit}
                      className="cancel-button"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          <div className="users-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Team</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((rowUser) => (
                  <tr key={rowUser.id}>
                    <td>{rowUser.id}</td>
                    <td>{rowUser.name}</td>
                    <td>{rowUser.email}</td>
                    <td>
                      <span className={`role-badge ${rowUser.role}`}>
                        {rowUser.role}
                      </span>
                    </td>
                    <td>{rowUser.team_name || '-'}</td>
                    <td>
                      <div className="action-buttons">
                        <button
                          onClick={() => handleEditUser(rowUser)}
                          className="edit-button"
                          disabled={rowUser.id === user?.id}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteUser(rowUser.id)}
                          className="delete-button"
                          disabled={rowUser.id === user?.id}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="admin-actions">
          <button onClick={handleBackToDashboard} className="secondary-button">
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel; 