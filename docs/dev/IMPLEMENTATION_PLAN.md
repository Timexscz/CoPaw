# CoPaw 分类管理系统 - 前端待创建文件清单

## 已完成后端部分 ✅

- [x] 数据库迁移文件 (`src/copaw/db/migrations/001_categories.sql`)
- [x] 数据库连接模块 (`src/copaw/db/database.py`)
- [x] 数据访问层 (`src/copaw/db/repositories/`)
- [x] 业务逻辑层 (`src/copaw/services/`)
- [x] Python 分类配置 (`src/copaw/config/`)
- [x] API 路由 (`src/copaw/app/routers/categories.py`)
- [x] Skills 详情 API (`src/copaw/app/routers/skills.py` 增强)

## 待创建前端文件 📝

### 1. API 类型定义
```typescript
// console/src/api/types/category.ts
export interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  keywords: string[];
  priority: number;
  is_custom: boolean;
  is_enabled: boolean;
  category_type: 'skill' | 'mcp';
  matcher_type?: 'keyword' | 'transport';
  matcher_config?: any;
}
```

### 2. API 模块
```typescript
// console/src/api/modules/categories.ts
export const categoriesApi = {
  getSkillCategories: (enabledOnly = true) => ...,
  getMCPCategories: (enabledOnly = true) => ...,
  createSkillCategory: (category) => ...,
  reorderSkillCategories: (categoryIds) => ...,
  // ... 更多方法
};
```

### 3. Skills 页面组件
```typescript
// console/src/pages/Agent/Skills/components/CategoryManager.tsx
// console/src/pages/Agent/Skills/components/SkillDetail.tsx
// console/src/pages/Agent/Skills/hooks/useSkillCategories.ts
```

### 4. MCP 页面组件
```typescript
// console/src/pages/Agent/MCP/components/MCPCategoryManager.tsx
// console/src/pages/Agent/MCP/hooks/useMCPCategories.ts
```

### 5. Markdown 渲染组件
```typescript
// console/src/components/MarkdownRenderer/index.tsx
// console/src/components/MarkdownRenderer/index.module.less
```

### 6. 样式文件
```less
// console/src/pages/Agent/Skills/components/CategoryManager.module.less
// console/src/pages/Agent/Skills/components/SkillDetail.module.less
```

## 安装依赖

### 后端
```bash
pip install asyncpg redis asyncpg redis pydantic python-frontmatter markdown
```

### 前端
```bash
cd console
npm install react-markdown remark-gfm rehype-highlight highlight.js
```

## 启动步骤

1. **启动数据库**
```bash
docker-compose up -d postgres redis
```

2. **初始化数据库**
```bash
docker exec -it <postgres_container> psql -U copaw -c "CREATE DATABASE copaw"
docker-compose restart postgres
```

3. **启动后端**
```bash
python -m uvicorn src.copaw.app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **启动前端**
```bash
cd console
npm run dev
```

## API 端点列表

### 分类管理
- `GET /api/categories/skills` - 获取技能分类
- `GET /api/categories/mcp` - 获取 MCP 分类
- `POST /api/categories/skills` - 创建技能分类
- `POST /api/categories/mcp` - 创建 MCP 分类
- `PUT /api/categories/skills/reorder` - 调整技能分类顺序
- `PUT /api/categories/mcp/reorder` - 调整 MCP 分类顺序
- `DELETE /api/categories/skills/{id}` - 删除技能分类
- `DELETE /api/categories/mcp/{id}` - 删除 MCP 分类
- `PATCH /api/categories/skills/{id}/toggle` - 切换技能分类状态
- `PATCH /api/categories/mcp/{id}/toggle` - 切换 MCP 分类状态

### 技能分类映射
- `POST /api/categories/skills/{name}/category` - 设置技能分类
- `GET /api/categories/skills/{name}/category` - 获取技能分类
- `POST /api/categories/skills/batch/categorize` - 批量获取技能分类

### 技能详情
- `GET /api/skills/{name}/detail` - 获取技能详情（含 Markdown）

## 下一步

1. 创建前端 API 类型和模块
2. 创建分类管理 UI 组件
3. 创建 Markdown 渲染组件
4. 集成到现有 Skills/MCP 页面
5. 测试和优化
