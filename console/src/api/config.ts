declare const BASE_URL: string;
declare const TOKEN: string;

const TOKEN_STORAGE_KEY = "copaw_auth_token";

/**
 * Get the full API URL with /api prefix
 * @param path - API path (e.g., "/models", "/skills")
 * @returns Full API URL (e.g., "http://localhost:8088/api/models" or "/api/models")
 */
export function getApiUrl(path: string): string {
  const base = BASE_URL || "";
  const apiPrefix = "/api";
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${base}${apiPrefix}${normalizedPath}`;
}

/**
 * Get the API token
 * @returns API token string or empty string
 */
export function getApiToken(): string {
  // If TOKEN is defined at build time, use it (for backward compatibility)
  if (typeof TOKEN !== "undefined" && TOKEN) {
    return TOKEN;
  }
  // Otherwise, get from localStorage
  return localStorage.getItem(TOKEN_STORAGE_KEY) || "";
}

/**
 * Set the API token
 * @param token - API token string or null to clear
 */
export function setApiToken(token: string | null): void {
  if (token === null) {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  } else {
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
  }
}

/**
 * Check if user is authenticated
 * @returns true if user has a token
 */
export function isAuthenticated(): boolean {
  return getApiToken() !== "";
}

