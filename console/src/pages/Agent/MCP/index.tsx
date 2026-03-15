import { useState, useMemo } from "react";
import { Button, Empty, Modal } from "@agentscope-ai/design";
import { DownOutlined, SettingOutlined } from "@ant-design/icons";
import type { MCPClientInfo } from "../../../api/types";
import { MCPClientRow, MCPCategoryManager } from "./components";
import { useMCP } from "./useMCP";
import { useTranslation } from "react-i18next";
import { categorizeMCP, getAllMCPCategories } from "../../../config/mcpCategories";
import styles from "./index.module.less";

type MCPTransport = "stdio" | "streamable_http" | "sse";

function normalizeTransport(raw?: unknown): MCPTransport | undefined {
  if (typeof raw !== "string") return undefined;
  const value = raw.trim().toLowerCase();
  switch (value) {
    case "stdio":
      return "stdio";
    case "sse":
      return "sse";
    case "streamablehttp":
    case "streamable_http":
    case "http":
      return "streamable_http";
    default:
      return undefined;
  }
}

function normalizeClientData(key: string, rawData: any) {
  const transport =
    normalizeTransport(rawData.transport ?? rawData.type) ??
    (rawData.url || rawData.baseUrl || !rawData.command
      ? "streamable_http"
      : "stdio");

  const command =
    transport === "stdio" ? (rawData.command ?? "").toString() : "";

  return {
    name: rawData.name || key,
    description: rawData.description || "",
    enabled: rawData.enabled ?? rawData.isActive ?? true,
    transport,
    url: (rawData.url || rawData.baseUrl || "").toString(),
    headers: rawData.headers || {},
    command,
    args: Array.isArray(rawData.args) ? rawData.args : [],
    env: rawData.env || {},
    cwd: (rawData.cwd || "").toString(),
  };
}

