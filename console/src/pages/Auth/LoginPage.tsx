import { useState, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { Form, Input, Button, Card, message, Typography, Dropdown } from "antd";
import type { MenuProps } from "antd";
import { UserOutlined, LockOutlined, GlobalOutlined, MoonOutlined, SunOutlined, LaptopOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../contexts/AuthContext";
import { useTheme } from "../../contexts/ThemeContext";
import "./Auth.css";

const { Title, Text } = Typography;

// Language options
const languageOptions: MenuProps['items'] = [
  { key: 'zh', label: '简体中文', icon: '🇨🇳' },
  { key: 'en', label: 'English', icon: '🇺🇸' },
  { key: 'ja', label: '日本語', icon: '🇯🇵' },
  { key: 'ru', label: 'Русский', icon: '🇷🇺' },
];

// Theme options
const themeOptions: MenuProps['items'] = [
  { key: 'light', icon: <SunOutlined />, label: '浅色模式' },
  { key: 'dark', icon: <MoonOutlined />, label: '深色模式' },
  { key: 'system', icon: <LaptopOutlined />, label: '跟随系统' },
];

export default function LoginPage() {
  const [form] = Form.useForm();
  const { login, authEnabled, authenticated, checkAuth } = useAuth();
  const { t, i18n } = useTranslation();
  const { mode, setThemeMode, effectiveTheme } = useTheme();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || "/";

  useEffect(() => {
    if (authenticated && authEnabled) {
      navigate(from, { replace: true });
    }
  }, [authenticated, authEnabled, navigate, from]);

  useEffect(() => {
    if (!authEnabled && !loading) {
      checkAuth().then(() => {
        if (!authEnabled) {
          navigate("/");
        }
      });
    }
  }, [authEnabled, loading, checkAuth, navigate]);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success(t("auth.loginSuccess"));
      navigate(from, { replace: true });
    } catch (error: any) {
      console.error("Login error:", error);
      message.error(error.message || t("auth.loginFailed"));
      form.setFields([
        {
          name: "password",
          errors: [error.message || t("auth.loginFailed")],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Handle language change
  const handleLanguageChange: MenuProps['onClick'] = ({ key }) => {
    i18n.changeLanguage(key);
    localStorage.setItem('i18nextLng', key);
  };

  // Handle theme change
  const handleThemeChange: MenuProps['onClick'] = ({ key }) => {
    setThemeMode(key as 'light' | 'dark' | 'system');
  };

  if (!authEnabled) {
    return null;
  }

  return (
    <div className="auth-page">
      {/* Settings bar with theme and language */}
      <div className="auth-settings-bar">
        {/* Language selector */}
        <Dropdown
          menu={{ items: languageOptions, onClick: handleLanguageChange, selectedKeys: [i18n.language] }}
          trigger={['click']}
          placement="bottomRight"
        >
          <div className="auth-setting-btn">
            <span className="auth-setting-btn-icon"><GlobalOutlined /></span>
            <span className="auth-setting-btn-label">
              {i18n.language === 'zh' ? '简体中文' : i18n.language === 'en' ? 'English' : i18n.language === 'ja' ? '日本語' : 'Русский'}
            </span>
          </div>
        </Dropdown>

        {/* Theme selector */}
        <Dropdown
          menu={{ items: themeOptions, onClick: handleThemeChange, selectedKeys: [mode] }}
          trigger={['click']}
          placement="bottomRight"
        >
          <div className="auth-setting-btn">
            <span className="auth-setting-btn-icon">
              {effectiveTheme === 'dark' ? <MoonOutlined /> : <SunOutlined />}
            </span>
            <span className="auth-setting-btn-label">
              {mode === 'light' ? '浅色模式' : mode === 'dark' ? '深色模式' : '跟随系统'}
            </span>
          </div>
        </Dropdown>
      </div>

      <div className="auth-container">
        <Card className="auth-card">
          <div className="auth-logo">
            <img src="/logo.png" alt="CoPaw" />
          </div>
          <Title level={2} className="auth-title">
            {t("auth.welcomeTitle")}
          </Title>
          <Text type="secondary" className="auth-subtitle">
            {t("auth.welcomeSubtitle")}
          </Text>

          <Form
            form={form}
            name="login"
            onFinish={onFinish}
            autoComplete="off"
            size="large"
            className="auth-form"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: t("auth.usernameRequired") },
                { min: 3, message: t("auth.usernameMin") },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder={t("auth.usernamePlaceholder")}
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: t("auth.passwordRequired") },
                { min: 6, message: t("auth.passwordMin") },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder={t("auth.passwordPlaceholder")}
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                size="large"
                className="auth-button"
              >
                {t("auth.login")}
              </Button>
            </Form.Item>

            <div className="auth-footer">
              <Text type="secondary">
                {t("auth.noAccount")}{" "}
                <Link to="/register">{t("auth.signUp")}</Link>
              </Text>
            </div>
          </Form>
        </Card>
      </div>
    </div>
  );
}
