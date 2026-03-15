/**
 * Category Manager Component for MCP
 */

import { useState } from 'react';
import { Modal, Form, Input, Button, Table, Switch, Popconfirm, message, Select } from '@agentscope-ai/design';
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  UpOutlined,
  DownOutlined,
} from '@ant-design/icons';
import { useMCPCategories } from '../hooks/useMCPCategories';
import type { Category } from '../../../../api/types/category';
import styles from './MCPCategoryManager.module.less';

interface MCPCategoryManagerProps {
  open: boolean;
  onClose: () => void;
}

interface CategoryFormValues {
  name: string;
  icon: string;
  color: string;
  matcherType: 'transport' | 'keyword';
  transport?: string[];
  keywords?: string;
}

export function MCPCategoryManager({ open, onClose }: MCPCategoryManagerProps) {
  const { categories, loading, createCategory, deleteCategory, toggleCategory, reorderCategories } = useMCPCategories();
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm<CategoryFormValues>();

  const handleAdd = () => {
    setEditingCategory(null);
    form.resetFields();
    form.setFieldsValue({
      icon: '🔌',
      color: '#1890ff',
      matcherType: 'keyword',
    });
    setIsModalOpen(true);
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    form.setFieldsValue({
      name: category.name,
      icon: category.icon,
      color: category.color,
      matcherType: category.matcher_type || 'keyword',
      keywords: category.keywords?.join(', ') || '',
    });
    setIsModalOpen(true);
  };

  const handleSave = async (values: CategoryFormValues) => {
    if (!editingCategory) {
      try {
        if (values.matcherType === 'transport') {
          await createCategory({
            id: `custom_${Date.now()}`,
            name: values.name,
            icon: values.icon,
            color: values.color,
            keywords: [],
            priority: 0,
            is_enabled: true,
            category_type: 'mcp',
            matcher_type: 'transport',
            matcher_config: {
              transport: values.transport,
            },
          });
        } else {
          const keywords = (values.keywords || '')
            .split(',')
            .map(k => k.trim())
            .filter(k => k.length > 0);
          
          await createCategory({
            id: `custom_${Date.now()}`,
            name: values.name,
            icon: values.icon,
            color: values.color,
            keywords,
            priority: 0,
            is_enabled: true,
            category_type: 'mcp',
            matcher_type: 'keyword',
            matcher_config: {
              keywords,
            },
          });
        }
        message.success('分类已添加');
        setIsModalOpen(false);
      } catch (error) {
        message.error('添加分类失败');
      }
    } else {
      message.warning('内置分类不支持编辑，请创建自定义分类');
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
      title: '匹配方式',
      dataIndex: 'matcher_type',
      key: 'matcher_type',
      width: 120,
      render: (_: string, record: Category) => {
        if (record.id === 'local' || record.id === 'remote_http' || record.id === 'remote_sse') {
          return <span className={styles.matcherType}>传输方式</span>;
        }
        return <span className={styles.matcherType}>关键词匹配</span>;
      },
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
        title="MCP 分类管理"
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
              <li>传输方式分类：local (stdio), remote_http (streamable_http), remote_sse (sse)</li>
              <li>关键词分类：匹配 MCP 客户端的名称和描述</li>
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
            <Input placeholder="例如：数据库" />
          </Form.Item>

          <Form.Item
            name="icon"
            label="图标"
            rules={[{ required: true, message: '请输入图标' }]}
          >
            <Input placeholder="例如：🗄️" style={{ width: 100 }} />
          </Form.Item>

          <Form.Item
            name="color"
            label="颜色"
            rules={[{ required: true, message: '请选择颜色' }]}
          >
            <Input type="color" style={{ width: 100 }} />
          </Form.Item>

          <Form.Item
            name="matcherType"
            label="匹配方式"
            rules={[{ required: true, message: '请选择匹配方式' }]}
            initialValue="keyword"
          >
            <Select
              options={[
                { label: '关键词匹配', value: 'keyword' },
                { label: '传输方式', value: 'transport' },
              ]}
            />
          </Form.Item>

          <Form.Item noStyle shouldUpdate>
            {({ getFieldValue }) => {
              const matcherType = getFieldValue('matcherType');
              
              if (matcherType === 'transport') {
                return (
                  <Form.Item
                    name="transport"
                    label="传输方式"
                    rules={[{ required: true, message: '请选择传输方式' }]}
                    extra="选择此分类匹配的传输方式"
                  >
                    <Select
                      mode="multiple"
                      placeholder="选择传输方式"
                      options={[
                        { label: 'stdio (本地)', value: 'stdio' },
                        { label: 'streamable_http (HTTP)', value: 'streamable_http' },
                        { label: 'sse (SSE)', value: 'sse' },
                      ]}
                    />
                  </Form.Item>
                );
              }
              
              return (
                <Form.Item
                  name="keywords"
                  label="关键词"
                  rules={[{ required: true, message: '请输入关键词' }]}
                  extra="用逗号分隔，例如：postgres, mysql, database"
                >
                  <Input.TextArea
                    rows={4}
                    placeholder="输入匹配此分类的关键词"
                  />
                </Form.Item>
              );
            }}
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
