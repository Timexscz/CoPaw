import { useState, useMemo } from "react";
import { Button, Form, Modal } from "@agentscope-ai/design";
import { DownloadOutlined, PlusOutlined, SettingOutlined, DownOutlined } from "@ant-design/icons";
import type { SkillSpec } from "../../../api/types";
import { SkillRow, SkillDrawer, CategoryManager } from "./components";
import { useSkills } from "./useSkills";
import { useTranslation } from "react-i18next";
import { categorizeSkill, getAllCategories } from "../../../config/skillCategories";
import styles from "./index.module.less";

function SkillsPage() {
  const { t } = useTranslation();
  const {
    skills,
    loading,
    importing,
    createSkill,
    importFromHub,
    toggleEnabled,
    deleteSkill,
  } = useSkills();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [importModalOpen, setImportModalOpen] = useState(false);
  const [importUrl, setImportUrl] = useState("");
  const [importUrlError, setImportUrlError] = useState("");
  const [editingSkill, setEditingSkill] = useState<SkillSpec | null>(null);
  const [form] = Form.useForm<SkillSpec>();
  const [categoryManagerOpen, setCategoryManagerOpen] = useState(false);
  
  // Collapsed state for categories (persisted in localStorage)
  const [collapsedCategories, setCollapsedCategories] = useState<Record<string, boolean>>(() => {
    const saved = localStorage.getItem("skills_collapsed_categories");
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
      localStorage.setItem("skills_collapsed_categories", JSON.stringify(next));
      return next;
    });
  };

  const supportedSkillUrlPrefixes = [
    "https://skills.sh/",
    "https://clawhub.ai/",
    "https://skillsmp.com/",
    "https://github.com/",
  ];

  const isSupportedSkillUrl = (url: string) => {
    return supportedSkillUrlPrefixes.some((prefix) => url.startsWith(prefix));
  };

  const handleCreate = () => {
    setEditingSkill(null);
    form.resetFields();
    form.setFieldsValue({
      enabled: false,
    });
    setDrawerOpen(true);
  };

  const closeImportModal = () => {
    if (importing) {
      return;
    }
    setImportModalOpen(false);
    setImportUrl("");
    setImportUrlError("");
  };

  const handleImportFromHub = () => {
    setImportModalOpen(true);
  };

  const handleImportUrlChange = (value: string) => {
    setImportUrl(value);
    const trimmed = value.trim();
    if (trimmed && !isSupportedSkillUrl(trimmed)) {
      setImportUrlError(t("skills.invalidSkillUrlSource"));
      return;
    }
    setImportUrlError("");
  };

  const handleConfirmImport = async () => {
    if (importing) return;
    const trimmed = importUrl.trim();
    if (!trimmed) return;
    if (!isSupportedSkillUrl(trimmed)) {
      setImportUrlError(t("skills.invalidSkillUrlSource"));
      return;
    }
    const success = await importFromHub(trimmed);
    if (success) {
      closeImportModal();
    }
  };

  const handleEdit = (skill: SkillSpec) => {
    setEditingSkill(skill);
    form.setFieldsValue(skill);
    setDrawerOpen(true);
  };

  const handleToggleEnabled = async (skill: SkillSpec, e: React.MouseEvent) => {
    e.stopPropagation();
    await toggleEnabled(skill);
  };

  const handleDelete = async (skill: SkillSpec, e?: React.MouseEvent) => {
    e?.stopPropagation();
    await deleteSkill(skill);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
    setEditingSkill(null);
  };

  const handleSubmit = async (values: { name: string; content: string }) => {
    try {
      const success = await createSkill(values.name, values.content);
      if (success) {
        setDrawerOpen(false);
      }
    } catch (error) {
      console.error("Submit failed", error);
    }
  };

  // Group skills by intelligent category (based on content analysis)
  const groupedSkills = useMemo(() => {
    const groups: Record<string, SkillSpec[]> = {};
    
    skills.forEach((skill) => {
      // Use intelligent categorization based on skill content
      const category = categorizeSkill({
        name: skill.name,
        description: skill.content,
        content: skill.content,
      });
      
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(skill);
    });

    // Sort skills within each group: enabled first, then by name
    Object.keys(groups).forEach((type) => {
      groups[type].sort((a, b) => {
        if (a.enabled && !b.enabled) return -1;
        if (!a.enabled && b.enabled) return 1;
        return a.name.localeCompare(b.name);
      });
    });

    return groups;
  }, [skills]);

  return (
    <div className={styles.skillsPage}>
      <div className={styles.header}>
        <div className={styles.headerInfo}>
          <h1 className={styles.title}>{t("skills.title")}</h1>
          <p className={styles.description}>{t("skills.description")}</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <Button
            type="default"
            onClick={() => setCategoryManagerOpen(true)}
            icon={<SettingOutlined />}
          >
            分类管理
          </Button>
          <Button
            type="primary"
            onClick={handleImportFromHub}
            icon={<DownloadOutlined />}
          >
            {t("skills.importSkills")}
          </Button>
          <Button type="primary" onClick={handleCreate} icon={<PlusOutlined />}>
            {t("skills.createSkill")}
          </Button>
        </div>
      </div>

      <Modal
        title={t("skills.importSkills")}
        open={importModalOpen}
        onCancel={closeImportModal}
        maskClosable={!importing}
        closable={!importing}
        keyboard={!importing}
        footer={
          <div style={{ textAlign: "right" }}>
            <Button
              onClick={closeImportModal}
              style={{ marginRight: 8 }}
              disabled={importing}
            >
              {t("common.cancel")}
            </Button>
            <Button
              type="primary"
              onClick={handleConfirmImport}
              loading={importing}
              disabled={importing || !importUrl.trim() || !!importUrlError}
            >
              {t("skills.importSkills")}
            </Button>
          </div>
        }
        width={760}
      >
        <div className={styles.importHintBlock}>
          <p className={styles.importHintTitle}>
            {t("skills.supportedSkillUrlSources")}
          </p>
          <ul className={styles.importHintList}>
            <li>https://skills.sh/</li>
            <li>https://clawhub.ai/</li>
            <li>https://skillsmp.com/</li>
            <li>https://github.com/</li>
          </ul>
          <p className={styles.importHintTitle}>{t("skills.urlExamples")}</p>
          <ul className={styles.importHintList}>
            <li>https://skills.sh/vercel-labs/skills/find-skills</li>
            <li>
              https://github.com/anthropics/skills/tree/main/skills/skill-creator
            </li>
          </ul>
        </div>

        <input
          className={styles.importUrlInput}
          value={importUrl}
          onChange={(e) => handleImportUrlChange(e.target.value)}
          placeholder={t("skills.enterSkillUrl")}
          disabled={importing}
        />
        {importUrlError ? (
          <div className={styles.importUrlError}>{importUrlError}</div>
        ) : null}
        {importing ? (
          <div className={styles.importLoadingText}>{t("common.loading")}</div>
        ) : null}
      </Modal>

      {loading ? (
        <div className={styles.loading}>
          <span className={styles.loadingText}>{t("common.loading")}</span>
        </div>
      ) : (
        <div className={styles.skillsList}>
          {getAllCategories().map((category) => {
            const categorySkills = groupedSkills[category.id] || [];
            if (categorySkills.length === 0) return null;
            
            const isCollapsed = collapsedCategories[category.id] ?? false;
            
            return (
              <div key={category.id} className={styles.skillGroup}>
                <div
                  className={styles.groupHeader}
                  onClick={() => handleToggleCategory(category.id)}
                  style={{ cursor: "pointer" }}
                >
                  <h2 className={styles.groupTitle} style={{ color: category.color }}>
                    {category.icon} {category.name}
                    <span className={styles.groupCount}>({categorySkills.length})</span>
                  </h2>
                  <DownOutlined
                    className={styles.expandIcon}
                    style={{
                      transform: isCollapsed ? "rotate(-90deg)" : "rotate(0deg)",
                      transition: "transform 0.2s",
                    }}
                  />
                </div>
                {!isCollapsed && (
                  <div className={styles.skillRows}>
                    {categorySkills.map((skill) => (
                      <SkillRow
                        key={skill.name}
                        skill={skill}
                        onClick={() => handleEdit(skill)}
                        onToggleEnabled={(e) => handleToggleEnabled(skill, e)}
                        onDelete={(e) => handleDelete(skill, e)}
                      />
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <SkillDrawer
        open={drawerOpen}
        editingSkill={editingSkill}
        form={form}
        onClose={handleDrawerClose}
        onSubmit={handleSubmit}
      />

      <CategoryManager
        open={categoryManagerOpen}
        onClose={() => setCategoryManagerOpen(false)}
      />
    </div>
  );
}

export default SkillsPage;