function MCPPage() {
  const { t } = useTranslation();
  const {
    clients,
    loading,
    toggleEnabled,
    deleteClient,
    createClient,
    updateClient,
  } = useMCP();
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newClientJson, setNewClientJson] = useState(`{
  "mcpServers": {
    "example-client": {
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "env": {
        "API_KEY": "<YOUR_API_KEY>"
      }
    }
  }
}`);
  const [categoryManagerOpen, setCategoryManagerOpen] = useState(false);

  // Collapsed state for categories (persisted in localStorage)
  const [collapsedCategories, setCollapsedCategories] = useState<Record<string, boolean>>(() => {
    const saved = localStorage.getItem("mcp_collapsed_categories");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return {};
      }
    }
    return {};
  });

  const handleToggleCategory = (categoryId: string) => {
    setCollapsedCategories(prev => {
      const next = { ...prev, [categoryId]: !prev[categoryId] };
      localStorage.setItem("mcp_collapsed_categories", JSON.stringify(next));
      return next;
    });
  };

  const handleToggleEnabled = async (
    client: MCPClientInfo,
    e?: React.MouseEvent,
  ) => {
    e?.stopPropagation();
    await toggleEnabled(client);
  };

  const handleDelete = async (client: MCPClientInfo, e?: React.MouseEvent) => {
    e?.stopPropagation();
    await deleteClient(client);
  };

  const handleCreateClient = async () => {
    try {
      const parsed = JSON.parse(newClientJson);

      // Support two formats:
      // Format 1: { "mcpServers": { "key": { "command": "...", ... } } }
      // Format 2: { "key": { "command": "...", ... } }
      // Format 3: { "key": "...", "name": "...", "command": "...", ... } (direct)

      let clientsToCreate: Array<{ key: string; data: any }> = [];

      if (parsed.mcpServers) {
        // Format 1: nested mcpServers
        Object.entries(parsed.mcpServers).forEach(
          ([key, data]: [string, any]) => {
            clientsToCreate.push({
              key,
              data: normalizeClientData(key, data),
            });
          },
        );
      } else if (
        parsed.key &&
        (parsed.command || parsed.url || parsed.baseUrl)
      ) {
        // Format 3: direct format with key field
        const { key, ...clientData } = parsed;
        clientsToCreate.push({
          key,
          data: normalizeClientData(key, clientData),
        });
      } else {
        // Format 2: direct client objects with keys
        Object.entries(parsed).forEach(([key, data]: [string, any]) => {
          if (
            typeof data === "object" &&
            (data.command || data.url || data.baseUrl)
          ) {
            clientsToCreate.push({
              key,
              data: normalizeClientData(key, data),
            });
          }
        });
      }

      // Create all clients
      let allSuccess = true;
      for (const { key, data } of clientsToCreate) {
        const success = await createClient(key, data);
        if (!success) allSuccess = false;
      }

      if (allSuccess) {
        setCreateModalOpen(false);
        setNewClientJson(`{
  "mcpServers": {
    "example-client": {
      "command": "npx",
      "args": ["-y", "@example/mcp-server"],
      "env": {
        "API_KEY": "<YOUR_API_KEY>"
      }
    }
  }
}`);
      }
    } catch (error) {
      alert("Invalid JSON format");
    }
  };

  // Group clients by intelligent category (based on transport and content analysis)
  const groupedClients = useMemo(() => {
    const groups: Record<string, MCPClientInfo[]> = {};

    clients.forEach((client) => {
      // Use intelligent categorization based on client configuration
      const category = categorizeMCP({
        name: client.name,
        description: client.description,
        transport: client.transport,
        command: client.command,
        url: client.url,
      });
      
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(client);
    });

    // Sort clients within each group: enabled first, then by name
    Object.keys(groups).forEach((type) => {
      groups[type].sort((a, b) => {
        if (a.enabled && !b.enabled) return -1;
        if (!a.enabled && b.enabled) return 1;
        return a.name.localeCompare(b.name);
      });
    });

    return groups;
  }, [clients]);

  return (
    <div className={styles.mcpPage}>
      <div
        className={styles.mcpHeader}
      >
        <div>
          <h1 className={styles.mcpTitle}>
            {t("mcp.title")}
          </h1>
          <p className={styles.mcpDescription}>
            {t("mcp.description")}
          </p>
        </div>
        <div className={styles.mcpActions}>
          <Button
            type="default"
            onClick={() => setCategoryManagerOpen(true)}
            icon={<SettingOutlined />}
          >
            分类管理
          </Button>
          <Button type="primary" onClick={() => setCreateModalOpen(true)}>
            {t("mcp.create")}
          </Button>
        </div>
      </div>

      {loading ? (
        <div className={styles.mcpLoading}>
          <p className={styles.mcpLoadingText}>{t("common.loading")}</p>
        </div>
      ) : clients.length === 0 ? (
        <Empty description={t("mcp.emptyState")} />
      ) : (
        <div className={styles.mcpGroups}>
          {getAllMCPCategories().map((category) => {
            const categoryClients = groupedClients[category.id] || [];
            if (categoryClients.length === 0) return null;
            
            const isCollapsed = collapsedCategories[category.id] ?? false;
            
            return (
              <div key={category.id} className={styles.mcpGroup}>
                <div
                  className={styles.mcpGroupHeader}
                  onClick={() => handleToggleCategory(category.id)}
                >
                  <h2 className={styles.mcpGroupTitle}>
                    <span style={{ color: category.color }}>
                      {category.icon} {category.name}
                    </span>
                    <span className={styles.mcpGroupCount}>
                      ({categoryClients.length})
                    </span>
                  </h2>
                  <DownOutlined
                    className={styles.mcpGroupIcon}
                    style={{
                      transform: isCollapsed ? "rotate(-90deg)" : "rotate(0deg)",
                    }}
                  />
                </div>
                {!isCollapsed && (
                  <div className={styles.mcpGroupContent}>
                    {categoryClients.map((client) => (
                      <MCPClientRow
                        key={client.key}
                        client={client}
                        onToggle={handleToggleEnabled}
                        onDelete={handleDelete}
                        onUpdate={updateClient}
                      />
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <Modal
        title={t("mcp.create")}
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={
          <div className={styles.mcpModalFooter}>
            <Button
              onClick={() => setCreateModalOpen(false)}
              className={styles.mcpModalBtn}
            >
              {t("common.cancel")}
            </Button>
            <Button type="primary" onClick={handleCreateClient}>
              {t("common.create")}
            </Button>
          </div>
        }
        width={800}
      >
        <div className={styles.mcpModalHint}>
          <p className={styles.mcpModalHintTitle}>
            {t("mcp.formatSupport")}:
          </p>
          <ul className={styles.mcpModalHintList}>
            <li>
              Standard format:{" "}
              <code>{`{ "mcpServers": { "key": {...} } }`}</code>
            </li>
            <li>
              Direct format: <code>{`{ "key": {...} }`}</code>
            </li>
            <li>
              Single format:{" "}
              <code>{`{ "key": "...", "name": "...", "command": "..." }`}</code>
            </li>
          </ul>
        </div>
        <textarea
          value={newClientJson}
          onChange={(e) => setNewClientJson(e.target.value)}
          className={styles.mcpModalTextarea}
        />
      </Modal>

      <MCPCategoryManager
        open={categoryManagerOpen}
        onClose={() => setCategoryManagerOpen(false)}
      />
    </div>
  );
}

export default MCPPage;
