# 数据库配置指南

## 📋 环境配置文件

已创建 `.env` 文件在 `/root/CoPaw/.env`

### 默认配置

```bash
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=copaw
DATABASE_PASSWORD=copaw_password
DATABASE_NAME=copaw

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Application Configuration
WORKING_DIR=./working_dir
```

## 🔧 配置方式

### 方式 1: 使用 .env 文件（推荐）

编辑 `/root/CoPaw/.env` 文件，修改数据库配置：

```bash
DATABASE_HOST=your-db-host
DATABASE_PORT=5432
DATABASE_USER=your-username
DATABASE_PASSWORD=your-password
DATABASE_NAME=your-database
```

### 方式 2: 系统环境变量

```bash
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DATABASE_USER=copaw
export DATABASE_PASSWORD=copaw_password
export DATABASE_NAME=copaw

export REDIS_HOST=localhost
export REDIS_PORT=6379
```

### 方式 3: Docker 环境变量

```bash
docker run -d \
  -e DATABASE_HOST=postgres \
  -e DATABASE_PORT=5432 \
  -e DATABASE_USER=copaw \
  -e DATABASE_PASSWORD=copaw_password \
  -e DATABASE_NAME=copaw \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  copaw:latest
```

## 🗄️ 数据库初始化

### 1. 创建数据库

```bash
# 连接到 PostgreSQL
psql -h localhost -U copaw -d postgres

# 创建数据库
CREATE DATABASE copaw;

# 或使用 docker
docker exec -it <postgres_container> psql -U copaw -c "CREATE DATABASE copaw"
```

### 2. 运行迁移

迁移文件会自动执行：
- `/root/CoPaw/src/copaw/db/migrations/001_categories.sql`

或手动执行：
```bash
psql -h localhost -U copaw -d copaw -f /root/CoPaw/src/copaw/db/migrations/001_categories.sql
```

### 3. 验证

```bash
# 连接到数据库
psql -h localhost -U copaw -d copaw

# 查看表
\dt

# 查看分类数据
SELECT * FROM categories;
```

## 🔍 验证配置

### Python 验证

```python
from copaw.db.database import settings, db

# 打印配置
print(f"Database: {settings.database.url}")
print(f"Redis: {settings.redis.host}:{settings.redis.port}")

# 测试连接
import asyncio

async def test():
    await db.connect()
    print("✅ Database connection successful!")
    await db.disconnect()

asyncio.run(test())
```

### 命令行验证

```bash
# 测试 PostgreSQL 连接
psql -h localhost -U copaw -d copaw -c "SELECT 1"

# 测试 Redis 连接
redis-cli ping
```

## 🐛 常见问题

### 1. 连接失败

**错误**: `could not connect to server`

**解决**:
```bash
# 检查 PostgreSQL 是否运行
docker ps | grep postgres

# 或检查本地服务
pg_isready -h localhost -p 5432
```

### 2. 认证失败

**错误**: `password authentication failed`

**解决**:
```bash
# 重置密码
docker exec -it <postgres_container> psql -U postgres -c "ALTER USER copaw WITH PASSWORD 'new_password';"
```

### 3. 数据库不存在

**错误**: `database "copaw" does not exist`

**解决**:
```bash
docker exec -it <postgres_container> psql -U copaw -c "CREATE DATABASE copaw;"
```

### 4. .env 文件未加载

**检查**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv('DATABASE_HOST'))
```

## 📝 配置说明

| 变量 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `DATABASE_HOST` | PostgreSQL 主机地址 | localhost | ✅ |
| `DATABASE_PORT` | PostgreSQL 端口 | 5432 | ✅ |
| `DATABASE_USER` | 数据库用户名 | copaw | ✅ |
| `DATABASE_PASSWORD` | 数据库密码 | copaw_password | ✅ |
| `DATABASE_NAME` | 数据库名称 | copaw | ✅ |
| `REDIS_HOST` | Redis 主机地址 | localhost | ✅ |
| `REDIS_PORT` | Redis 端口 | 6379 | ✅ |
| `REDIS_PASSWORD` | Redis 密码 | (空) | ❌ |
| `WORKING_DIR` | 工作目录 | ./working_dir | ❌ |

## 🔐 安全建议

1. **生产环境**: 使用强密码
2. **不要提交**: `.env` 文件应加入 `.gitignore`
3. **使用示例**: 提交 `.env.example` 作为模板
4. **权限控制**: 限制数据库用户权限

## 📚 相关文件

- 环境配置：`/root/CoPaw/.env`
- 配置示例：`/root/CoPaw/.env.example`
- 数据库连接：`/root/CoPaw/src/copaw/db/database.py`
- 迁移文件：`/root/CoPaw/src/copaw/db/migrations/001_categories.sql`
