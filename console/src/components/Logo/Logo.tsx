/**
 * Logo Component with Theme Support
 */

import { useTheme } from '../../contexts/ThemeContext';
import styles from './Logo.module.less';

interface LogoProps {
  collapsed?: boolean;
}

export function Logo({ collapsed }: LogoProps) {
  const { isDark } = useTheme();

  return (
    <div className={styles.logoWrapper}>
      <div className={styles.logo}>
        <img
          src="/logo.png"
          alt="CoPaw Logo"
          className={styles.logoImg}
          style={{
            filter: isDark ? 'brightness(0) invert(1)' : 'none'
          }}
        />
      </div>
      {!collapsed && (
        <span className={styles.versionBadge}>
          v0.0.5
        </span>
      )}
    </div>
  );
}
