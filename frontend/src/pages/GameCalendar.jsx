import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import './GameCalendar.css';

const GameCalendar = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchGames();
  }, []);

  const fetchGames = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.LIST_CSV_FILES, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        mode: 'cors',
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch games');
      }

      const data = await response.json();
      const gameData = data.map(file => ({
        id: file.id,
        date: file.game_date || file.uploaded_at.split('T')[0],
        opponent: file.opponent || 'Unknown',
        result: file.game_result || 'N/A',
        filename: file.original_filename,
        isWin: file.game_result?.toLowerCase().includes('w') || false,
        isLoss: file.game_result?.toLowerCase().includes('l') || false,
      }));

      setGames(gameData);
    } catch (error) {
      console.error('Error fetching games:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = date => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    return { daysInMonth, startingDayOfWeek };
  };

  const getGamesForDate = date => {
    const dateStr = date.toISOString().split('T')[0];
    return games.filter(game => game.date === dateStr);
  };

  const formatDate = dateString => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getMonthName = date => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const renderCalendar = () => {
    const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentMonth);
    const days = [];

    // Empty placeholders before first day
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty"></div>);
    }

    // Actual days
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
      const gamesForDay = getGamesForDate(date);

      days.push(
        <div key={day} className="calendar-day">
          <div className="day-number">{day}</div>
          {gamesForDay.map(game => (
            <div
              key={game.id}
              className={`game-indicator ${game.isWin ? 'win' : game.isLoss ? 'loss' : 'neutral'}`}
              title={`${game.opponent} - ${game.result}`}
              onClick={() => navigate(`/game-report/${game.id}`)}
            >
              {game.opponent}
            </div>
          ))}
        </div>
      );
    }

    return days;
  };

  const getSeasonStats = () => {
    const wins = games.filter(game => game.isWin).length;
    const losses = games.filter(game => game.isLoss).length;
    const total = wins + losses;
    const winPercentage = total > 0 ? ((wins / total) * 100).toFixed(1) : 0;
    return { wins, losses, total, winPercentage };
  };

  if (loading) return <div className="calendar-container">Loading calendar...</div>;
  if (error) return <div className="calendar-container">Error: {error}</div>;

  const stats = getSeasonStats();

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <h2>Game Calendar</h2>
        <div className="season-stats">
          <div className="stat">
            Wins: <span className="win">{stats.wins}</span>
          </div>
          <div className="stat">
            Losses: <span className="loss">{stats.losses}</span>
          </div>
          <div className="stat">Win %: {stats.winPercentage}%</div>
        </div>
      </div>

      <div className="calendar-navigation">
        <button onClick={previousMonth}>&lt; Previous</button>
        <h3>{getMonthName(currentMonth)}</h3>
        <button onClick={nextMonth}>Next &gt;</button>
      </div>

      <div className="calendar-legend">
        <div className="legend-item"><span className="legend-color win"></span> Win</div>
        <div className="legend-item"><span className="legend-color loss"></span> Loss</div>
        <div className="legend-item"><span className="legend-color neutral"></span> No Result</div>
      </div>

      <div className="calendar-weekdays">
        <div>Sun</div>
        <div>Mon</div>
        <div>Tue</div>
        <div>Wed</div>
        <div>Thu</div>
        <div>Fri</div>
        <div>Sat</div>
      </div>

      <div className="calendar-days">{renderCalendar()}</div>

      <div className="recent-games">
        <h3>Recent Games</h3>
        {games.slice(0, 5).map(game => (
          <div
            key={game.id}
            className={`game-item ${game.isWin ? 'win' : game.isLoss ? 'loss' : 'neutral'}`}
            onClick={() => navigate(`/game-report/${game.id}`)}
          >
            <span className="game-date">{formatDate(game.date)}</span>
            <span className="game-opponent">{game.opponent}</span>
            <span className="game-result">{game.result}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GameCalendar;
