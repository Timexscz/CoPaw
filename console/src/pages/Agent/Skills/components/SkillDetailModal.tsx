/**
 * Skill Detail Modal with Markdown rendering and category selection
 */

import { useState, useEffect } from "react";
import { Modal, Tabs, Select, message } from "@agentscope-ai/design";
import { Spin } from "antd";
import { useTheme } from "../../../../contexts/ThemeContext";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { categoriesApi } from "../../../../api/modules/categories";
import { useSkillCategories } from "../hooks/useSkillCategories";
import styles from "./SkillDetail.module.less";

interface SkillDetailModalProps {
  skillName: string;
  open: boolean;
  onClose: () => void;
}

interface SkillDetailData {
  name: string;
  source: string;
  path: string;
  metadata: Record<string, any>;
  category: string;
  category_name: string;
  category_icon: string;
  category_color: string;
  html_content: string;
  raw_content: string;
}

export function SkillDetailModal({ skillName, open, onClose }: SkillDetailModalProps) {
  const { isDark } = useTheme();
  const [skillData, setSkillData] = useState<SkillDetailData | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("preview");
  const [selectedCategory, setSelectedCategory] = useState("");
  const { categories } = useSkillCategories();

  const loadSkillDetail = async () => {
    if (!skillName || !open) return;
    
    setLoading(true);
    try {
      const data = await categoriesApi.getSkillDetail(skillName);
      setSkillData(data);
      setSelectedCategory(data.category);
    } catch (error) {
      message.error("加载技能详情失败");
      console.error("Failed to load skill detail:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryChange = async (categoryId: string) => {
    setSelectedCategory(categoryId);
    
    try {
      await categoriesApi.setSkillCategory(skillName, categoryId);
      message.success("分类已更新");
      
      // Reload to get updated category info
      await loadSkillDetail();
    } catch (error) {
      message.error("更新分类失败");
      setSelectedCategory(skillData?.category || "");
    }
  };

  useEffect(() => {
    if (open) {
      loadSkillDetail();
    }
  }, [skillName, open]);

  return (
    <Modal
      title={
        <div className={styles.modalTitle}>
          <span>{skillData?.category_icon} {skillData?.name}</span>
          <span
            className={styles.categoryBadge}
            style={{ 
              backgroundColor: skillData?.category_color,
              opacity: isDark ? 0.85 : 1
            }}
          >
            {skillData?.category_name}
          </span>
        </div>
      }
      open={open}
      onCancel={onClose}
      width={900}
      footer={null}
    >
      {loading ? (
        <div className={styles.loading}>
          <Spin tip="加载中..." />
        </div>
      ) : skillData ? (
        <div className={styles.detailContainer}>
          {/* Category Selector */}
          <div className={styles.categorySelector}>
            <span className={styles.selectorLabel}>分类：</span>
            <Select
              value={selectedCategory}
              onChange={handleCategoryChange}
              options={categories.map(cat => ({
                label: `${cat.icon} ${cat.name}`,
                value: cat.id,
              }))}
              style={{ width: 200 }}
            />
          </div>

          {/* Tabs for Preview/Source */}
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: "preview",
                label: "预览",
                children: (
                  <div className={styles.markdownPreview}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {skillData.raw_content}
                    </ReactMarkdown>
                  </div>
                ),
              },
              {
                key: "source",
                label: "源码",
                children: (
                  <pre className={styles.sourceCode}>
                    <code>{skillData.raw_content}</code>
                  </pre>
                ),
              },
            ]}
          />
        </div>
      ) : null}
    </Modal>
  );
}
