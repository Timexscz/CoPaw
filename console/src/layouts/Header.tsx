import { Layout, Space, Dropdown, Avatar } from "antd";
import type { MenuProps } from "antd";
import LanguageSwitcher from "../components/LanguageSwitcher";
import { ThemeToggle } from "../components/ThemeToggle";
import { useTranslation } from "react-i18next";
import {
  FileTextOutlined,
  BookOutlined,
  QuestionCircleOutlined,
  GithubOutlined,
  UserOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import { Button, Tooltip } from "@agentscope-ai/design";
import { useAuth } from "../contexts/AuthContext";
import styles from "./index.module.less";

const { Header: AntHeader } = Layout;

// Navigation URLs
const NAV_URLS = {
  docs: "https://copaw.agentscope.io/docs/intro",
  faq: "https://copaw.agentscope.io/docs/faq",
  changelog: "https://github.com/agentscope-ai/CoPaw/releases",
  github: "https://github.com/agentscope-ai/CoPaw",
} as const;

const keyToLabel: Record<string, string> = {
  chat: "nav.chat",
  channels: "nav.channels",
  sessions: "nav.sessions",
  "cron-jobs": "nav.cronJobs",
  heartbeat: "nav.heartbeat",
  skills: "nav.skills",
  mcp: "nav.mcp",
  "agent-config": "nav.agentConfig",
  workspace: "nav.workspace",
  models: "nav.models",
  environments: "nav.environments",
};

interface HeaderProps {
  selectedKey: string;
}

export default function Header({ selectedKey }: HeaderProps) {
  const { t } = useTranslation();
  const { user, authEnabled, logout } = useAuth();

  const handleNavClick = (url: string) => {
    if (url) {
      window.open(url, "_blank");
    }
  };

  const handleLogout = async () => {
    await logout();
    window.location.href = "/login";
  };

  const userMenuItems: MenuProps["items"] = [
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: t("auth.logout") || "Logout",
      onClick: handleLogout,
    },
  ];

  return (
    <AntHeader className={styles.header}>
      <span className={styles.headerTitle}>
        {t(keyToLabel[selectedKey] || "nav.chat")}
      </span>
      <Space size="middle">
        <Tooltip title={t("header.changelog")}>
          <Button
            icon={<FileTextOutlined />}
            type="text"
            onClick={() => handleNavClick(NAV_URLS.changelog)}
          >
            {t("header.changelog")}
          </Button>
        </Tooltip>
        <Tooltip title={t("header.docs")}>
          <Button
            icon={<BookOutlined />}
            type="text"
            onClick={() => handleNavClick(NAV_URLS.docs)}
          >
            {t("header.docs")}
          </Button>
        </Tooltip>
        <Tooltip title={t("header.faq")}>
          <Button
            icon={<QuestionCircleOutlined />}
            type="text"
            onClick={() => handleNavClick(NAV_URLS.faq)}
          >
            {t("header.faq")}
          </Button>
        </Tooltip>
        <Tooltip title={t("header.github")}>
          <Button
            icon={<GithubOutlined />}
            type="text"
            onClick={() => handleNavClick(NAV_URLS.github)}
          >
            {t("header.github")}
          </Button>
        </Tooltip>
        <ThemeToggle placement="bottom" />
        <LanguageSwitcher />
        {authEnabled && user && (
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Space style={{ cursor: "pointer" }}>
              <Avatar
                size="small"
                icon={<UserOutlined />}
                style={{ backgroundColor: "#1890ff" }}
              />
              <span className={styles.username}>{user.username}</span>
            </Space>
          </Dropdown>
        )}
      </Space>
    </AntHeader>
  );
}
