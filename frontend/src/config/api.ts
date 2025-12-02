export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8081",
  ENDPOINTS: {
    HEALTH: "/health",
    FETCH_DATA: "/api/data/fetch",
    GET_ALL_DATA: "/api/data",
    GET_DATA_BY_ID: (id: string) => `/api/data/${id}`,
  },
  TIMEOUT: 30000,
} as const;
