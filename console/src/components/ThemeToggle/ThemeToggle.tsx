/**
 * Theme Toggle Component
 */

import { Dropdown, MenuProps } from 'antd';
import { MoonOutlined, SunOutlined, LaptopOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../../contexts/ThemeContext';
import styles from './ThemeToggle.module.less';

interface ThemeToggleProps {
  placement?: 'top' | 'bottom';
}

export function ThemeToggle({ placement = 'bottom' }: ThemeToggleProps) {
  const { t } = useTranslation();
  const { mode, setThemeMode, isDark } = useTheme();

  const menuItems: MenuProps['items'] = [
    {
      key: 'light',
      icon: <SunOutlined />,
      label: t('theme.light', '浅色模式'),
      onClick: () => setThemeMode('light'),
    },
    {
      key: 'dark',
      icon: <MoonOutlined />,
      label: t('theme.dark', '深色模式'),
      onClick: () => setThemeMode('dark'),
    },
    {
      key: 'system',
      icon: <LaptopOutlined />,
      label: t('theme.system', '跟随系统'),
      onClick: () => setThemeMode('system'),
    },
  ];

  const getIcon = () => {
    switch (mode) {
      case 'light':
        return <SunOutlined />;
      case 'dark':
        return <MoonOutlined />;
      case 'system':
        return isDark ? <MoonOutlined /> : <SunOutlined />;
    }
  };

  const getLabel = () => {
    // 保持显示文本长度一致（4 个字符）
    switch (mode) {
      case 'light':
        return t('theme.light', '浅色模式');
      case 'dark':
        return t('theme.dark', '深色模式');
      case 'system':
        return t('theme.system', '跟随系统');
    }
  };

  return (
    <Dropdown
      menu={{ items: menuItems, selectedKeys: [mode] }}
      placement={placement}
      trigger={['click']}
      overlayClassName={styles.themeDropdown}
    >
      <div className={styles.themeToggle}>
        <span className={styles.icon}>{getIcon()}</span>
        <span className={styles.label}>{getLabel()}</span>
      </div>
    </Dropdown>
  );
}
