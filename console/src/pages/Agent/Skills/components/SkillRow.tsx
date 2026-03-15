import { Button, Tooltip, message } from "@agentscope-ai/design";
import {
  DeleteOutlined,
  FileTextFilled,
  FileZipFilled,
  FilePdfFilled,
  FileWordFilled,
  FileExcelFilled,
  FilePptFilled,
  FileImageFilled,
  CodeFilled,
  CheckCircleFilled,
  StopOutlined,
} from "@ant-design/icons";
import type { SkillSpec } from "../../../../api/types";
import { useTranslation } from "react-i18next";
import styles from "../index.module.less";

interface SkillRowProps {
  skill: SkillSpec;
  onClick: () => void;
  onToggleEnabled: (e: React.MouseEvent) => void;
  onDelete?: (e?: React.MouseEvent) => void;
}

const getFileIcon = (filePath: string) => {
  const extension = filePath.split(".").pop()?.toLowerCase() || "";

  switch (extension) {
    case "txt":
    case "md":
    case "markdown":
      return <FileTextFilled style={{ color: "#1890ff" }} />;
    case "zip":
    case "rar":
    case "7z":
    case "tar":
    case "gz":
      return <FileZipFilled style={{ color: "#fa8c16" }} />;
    case "pdf":
      return <FilePdfFilled style={{ color: "#f5222d" }} />;
    case "doc":
    case "docx":
      return <FileWordFilled style={{ color: "#2b579a" }} />;
    case "xls":
    case "xlsx":
      return <FileExcelFilled style={{ color: "#217346" }} />;
    case "ppt":
    case "pptx":
      return <FilePptFilled style={{ color: "#d24726" }} />;
    case "jpg":
    case "jpeg":
    case "png":
    case "gif":
    case "svg":
    case "webp":
      return <FileImageFilled style={{ color: "#eb2f96" }} />;
    case "py":
    case "js":
    case "ts":
    case "jsx":
    case "tsx":
    case "java":
    case "cpp":
    case "c":
    case "go":
    case "rs":
    case "rb":
    case "php":
      return <CodeFilled style={{ color: "#52c41a" }} />;
    default:
      return <FileTextFilled style={{ color: "#1890ff" }} />;
  }
};

export function SkillRow({
  skill,
  onClick,
  onToggleEnabled,
  onDelete,
}: SkillRowProps) {
  const { t } = useTranslation();
  const isCustomized = skill.source === "customized";

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!skill.enabled && onDelete) {
      if (!isCustomized) {
        message.warning(t("skills.cannotDeleteBuiltIn"));
        return;
      }
      onDelete(e);
    }
  };

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleEnabled(e);
  };

  return (
    <div
      className={`${styles.skillRow} ${
        skill.enabled ? styles.enabledRow : ""
      }`}
      onClick={onClick}
    >
      <div className={styles.rowLeft}>
        <span className={styles.rowFileIcon}>{getFileIcon(skill.name)}</span>
        <div className={styles.rowInfo}>
          <Tooltip title={skill.name}>
            <span className={styles.rowTitle}>{skill.name}</span>
          </Tooltip>
          <div className={styles.rowMeta}>
            <span className={styles.rowMetaLabel}>{t("skills.source")}:</span>
            <code className={styles.rowMetaValue}>{skill.source}</code>
            <span className={styles.rowMetaDivider}>|</span>
            <span className={styles.rowMetaLabel}>{t("skills.path")}:</span>
            <code className={`${styles.rowMetaValue} ${styles.rowPath}`}>
              {skill.path}
            </code>
          </div>
        </div>
      </div>

      <div className={styles.rowActions}>
        <Button
          type={skill.enabled ? "primary" : "default"}
          size="small"
          onClick={handleToggle}
          className={`${styles.rowToggleButton} ${
            skill.enabled ? styles.rowToggleEnabled : styles.rowToggleDisabled
          }`}
          icon={
            skill.enabled ? (
              <CheckCircleFilled />
            ) : (
              <StopOutlined style={{ transform: "rotate(45deg)" }} />
            )
          }
        >
          {skill.enabled ? t("common.enabled") : t("common.disabled")}
        </Button>

        {onDelete && (
          <Button
            type="text"
            size="small"
            danger
            icon={<DeleteOutlined />}
            className={styles.rowDeleteButton}
            onClick={handleDeleteClick}
            disabled={skill.enabled}
            title={isCustomized ? t("common.delete") : t("skills.cannotDeleteBuiltIn")}
          />
        )}
      </div>
    </div>
  );
}
