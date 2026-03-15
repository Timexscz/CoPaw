/**
 * Theme Context for managing app-wide theme
 */

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import type { ThemeMode, ThemeConfig } from '../config/theme';
import {
  loadTheme,
  applyTheme,
  getEffectiveTheme,
  onSystemThemeChange,
} from '../config/theme';

interface ThemeContextType extends ThemeConfig {
  setThemeMode: (mode: ThemeMode) => void;
  toggleTheme: () => void;
  effectiveTheme: 'light' | 'dark';
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [mode, setMode] = useState<ThemeMode>(() => loadTheme());
  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>(() =>
    getEffectiveTheme(mode)
  );

  // Apply theme when mode changes
  useEffect(() => {
    applyTheme(mode);
    setEffectiveTheme(getEffectiveTheme(mode));
  }, [mode]);

  // Listen for system theme changes when in 'system' mode
  useEffect(() => {
    if (mode !== 'system') return;

    const unsubscribe = onSystemThemeChange((isDark: boolean) => {
      setEffectiveTheme(isDark ? 'dark' : 'light');
      applyTheme('system');
    });

    return unsubscribe;
  }, [mode]);

  const setThemeMode = useCallback((newMode: ThemeMode) => {
    setMode(newMode);
  }, []);

  const toggleTheme = useCallback(() => {
    setMode((prev) => {
      if (prev === 'light') return 'dark';
      if (prev === 'dark') return 'light';
      // If system, toggle to opposite of current effective
      return effectiveTheme === 'light' ? 'dark' : 'light';
    });
  }, [effectiveTheme]);

  const value: ThemeContextType = {
    mode,
    primaryColor: '#1890ff',
    setThemeMode,
    toggleTheme,
    effectiveTheme,
    isDark: effectiveTheme === 'dark',
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to use theme context
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  
  return context;
}

/**
 * Hook to check if dark mode is active
 */
export function useDarkMode(): boolean {
  const { isDark } = useTheme();
  return isDark;
}
