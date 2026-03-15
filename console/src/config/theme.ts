/**
 * Theme types and configuration
 */

export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeConfig {
  mode: ThemeMode;
  primaryColor: string;
}

export const THEME_STORAGE_KEY = 'copaw_theme_mode';

/**
 * Get system color scheme preference
 */
export function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light';
  
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
}

/**
 * Get effective theme (resolves 'system' to actual mode)
 */
export function getEffectiveTheme(mode: ThemeMode): 'light' | 'dark' {
  if (mode === 'system') {
    return getSystemTheme();
  }
  return mode;
}

/**
 * Apply theme to document
 */
export function applyTheme(mode: ThemeMode): void {
  const effectiveTheme = getEffectiveTheme(mode);
  const root = document.documentElement;
  
  // Remove existing theme classes
  root.classList.remove('light', 'dark');
  
  // Add new theme class
  root.classList.add(effectiveTheme);
  
  // Set data attribute for CSS variables
  root.setAttribute('data-theme', effectiveTheme);
  
  // Store preference
  localStorage.setItem(THEME_STORAGE_KEY, mode);
}

/**
 * Load saved theme preference
 */
export function loadTheme(): ThemeMode {
  if (typeof window === 'undefined') return 'system';
  
  const saved = localStorage.getItem(THEME_STORAGE_KEY);
  if (saved && ['light', 'dark', 'system'].includes(saved)) {
    return saved as ThemeMode;
  }
  
  return 'system';
}

/**
 * Listen for system theme changes
 */
export function onSystemThemeChange(callback: (isDark: boolean) => void): () => void {
  if (typeof window === 'undefined') return () => {};
  
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  const handler = (e: MediaQueryListEvent) => {
    callback(e.matches);
  };
  
  mediaQuery.addEventListener('change', handler);
  
  return () => {
    mediaQuery.removeEventListener('change', handler);
  };
}
