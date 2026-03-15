// Note: AgentScopeRuntimeWebUI has been removed from @agentscope-ai/chat in newer versions
// This is a temporary placeholder until we migrate to the new ChatAnywhere API
import { useMemo, useState } from "react";
import { Modal, Button, Result, Empty } from "antd";
import { ExclamationCircleOutlined, SettingOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useLocalStorageState } from "ahooks";
import defaultConfig, { DefaultConfig } from "./OptionsPanel/defaultConfig";
import "./index.module.less";

// Type definition for AgentScopeRuntimeWebUI options (placeholder)
interface IAgentScopeRuntimeWebUIOptions {
  api?: any;
  session?: any;
  theme?: any;
  customToolRenderConfig?: any;
  [key: string]: any;
}

interface CustomWindow extends Window {
  currentSessionId?: string;
  currentUserId?: string;
  currentChannel?: string;
}

declare const window: CustomWindow;

type OptionsConfig = DefaultConfig;

export default function ChatPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [showModelPrompt, setShowModelPrompt] = useState(false);
  const [optionsConfig] = useLocalStorageState<OptionsConfig>(
    "agent-scope-runtime-webui-options",
    {
      defaultValue: defaultConfig,
      listenStorageChange: true,
    },
  );

  const handleConfigureModel = () => {
    setShowModelPrompt(false);
    navigate("/models");
  };

  const handleSkipConfiguration = () => {
    setShowModelPrompt(false);
  };

  // Note: options configuration for AgentScopeRuntimeWebUI is kept for reference
  // but not used until we migrate to the new ChatAnywhere API
  useMemo(() => {
    return {
      ...optionsConfig,
    } as unknown as IAgentScopeRuntimeWebUIOptions;
  }, [optionsConfig]);

  return (
    <div style={{ height: "100%", width: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Empty
        description={
          <div style={{ textAlign: "center", maxWidth: 500 }}>
            <h3>Chat Component Temporarily Unavailable</h3>
            <p>
              The AgentScopeRuntimeWebUI component has been removed from the 
              @agentscope-ai/chat package. We are working on migrating to the 
              new ChatAnywhere API.
            </p>
            <p style={{ marginTop: 16 }}>
              <Button
                type="primary"
                icon={<SettingOutlined />}
                onClick={handleConfigureModel}
              >
                Configure Model
              </Button>
            </p>
          </div>
        }
      />

      <Modal open={showModelPrompt} closable={false} footer={null} width={480}>
        <Result
          icon={<ExclamationCircleOutlined style={{ color: "#faad14" }} />}
          title={t("modelConfig.promptTitle")}
          subTitle={t("modelConfig.promptMessage")}
          extra={[
            <Button key="skip" onClick={handleSkipConfiguration}>
              {t("modelConfig.skipButton")}
            </Button>,
            <Button
              key="configure"
              type="primary"
              icon={<SettingOutlined />}
              onClick={handleConfigureModel}
            >
              {t("modelConfig.configureButton")}
            </Button>,
          ]}
        />
      </Modal>
    </div>
  );
}
