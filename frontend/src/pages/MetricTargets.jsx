import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config';
import './MetricTargets.css';

const MetricTargets = () => {
    const { user, token } = useAuth();
    const [targets, setTargets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editingTarget, setEditingTarget] = useState(null);
    const [showForm, setShowForm] = useState(false);

    // Available metrics with their display names and descriptions
    const availableMetrics = {
        'chase_rate': {
            name: 'Chase Rate',
            description: 'Percentage of swings on pitches outside the strike zone',
            unit: '%',
            defaultTarget: 22.0,
            lowerIsBetter: true
        },
        'strike_percentage': {
            name: 'Strike Percentage',
            description: 'Percentage of pitches that are strikes',
            unit: '%',
            defaultTarget: 70.0,
            lowerIsBetter: false
        },
        'exit_velocity': {
            name: 'Exit Velocity',
            description: 'Average exit velocity of batted balls',
            unit: 'mph',
            defaultTarget: 88.0,
            lowerIsBetter: false
        },
        'avg_spin_rate': {
            name: 'Average Spin Rate',
            description: 'Average spin rate of pitches',
            unit: 'rpm',
            defaultTarget: 2300,
            lowerIsBetter: false
        },
        'first_pitch_strike_percentage': {
            name: 'First Pitch Strike Percentage',
            description: 'Percentage of first pitches that are strikes',
            unit: '%',
            defaultTarget: 65.0,
            lowerIsBetter: false
        }
    };

    useEffect(() => {
        fetchTargets();
    }, []);

    const fetchTargets = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_BASE_URL}/csv/metric-targets`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch targets');
            }

            const data = await response.json();
            setTargets(data.targets || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const saveTarget = async (formData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/csv/metric-targets`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to save target');
            }

            await fetchTargets();
            setShowForm(false);
            setEditingTarget(null);
        } catch (err) {
            setError(err.message);
        }
    };

    const deleteTarget = async (targetId) => {
        if (!window.confirm('Are you sure you want to delete this target?')) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/csv/metric-targets/${targetId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to delete target');
            }

            await fetchTargets();
        } catch (err) {
            setError(err.message);
        }
    };

    const resetDefaults = async () => {
        if (!window.confirm('Are you sure you want to reset all targets to defaults? This will overwrite any custom targets.')) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/csv/metric-targets/reset-defaults`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to reset targets');
            }

            await fetchTargets();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('metric_name', editingTarget.metric_name);
        formData.append('target_value', editingTarget.target_value);
        formData.append('priority', editingTarget.priority);
        formData.append('description', editingTarget.description);
        formData.append('lower_is_better', editingTarget.lower_is_better);
        saveTarget(formData);
    };

    const editTarget = (target) => {
        setEditingTarget(target);
        setShowForm(true);
    };

    const addNewTarget = () => {
        setEditingTarget({
            metric_name: '',
            target_value: '',
            priority: 'Medium',
            description: '',
            lower_is_better: false
        });
        setShowForm(true);
    };

    if (loading) {
        return <div className="metric-targets-container">Loading...</div>;
    }

    return (
        <div className="metric-targets-container">
            <div className="metric-targets-header">
                <h1>Team Metric Targets</h1>
                <p>Set custom target values for your team's performance metrics. These targets will be used in the Player Development analysis.</p>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                    <button onClick={() => setError(null)}>×</button>
                </div>
            )}

            <div className="metric-targets-actions">
                <button className="btn-primary" onClick={addNewTarget}>
                    Add New Target
                </button>
                <button className="btn-secondary" onClick={resetDefaults}>
                    Reset to Defaults
                </button>
            </div>

            {showForm && (
                <div className="target-form-overlay">
                    <div className="target-form">
                        <h2>{editingTarget.id ? 'Edit Target' : 'Add New Target'}</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>Metric:</label>
                                <select
                                    value={editingTarget.metric_name}
                                    onChange={(e) => setEditingTarget({
                                        ...editingTarget,
                                        metric_name: e.target.value,
                                        target_value: availableMetrics[e.target.value]?.defaultTarget || '',
                                        lower_is_better: availableMetrics[e.target.value]?.lowerIsBetter || false
                                    })}
                                    required
                                >
                                    <option value="">Select a metric</option>
                                    {Object.entries(availableMetrics).map(([key, metric]) => (
                                        <option key={key} value={key}>
                                            {metric.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Target Value:</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={editingTarget.target_value}
                                    onChange={(e) => setEditingTarget({
                                        ...editingTarget,
                                        target_value: parseFloat(e.target.value)
                                    })}
                                    required
                                />
                                {editingTarget.metric_name && (
                                    <span className="unit">
                                        {availableMetrics[editingTarget.metric_name]?.unit}
                                    </span>
                                )}
                            </div>

                            <div className="form-group">
                                <label>Priority:</label>
                                <select
                                    value={editingTarget.priority}
                                    onChange={(e) => setEditingTarget({
                                        ...editingTarget,
                                        priority: e.target.value
                                    })}
                                >
                                    <option value="High">High</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Low">Low</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>Description:</label>
                                <textarea
                                    value={editingTarget.description}
                                    onChange={(e) => setEditingTarget({
                                        ...editingTarget,
                                        description: e.target.value
                                    })}
                                    rows="3"
                                />
                            </div>

                            <div className="form-group checkbox-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={editingTarget.lower_is_better}
                                        onChange={(e) => setEditingTarget({
                                            ...editingTarget,
                                            lower_is_better: e.target.checked
                                        })}
                                    />
                                    Lower values are better (e.g., chase rate)
                                </label>
                            </div>

                            <div className="form-actions">
                                <button type="submit" className="btn-primary">
                                    {editingTarget.id ? 'Update Target' : 'Add Target'}
                                </button>
                                <button
                                    type="button"
                                    className="btn-secondary"
                                    onClick={() => {
                                        setShowForm(false);
                                        setEditingTarget(null);
                                    }}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="targets-grid">
                {targets.length === 0 ? (
                    <div className="no-targets">
                        <p>No custom targets set. Use the "Add New Target" button to create custom targets, or "Reset to Defaults" to use standard targets.</p>
                    </div>
                ) : (
                    targets.map((target) => (
                        <div key={target.id} className="target-card">
                            <div className="target-header">
                                <h3>{availableMetrics[target.metric_name]?.name || target.metric_name}</h3>
                                <span className={`priority-badge ${target.priority.toLowerCase()}`}>
                                    {target.priority}
                                </span>
                            </div>
                            
                            <div className="target-value">
                                <span className="value">{target.target_value}</span>
                                <span className="unit">{availableMetrics[target.metric_name]?.unit}</span>
                            </div>
                            
                            {target.description && (
                                <p className="target-description">{target.description}</p>
                            )}
                            
                            <div className="target-meta">
                                <span className={`better-indicator ${target.lower_is_better ? 'lower' : 'higher'}`}>
                                    {target.lower_is_better ? 'Lower is better' : 'Higher is better'}
                                </span>
                            </div>
                            
                            <div className="target-actions">
                                <button
                                    className="btn-edit"
                                    onClick={() => editTarget(target)}
                                >
                                    Edit
                                </button>
                                <button
                                    className="btn-delete"
                                    onClick={() => deleteTarget(target.id)}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default MetricTargets; 