// API Configuration
export const API_BASE_URL = "https://api.moundvision.com/api";

// API Endpoints
export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/auth/login`,
  UPLOAD_CSV: `${API_BASE_URL}/csv/upload`,
  UPLOAD_CSV_PERSISTENT: `${API_BASE_URL}/csv/upload-persistent`,
  LIST_CSV_FILES: `${API_BASE_URL}/csv/files`,
  GET_CSV_FILE: `${API_BASE_URL}/csv/files`,
  DELETE_CSV_FILE: `${API_BASE_URL}/csv/files`,
              UPDATE_CSV_METADATA: `${API_BASE_URL}/csv/files`,
            TEAM_PITCHERS: `${API_BASE_URL}/csv/team_pitchers`,
            MY_TEAM_PITCHERS: `${API_BASE_URL}/csv/my_team_pitchers`,
            FILE_TEAMS: `${API_BASE_URL}/csv/file`,
            FILE_PITCHERS: `${API_BASE_URL}/csv/file`,
            ROSTER: `${API_BASE_URL}/csv/roster`,
            TEAM_ROSTER: `${API_BASE_URL}/csv/roster`,
  GAME_REPORT: `${API_BASE_URL}/csv/game-report`,
  PLAYER_PROFILE: `${API_BASE_URL}/csv/player-profile`,
  METRICS_SUMMARY: `${API_BASE_URL}/metrics/summary`,
  METRICS_PITCHES: `${API_BASE_URL}/metrics/pitches`,
  METRICS_DOWNLOAD_PDF: `${API_BASE_URL}/metrics/download_pdf`,
  METRICS_BASE: `${API_BASE_URL}/metrics`,
  METRICS_BEST_OF: `${API_BASE_URL}/metrics/best-of`,
  METRICS_UMPIRE_ACCURACY: `${API_BASE_URL}/metrics/umpire-accuracy`,
  METRICS_UMPIRE_ACCURACY_PLOT: `${API_BASE_URL}/metrics/umpire-accuracy-plot`,
  DEVELOPMENT_ANALYSIS: `${API_BASE_URL}/csv/development/analysis`,
  ADMIN_USERS: `${API_BASE_URL}/admin/users`,
  ADMIN_STATS: `${API_BASE_URL}/admin/stats`,
  ADMIN_TEAMS: `${API_BASE_URL}/admin/teams`,
  ADMIN_ASSIGN_TEAM: `${API_BASE_URL}/admin/users`,
  SOCIAL_GENERATE_GRAPHIC: `${API_BASE_URL}/social/generate-graphic`,
};

// Fallback URL for development
export const FALLBACK_API_URL = API_BASE_URL; 