import { Button, Tooltip, Modal } from "@agentscope-ai/design";
import {
  DeleteOutlined,
  CheckCircleFilled,
  StopOutlined,
} from "@ant-design/icons";
import { Server } from "lucide-react";
import type { MCPClientInfo } from "../../../../api/types";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import styles from "../index.module.less";

interface MCPClientRowProps {
  client: MCPClientInfo;
  onToggle: (client: MCPClientInfo, e: React.MouseEvent) => void;
  onDelete: (client: MCPClientInfo, e: React.MouseEvent) => void;
  onUpdate: (key: string, updates: any) => Promise<boolean>;
}

export function MCPClientRow({
  client,
  onToggle,
  onDelete,
  onUpdate,
}: MCPClientRowProps) {
  const { t } = useTranslation();
  const [jsonModalOpen, setJsonModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [editedJson, setEditedJson] = useState("");
  const [isEditing, setIsEditing] = useState(false);

  // Determine if MCP client is remote or local based on command
  const isRemote =
    client.transport === "streamable_http" || client.transport === "sse";
  const clientType = isRemote ? "Remote" : "Local";

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setDeleteModalOpen(true);
  };

  const confirmDelete = () => {
    setDeleteModalOpen(false);
    onDelete(client, null as any);
  };

  const handleRowClick = () => {
    const jsonStr = JSON.stringify(client, null, 2);
    setEditedJson(jsonStr);
    setIsEditing(false);
    setJsonModalOpen(true);
  };

  const handleSaveJson = async () => {
    try {
      const parsed = JSON.parse(editedJson);
      const { key, ...updates } = parsed;

      // Send all updates directly to backend, let backend handle env masking check
      const success = await onUpdate(client.key, updates);
      if (success) {
        setJsonModalOpen(false);
        setIsEditing(false);
      }
    } catch (error) {
      alert("Invalid JSON format");
    }
  };

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggle(client, e);
  };

  const clientJson = JSON.stringify(client, null, 2);

  return (
    <>
      <div
        className={`${styles.mcpRow} ${
          client.enabled ? styles.enabledRow : ""
        }`}
        onClick={handleRowClick}
      >
        <div className={styles.rowLeft}>
          <span className={styles.rowFileIcon}>
            <Server className={styles.mcpClientIcon} />
          </span>
          <div className={styles.rowInfo}>
            <div className={styles.rowTitleWrapper}>
              <Tooltip title={client.name}>
                <span className={styles.rowTitle}>{client.name}</span>
              </Tooltip>
              <span
                className={`${styles.rowTypeBadge} ${
                  isRemote ? styles.remote : styles.local
                }`}
              >
                {clientType}
              </span>
            </div>
            <div className={styles.rowDescription}>
              {client.description || "\u00A0"}
            </div>
          </div>
        </div>

        <div className={styles.rowActions}>
          <Button
            type={client.enabled ? "primary" : "default"}
            size="small"
            onClick={handleToggle}
            className={`${styles.rowToggleButton} ${
              client.enabled ? styles.rowToggleEnabled : styles.rowToggleDisabled
            }`}
            icon={
              client.enabled ? (
                <CheckCircleFilled />
              ) : (
                <StopOutlined style={{ transform: "rotate(45deg)" }} />
              )
            }
          >
            {client.enabled ? t("common.enabled") : t("common.disabled")}
          </Button>

          <Button
            type="text"
            size="small"
            danger
            icon={<DeleteOutlined />}
            className={styles.rowDeleteButton}
            onClick={handleDeleteClick}
            disabled={client.enabled}
          />
        </div>
      </div>

      <Modal
        title={t("common.confirm")}
        open={deleteModalOpen}
        onOk={confirmDelete}
        onCancel={() => setDeleteModalOpen(false)}
        okText={t("common.confirm")}
        cancelText={t("common.cancel")}
        okButtonProps={{ danger: true }}
      >
        <p>{t("mcp.deleteConfirm")}</p>
      </Modal>

      <Modal
        title={`${client.name} - Configuration`}
        open={jsonModalOpen}
        onCancel={() => setJsonModalOpen(false)}
        footer={
          <div style={{ textAlign: "right" }}>
            <Button
              onClick={() => setJsonModalOpen(false)}
              style={{ marginRight: 8 }}
            >
              {t("common.cancel")}
            </Button>
            {isEditing ? (
              <Button type="primary" onClick={handleSaveJson}>
                {t("common.save")}
              </Button>
            ) : (
              <Button type="primary" onClick={() => setIsEditing(true)}>
                {t("common.edit")}
              </Button>
            )}
          </div>
        }
        width={700}
      >
        {isEditing ? (
          <textarea
            value={editedJson}
            onChange={(e) => setEditedJson(e.target.value)}
            className={styles.editJsonTextArea}
          />
        ) : (
          <pre className={styles.preformattedText}>{clientJson}</pre>
        )}
      </Modal>
    </>
  );
}
