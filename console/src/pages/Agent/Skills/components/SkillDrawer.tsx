import { useState, useEffect, useCallback } from "react";
import { Drawer, Form, Input, Button, message, Select } from "@agentscope-ai/design";
import { useTranslation } from "react-i18next";
import type { FormInstance } from "antd";
import type { SkillSpec } from "../../../../api/types";
import { MarkdownCopy } from "../../../../components/MarkdownCopy/MarkdownCopy";
import { getEnabledCategories, categorizeSkill } from "../../../../config/skillCategories";

/**
 * Parse frontmatter from content string.
 * Returns an object with parsed key-value pairs, or null if no valid frontmatter found.
 */
function parseFrontmatter(content: string): Record<string, string> | null {
  const trimmed = content.trim();
  if (!trimmed.startsWith("---")) return null;

  const endIndex = trimmed.indexOf("---", 3);
  if (endIndex === -1) return null;

  const frontmatterBlock = trimmed.slice(3, endIndex).trim();
  if (!frontmatterBlock) return null;

  const result: Record<string, string> = {};
  for (const line of frontmatterBlock.split("\n")) {
    const colonIndex = line.indexOf(":");
    if (colonIndex > 0) {
      const key = line.slice(0, colonIndex).trim();
      const value = line.slice(colonIndex + 1).trim();
      result[key] = value;
    }
  }
  return result;
}

interface SkillDrawerProps {
  open: boolean;
  editingSkill: SkillSpec | null;
  form: FormInstance<SkillSpec>;
  onClose: () => void;
  onSubmit: (values: SkillSpec) => void;
  onContentChange?: (content: string) => void;
}

export function SkillDrawer({
  open,
  editingSkill,
  form,
  onClose,
  onSubmit,
  onContentChange,
}: SkillDrawerProps) {
  const { t } = useTranslation();
  const [showMarkdown, setShowMarkdown] = useState(false);
  const [contentValue, setContentValue] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [aiRecommendations, setAiRecommendations] = useState<Array<{ categoryId: string; confidence: number; reason: string }>>([]);

  const categories = getEnabledCategories();

  const validateFrontmatter = useCallback(
    (_: unknown, value: string) => {
      const content = contentValue || value;
      if (!content || !content.trim()) {
        return Promise.reject(new Error(t("skills.pleaseInputContent")));
      }
      const fm = parseFrontmatter(content);
      if (!fm) {
        return Promise.reject(new Error(t("skills.frontmatterRequired")));
      }
      if (!fm.name) {
        return Promise.reject(new Error(t("skills.frontmatterNameRequired")));
      }
      if (!fm.description) {
        return Promise.reject(
          new Error(t("skills.frontmatterDescriptionRequired")),
        );
      }
      return Promise.resolve();
    },
    [contentValue, t],
  );

  useEffect(() => {
    if (editingSkill) {
      setContentValue(editingSkill.content);
      form.setFieldsValue({
        name: editingSkill.name,
        content: editingSkill.content,
      });
      // Auto-categorize and get AI recommendations
      const category = categorizeSkill({
        name: editingSkill.name,
        description: editingSkill.content,
        content: editingSkill.content,
      });
      setSelectedCategory(category);
      // AI recommendations would be called here if we had an API
    } else {
      setContentValue("");
      form.resetFields();
      setSelectedCategory("");
      setAiRecommendations([]);
    }
  }, [editingSkill, form]);

  const handleSubmit = (values: { name: string; content: string }) => {
    if (editingSkill) {
      message.warning(t("skills.editNotSupported"));
      onClose();
    } else {
      onSubmit({
        ...values,
        content: contentValue || values.content,
        source: "",
        path: "",
      });
    }
  };

  const handleContentChange = (content: string) => {
    setContentValue(content);
    form.setFieldsValue({ content });
    // Re-validate the content field to give real-time feedback
    form.validateFields(["content"]).catch(() => {});
    if (onContentChange) {
      onContentChange(content);
    }
  };

  return (
    <Drawer
      width={520}
      placement="right"
      title={editingSkill ? t("skills.viewSkill") : t("skills.createSkill")}
      open={open}
      onClose={onClose}
      destroyOnClose
    >
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        {!editingSkill && (
          <>
            <Form.Item
              name="name"
              label="Name"
              rules={[{ required: true, message: t("skills.pleaseInputName") }]}
            >
              <Input placeholder={t("skills.skillNamePlaceholder")} />
            </Form.Item>

            <Form.Item
              name="content"
              label="Content"
              rules={[{ required: true, validator: validateFrontmatter }]}
            >
              <MarkdownCopy
                content={contentValue}
                showMarkdown={showMarkdown}
                onShowMarkdownChange={setShowMarkdown}
                editable={true}
                onContentChange={handleContentChange}
                textareaProps={{
                  placeholder: t("skills.contentPlaceholder"),
                  rows: 12,
                }}
              />
            </Form.Item>

            <Form.Item>
              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: 8,
                  marginTop: 16,
                }}
              >
                <Button onClick={onClose}>{t("common.cancel")}</Button>
                <Button type="primary" htmlType="submit">
                  {t("skills.create")}
                </Button>
              </div>
            </Form.Item>
          </>
        )}

        {editingSkill && (
          <>
            <Form.Item name="name" label="name">
              <Input disabled />
            </Form.Item>

            <Form.Item
              label="分类"
              extra="AI 推荐分类，可手动调整"
            >
              <Select
                value={selectedCategory}
                onChange={setSelectedCategory}
                options={categories.map(cat => ({
                  label: `${cat.icon} ${cat.name}`,
                  value: cat.id,
                }))}
                style={{ width: "100%" }}
              />
              {aiRecommendations.length > 0 && (
                <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
                  <strong>AI 推荐：</strong>
                  {aiRecommendations.map((rec, i) => (
                    <div key={rec.categoryId}>
                      {i + 1}. {categories.find(c => c.id === rec.categoryId)?.name} 
                      ({rec.confidence}% 匹配) - {rec.reason}
                    </div>
                  ))}
                </div>
              )}
            </Form.Item>

            <Form.Item name="content" label="Content">
              <MarkdownCopy
                content={editingSkill.content}
                showMarkdown={showMarkdown}
                onShowMarkdownChange={setShowMarkdown}
                textareaProps={{
                  disabled: true,
                  rows: 12,
                }}
              />
            </Form.Item>

            <Form.Item name="source" label="Source">
              <Input disabled />
            </Form.Item>

            <Form.Item name="path" label="Path">
              <Input disabled />
            </Form.Item>

            <div
              style={{
                padding: 12,
                backgroundColor: "#fffbe6",
                border: "1px solid #ffe58f",
                borderRadius: 4,
                marginTop: 16,
              }}
            >
              <p style={{ margin: 0, fontSize: 12, color: "#8c8c8c" }}>
                {t("skills.editNote")}
              </p>
            </div>
          </>
        )}
      </Form>
    </Drawer>
  );
}
