/**
 * Category Manager Component for Skills
 */

import { useState } from 'react';
import { Modal, Form, Input, Button, Table, Switch, Popconfirm, message } from '@agentscope-ai/design';
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  UpOutlined,
  DownOutlined,
} from '@ant-design/icons';
import { useSkillCategories } from '../hooks/useSkillCategories';
import type { Category } from '../../../../api/types/category';
import styles from './CategoryManager.module.less';

interface CategoryManagerProps {
  open: boolean;
  onClose: () => void;
}

interface CategoryFormValues {
  name: string;
  icon: string;
  color: string;
  keywords: string;
}

export function CategoryManager({ open, onClose }: CategoryManagerProps) {
  const { categories, loading, createCategory, deleteCategory, toggleCategory, reorderCategories } = useSkillCategories();
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm<CategoryFormValues>();

  const handleAdd = () => {
    setEditingCategory(null);
    form.resetFields();
    form.setFieldsValue({
      icon: '📁',
      color: '#1890ff',
    });
    setIsModalOpen(true);
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    form.setFieldsValue({
      name: category.name,
      icon: category.icon,
      color: category.color,
      keywords: category.keywords.join(', '),
    });
    setIsModalOpen(true);
  };

  const handleSave = async (values: CategoryFormValues) => {
    const keywords = values.keywords
      .split(',')
      .map(k => k.trim())
      .filter(k => k.length > 0);

    if (editingCategory) {
      message.warning('内置分类不支持编辑，请创建自定义分类');
    } else {
      try {
        await createCategory({
          id: `custom_${Date.now()}`,
          name: values.name,
          icon: values.icon,
          color: values.color,
          keywords,
          priority: 0,
          is_enabled: true,
          category_type: 'skill',
        });
        message.success('分类已添加');
        setIsModalOpen(false);
      } catch (error) {
        message.error('添加分类失败');
      }
    }
  };

  const handleDelete = async (categoryId: string) => {
    try {
      await deleteCategory(categoryId);
      message.success('分类已删除');
    } catch (error) {
      message.error('删除分类失败');
    }
  };

  const handleToggle = async (categoryId: string) => {
    try {
      await toggleCategory(categoryId);
      message.success('分类状态已更新');
    } catch (error) {
      message.error('更新状态失败');
    }
  };

  const handleMoveUp = async (index: number) => {
    if (index === 0) return;
    const newCategories = [...categories];
    [newCategories[index], newCategories[index - 1]] = [newCategories[index - 1], newCategories[index]];
    const categoryIds = newCategories.map(c => c.id);
    await reorderCategories(categoryIds);
  };

  const handleMoveDown = async (index: number) => {
    if (index === categories.length - 1) return;
    const newCategories = [...categories];
    [newCategories[index], newCategories[index + 1]] = [newCategories[index + 1], newCategories[index]];
    const categoryIds = newCategories.map(c => c.id);
    await reorderCategories(categoryIds);
  };

  const columns = [
    {
      title: '排序',
      dataIndex: 'priority',
      key: 'sort',
      width: 80,
      render: (_: unknown, __: Category, index: number) => (
        <div className={styles.sortButtons}>
          <Button
            type="text"
            size="small"
            icon={<UpOutlined />}
            onClick={() => handleMoveUp(index)}
            disabled={index === 0}
          />
          <Button
            type="text"
            size="small"
            icon={<DownOutlined />}
            onClick={() => handleMoveDown(index)}
            disabled={index === categories.length - 1}
          />
        </div>
      ),
    },
    {
      title: '分类',
      dataIndex: 'name',
      key: 'name',
      render: (_: unknown, record: Category) => (
        <span>
          {record.icon} {record.name}
          {record.is_custom && (
            <span className={styles.customBadge}>自定义</span>
          )}
        </span>
      ),
    },
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
      render: (keywords: string[]) => (
        <span className={styles.keywords}>
          {keywords.slice(0, 3).join(', ')}
          {keywords.length > 3 && '...'}
        </span>
      ),
    },
    {
      title: '启用',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      width: 80,
      render: (isEnabled: boolean, record: Category) => (
        <Switch
          checked={isEnabled}
          onChange={() => handleToggle(record.id)}
          size="small"
        />
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: unknown, record: Category) => (
        <div className={styles.actionButtons}>
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            disabled={!record.is_custom}
          />
          <Popconfirm
            title="确定要删除此分类吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="删除"
            cancelText="取消"
          >
            <Button
              type="text"
              size="small"
              danger
              icon={<DeleteOutlined />}
              disabled={!record.is_custom}
            />
          </Popconfirm>
        </div>
      ),
    },
  ];

  return (
    <>
      <Modal
        title="分类管理"
        open={open}
        onCancel={onClose}
        footer={
          <div>
            <Button onClick={onClose}>关闭</Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              添加分类
            </Button>
          </div>
        }
        width={800}
      >
        <div className={styles.managerContainer}>
          <div className={styles.tips}>
            <p>💡 提示：</p>
            <ul>
              <li>使用 ↑ ↓ 按钮调整分类顺序（优先级）</li>
              <li>只有自定义分类可以编辑和删除</li>
              <li>禁用的分类不会在列表中显示</li>
              <li>关键词用逗号分隔，匹配技能名称、描述或内容</li>
            </ul>
          </div>
          <Table
            columns={columns}
            dataSource={categories}
            rowKey="id"
            pagination={false}
            size="small"
            loading={loading}
          />
        </div>
      </Modal>

      <Modal
        title={editingCategory ? '编辑分类' : '添加分类'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        okText="保存"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
        >
          <Form.Item
            name="name"
            label="分类名称"
            rules={[{ required: true, message: '请输入分类名称' }]}
          >
            <Input placeholder="例如：文档处理" />
          </Form.Item>

          <Form.Item
            name="icon"
            label="图标"
            rules={[{ required: true, message: '请输入图标' }]}
          >
            <Input placeholder="例如：📄" style={{ width: 100 }} />
          </Form.Item>

          <Form.Item
            name="color"
            label="颜色"
            rules={[{ required: true, message: '请选择颜色' }]}
          >
            <Input type="color" style={{ width: 100 }} />
          </Form.Item>

          <Form.Item
            name="keywords"
            label="关键词"
            rules={[{ required: true, message: '请输入关键词' }]}
            extra="用逗号分隔，例如：docx, word, document, pdf"
          >
            <Input.TextArea
              rows={4}
              placeholder="输入匹配此分类的关键词"
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
