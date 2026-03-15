/**
 * Generate theme configuration for Ant Design ConfigProvider
 */

import type { ThemeConfig } from 'antd';

export function getThemeConfig(isDark: boolean): ThemeConfig {
  return {
    token: {
      // 基础颜色
      colorPrimary: isDark ? '#177ddc' : '#1890ff',
      colorSuccess: isDark ? '#389e0d' : '#52c41a',
      colorWarning: isDark ? '#d89614' : '#faad14',
      colorError: isDark ? '#d9363e' : '#ff4d4f',
      colorInfo: isDark ? '#177ddc' : '#1890ff',
      
      // 背景颜色
      colorBgBase: isDark ? '#000000' : '#ffffff',
      colorBgContainer: isDark ? '#1f1f1f' : '#ffffff',
      colorBgElevated: isDark ? '#262626' : '#ffffff',
      colorBgLayout: isDark ? '#000000' : '#f0f2f5',
      
      // 文字颜色
      colorText: isDark ? 'rgba(255, 255, 255, 0.85)' : 'rgba(0, 0, 0, 0.85)',
      colorTextSecondary: isDark ? 'rgba(255, 255, 255, 0.65)' : 'rgba(0, 0, 0, 0.65)',
      colorTextTertiary: isDark ? 'rgba(255, 255, 255, 0.45)' : 'rgba(0, 0, 0, 0.45)',
      
      // 边框颜色
      colorBorder: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
      colorBorderSecondary: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
      
      // 阴影效果 - 暗色模式使用更柔和的阴影，垂直偏移设为 0
      boxShadow: isDark
        ? '0 0 16px 0 rgba(0, 0, 0, 0.24), 0 0 6px -4px rgba(0, 0, 0, 0.32), 0 0 28px 8px rgba(0, 0, 0, 0.16)'
        : '0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05)',
      boxShadowSecondary: isDark
        ? '0 0 6px -4px rgba(0, 0, 0, 0.24), 0 0 16px 0 rgba(0, 0, 0, 0.16), 0 0 28px 8px rgba(0, 0, 0, 0.1)'
        : '0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 9px 28px 8px rgba(0, 0, 0, 0.05)',
      
      borderRadius: 6,
      borderRadiusLG: 8,
    },
    components: {
      Button: {
        colorPrimary: isDark ? '#177ddc' : '#1890ff',
        colorPrimaryHover: isDark ? '#4096ff' : '#40a9ff',
        colorPrimaryActive: isDark ? '#0958b9' : '#096dd9',
      },
      Input: {
        colorBgContainer: isDark ? '#141414' : '#ffffff',
        colorBorder: isDark ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.12)',
        activeBorderColor: isDark ? '#177ddc' : '#1890ff',
      },
      Select: {
        colorBgContainer: isDark ? '#141414' : '#ffffff',
        colorBorder: isDark ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.12)',
        colorBgElevated: isDark ? '#1f1f1f' : '#ffffff',
      },
      Modal: {
        colorBgElevated: isDark ? '#1f1f1f' : '#ffffff',
        colorBgMask: isDark ? 'rgba(0, 0, 0, 0.75)' : 'rgba(0, 0, 0, 0.45)',
      },
      Drawer: {
        colorBgElevated: isDark ? '#1f1f1f' : '#ffffff',
      },
      Table: {
        colorBgContainer: isDark ? '#1f1f1f' : '#ffffff',
        colorBorder: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
        headerBg: isDark ? '#141414' : '#fafafa',
      },
      Card: {
        colorBgContainer: isDark ? '#1f1f1f' : '#ffffff',
        colorBorder: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
        actionsBg: isDark ? '#141414' : '#fafafa',
      },
      Menu: {
        colorBgContainer: isDark ? '#141414' : '#ffffff',
        colorBorder: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
        itemHoverBg: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
        itemSelectedBg: isDark ? 'rgba(23, 125, 220, 0.15)' : 'rgba(24, 144, 255, 0.1)',
      },
      Layout: {
        headerBg: isDark ? '#141414' : '#ffffff',
        siderBg: isDark ? '#141414' : '#ffffff',
      },
      Dropdown: {
        colorBgElevated: isDark ? '#1f1f1f' : '#ffffff',
      },
      Tooltip: {
        colorBgElevated: isDark ? '#262626' : '#ffffff',
      },
      Tabs: {
        colorBgContainer: isDark ? '#1f1f1f' : '#ffffff',
      },
      Collapse: {
        colorBgContainer: isDark ? '#1f1f1f' : '#ffffff',
        colorBorder: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
      },
      Pagination: {
        colorBgContainer: isDark ? '#1f1f1f' : '#ffffff',
        colorBorder: isDark ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.12)',
      },
      Tag: {
        colorBgContainer: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
        colorBorder: isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
      },
    },
  };
}
