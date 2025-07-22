// API Configuration
export const API_BASE_URL = 'https://api.moundvision.com';

// API Endpoints
export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  UPLOAD_CSV: `${API_BASE_URL}/api/csv/upload`,
  TEAM_PITCHERS: `${API_BASE_URL}/api/csv/team_pitchers`,
  METRICS_SUMMARY: `${API_BASE_URL}/api/metrics/summary`,
  METRICS_PITCHES: `${API_BASE_URL}/api/metrics/pitches`,
  METRICS_DOWNLOAD_PDF: `${API_BASE_URL}/api/metrics/download_pdf`,
  METRICS_BEST_OF: `${API_BASE_URL}/api/metrics/best-of`,
  METRICS_UMPIRE_ACCURACY: `${API_BASE_URL}/api/metrics/umpire-accuracy`,
  METRICS_UMPIRE_ACCURACY_PLOT: `${API_BASE_URL}/api/metrics/umpire-accuracy-plot`,
  ADMIN_USERS: `${API_BASE_URL}/api/admin/users`,
  ADMIN_STATS: `${API_BASE_URL}/api/admin/stats`,
  SOCIAL_GENERATE_GRAPHIC: `${API_BASE_URL}/api/social/generate-graphic`,
};

// Fallback URL for development
export const FALLBACK_API_URL = 'https://api.moundvision.com';

// For development, you can also use:
// export const FALLBACK_API_URL = 'http://localhost:8000'; 