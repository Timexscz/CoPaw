# CoPaw 源码安装指南

## ✅ 安装状态：已完成

---

## 📋 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/agentscope-ai/CoPaw.git
cd CoPaw
```

### 2. 构建前端

```bash
cd console && npm ci && npm run build
cd ..
```

### 3. 复制前端构建产物

```bash
mkdir -p src/copaw/console
cp -R console/dist/. src/copaw/console/
```

### 4. 安装 Python 包

```bash
pip install -e .
```

这将自动安装以下依赖：
- ✅ `asyncpg>=0.28.0` - PostgreSQL 驱动
- ✅ `redis>=5.0.0` - Redis 客户端
- ✅ `pydantic>=2.0.0` - 配置验证
- ✅ `pydantic-settings` - 设置管理
- ✅ `python-frontmatter>=1.0.0` - Markdown Front Matter 解析
- ✅ `markdown>=3.4.0` - Markdown 处理
- ✅ `python-dotenv>=1.0.0` - 环境变量加载

### 5. 验证安装

```bash
python verify_install.py
```

预期输出：
```
✅ asyncpg: OK
✅ redis: OK
✅ pydantic: OK
✅ pydantic-settings: OK
✅ python-frontmatter: OK
✅ markdown: OK
✅ python-dotenv: OK

✅ Database module: OK
✅ CategoryService: OK
✅ SkillParser: OK
✅ CategoryRepository: OK

✅ All checks passed! CoPaw is ready to use.
```

---

## 🔧 配置数据库

### 方式 1: 编辑 .env 文件

编辑 `/root/CoPaw/.env` 文件：

```bash
DATABASE_HOST=your-db-host
DATABASE_PORT=5432
DATABASE_USER=your-username
DATABASE_PASSWORD=your-password
DATABASE_NAME=your-database

REDIS_HOST=your-redis-host
REDIS_PORT=6379
```

### 方式 2: 使用环境变量

```bash
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_USER=copaw
export DATABASE_PASSWORD=copaw_password
export DATABASE_NAME=copaw

export REDIS_HOST=localhost
export REDIS_PORT=6379
```

---

## 🗄️ 初始化数据库

### 1. 创建数据库（如果不存在）

```bash
psql -h $DATABASE_HOST -U $DATABASE_USER -d postgres -c "CREATE DATABASE $DATABASE_NAME"
```

### 2. 运行迁移

迁移会在首次连接时自动执行：
- `src/copaw/db/migrations/001_categories.sql`

或手动执行：
```bash
psql -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME \
  -f src/copaw/db/migrations/001_categories.sql
```

### 3. 验证

```bash
psql -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME -c "SELECT * FROM categories LIMIT 1"
```

---

## 🚀 启动应用

### 1. 初始化配置

```bash
copaw init --defaults
```

### 2. 启动应用

```bash
copaw app
```

### 3. 访问

- **Console UI**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs

---

## 🐛 故障排查

### 问题 1: pydantic 导入错误

**错误**:
```
pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package
```

**解决**:
```bash
pip install pydantic-settings
```

### 问题 2: 数据库连接失败

**错误**:
```
could not connect to server
```

**检查**:
```bash
# 检查 PostgreSQL
pg_isready -h $DATABASE_HOST -p $DATABASE_PORT

# 检查 Redis
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping
```

### 问题 3: 前端构建失败

**错误**:
```
npm ERR! code ENOENT
```

**解决**:
```bash
cd console
npm ci
npm run build
cd ..
```

### 问题 4: 权限问题

**错误**:
```
Permission denied
```

**解决**:
```bash
# 使用 --user 标志
pip install -e . --user

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate
pip install -e .
```

---

## 📚 相关文件

- 环境配置：`.env`
- 配置示例：`.env.example`
- 依赖配置：`pyproject.toml`
- 数据库迁移：`src/copaw/db/migrations/001_categories.sql`
- 验证脚本：`verify_install.py`

---

## 📖 文档链接

- [快速开始](https://copaw.agentscope.io/docs/quickstart)
- [数据库配置](DATABASE_CONFIG.md)
- [项目完成总结](PROJECT_COMPLETE.md)

---

**更新时间**: 2026-03-08  
**状态**: ✅ 验证通过
