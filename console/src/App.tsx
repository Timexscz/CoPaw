import { createGlobalStyle } from "antd-style";
import { ConfigProvider } from "@agentscope-ai/design";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider, useTheme } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import { getThemeConfig } from "./config/themeConfig";
import MainLayout from "./layouts/MainLayout";
import "./styles/layout.css";
import "./styles/form-override.css";
import "./styles/globalTheme.less";
import "./styles/globalStyles.less";

const GlobalStyle = createGlobalStyle`
* {
  margin: 0;
  box-sizing: border-box;
}

body {
  background-color: var(--theme-bg-layout);
  color: var(--theme-text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
`;

function AppContent() {
  const { isDark } = useTheme();
  const themeConfig = getThemeConfig(isDark);

  return (
    <ConfigProvider theme={themeConfig} prefix="copaw" prefixCls="copaw">
      <MainLayout />
    </ConfigProvider>
  );
}

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <GlobalStyle />
          <AppContent />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
