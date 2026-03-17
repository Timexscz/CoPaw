<div align="center">

# CoPaw-CE (Community Edition)

[![GitHub 仓库](https://img.shields.io/badge/GitHub-仓库-black.svg?logo=github)](https://github.com/Timexscz/CoPaw)
[![版本](https://img.shields.io/badge/version-v0.0.6.ce.1-blue.svg)](https://github.com/Timexscz/CoPaw/releases)
[![基于](https://img.shields.io/badge/基于-v0.0.5.post1-green.svg)](https://github.com/agentscope-ai/CoPaw)
[![Python 版本](https://img.shields.io/badge/python-3.10%20~%20%3C3.14-blue.svg?logo=python&label=Python)](https://www.python.org/downloads/)
[![许可证](https://img.shields.io/badge/license-Apache%202.0-red.svg?logo=apache&label=%E8%AE%B8%E5%8F%AF%E8%AF%81)](LICENSE)
[![测试](https://img.shields.io/badge/tests-56%20passed-green.svg)](https://github.com/Timexscz/CoPaw/actions)

[[English](README.md)] [[日本語](README_ja.md)] | [官方文档](https://copaw.agentscope.io/) | [官方仓库](https://github.com/agentscope-ai/CoPaw)

<p align="center">
  <img src="https://img.alicdn.com/imgextra/i2/O1CN014TIqyO1U5wDiSbFfA_!!6000000002467-2-tps-816-192.png" alt="CoPaw Logo" width="120">
</p>

<p align="center"><b>懂你所需，伴你左右 — 社区增强版</b></p>

<p align="center">
  <strong>🔐 认证系统</strong> • 
  <strong>📂 MCP 分类管理</strong> • 
  <strong>🛠️ Skills 分类管理</strong> • 
  <strong>🎨 主题切换</strong> • 
  <strong>📚 文档优化</strong>
</p>

</div>

## 🎉 发布说明

**[2026-03-14] v0.0.6.ce.1 发布**

这是 CoPaw 的社区增强版本，包含以下改进（本版本包含超过600，000行新增代码，由人-Ai协作完成（主要感谢qwen-coding-planning））：

### 新增功能
- 🔐 **完整的认证系统** - JWT 认证，保护 API 访问（可选启用）
- 📂 **MCP 客户端分类管理** - 智能分类：数据库、文件系统、API 集成、AI 服务等
- 🛠️ **Skills 技能分类管理** - 分类：文档处理、自动化、浏览器、通讯工具等
- 🎨 **主题切换** - 支持深色/浅色模式
- 📚 **文档结构优化** - 统一索引 INDEX.md，精简 40%

### 测试与质量
- ✅ **56 个测试全部通过** (100% 覆盖率)
- ✅ **修复所有弃用警告** (Pydantic V2、datetime、Redis)
- ✅ **异步集成测试完善** - 使用真实数据库验证

### 优化
- 📁 根目录文档精简 40%
- 📖 创建统一文档索引
- 🔧 代码质量提升，符合最新标准

---

## 目录

> **推荐阅读：**
>
> - **我想三条命令跑起来**： [快速开始](#快速开始) → 浏览器打开控制台。
> - **我想在钉钉 / 飞书 / QQ 里聊**：在控制台中进行 [频道配置](https://copaw.agentscope.io/docs/channels)。
> - **我不想装 Python**：[一键安装](#一键安装 beta 持续完善中) 自动管理 Python，或使用 [魔搭一键配置](https://modelscope.cn/studios/fork?target=AgentScope/CoPaw) 云端部署。

---

## 目录

- [快速开始](#快速开始)
- [数据库配置](#数据库配置)
- [核心功能](#核心功能)
- [CLI 工具](#cli-工具)
- [版本控制](#版本控制)
- [主题切换](#主题切换)
- [认证系统](#认证系统)
- [API Key 配置](#api-key-配置)
- [本地模型](#本地模型)
- [文档导航](#文档导航)
- [常见问题](#常见问题)
  - [认证系统](#1-如何启用认证系统)
  - [MCP/Skills](#2-mcpskills-分类如何使用)
  - [主题切换](#3-如何切换主题)
  - [版本控制](#4-如何检查技能更新)
  - [MCP 故障排除](#5-mcp-客户端无法启动)
  - [配置备份](#6-如何备份和恢复配置)
  - [测试运行](#7-测试如何运行)
  - [Docker 部署](#8-docker-部署)
  - [数据库安装](#9-如何安装-postgresql-和-redis)
  - [数据库连接](#10-数据库连接失败怎么办)
  - [数据库备份](#11-如何备份数据库)
- [参与贡献](#参与贡献)

---

## 快速开始

### 从源码部署

**前提条件**: Python 3.10-3.13, Git, PostgreSQL, Redis

```bash
1. 克隆仓库
git clone https://github.com/Timexscz/CoPaw.git
cd CoPaw

2. 前端控制台（Web 界面必需）
cd console && npm install && npm run build
cd ..

3. 安装依赖
pip install -e ".[dev]"

4. 将控制台构建产物复制到包目录
mkdir -p src/copaw/console
cp -R console/dist/. src/copaw/console/

5. 初始化配置
copaw init --defaults

6. 启动服务
copaw app
```

启动后，在浏览器打开 **http://127.0.0.1:8088/** 即可使用控制台。

> **注意**: 这是社区增强版 (v0.0.6.ce.1)，基于官方 CoPaw v0.0.5.post1 构建。

---

## 数据库配置

CoPaw 使用 **PostgreSQL** 作为主数据库，**Redis** 作为缓存和会话存储。

### 🗄️ PostgreSQL 配置

**环境变量**（在 `.env` 文件中配置）：
```bash
# 数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=copaw
DATABASE_PASSWORD=copaw_password
DATABASE_NAME=copaw
```

**Docker 快速启动 PostgreSQL**：
```bash
docker run -d \
  --name copaw-postgres \
  -e POSTGRES_USER=copaw \
  -e POSTGRES_PASSWORD=copaw_password \
  -e POSTGRES_DB=copaw \
  -p 5432:5432 \
  postgres:15
```

**手动安装 PostgreSQL**：
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@15

# 初始化数据库
createdb copaw
```

---

### 🔴 Redis 配置

**环境变量**（在 `.env` 文件中配置）：
```bash
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

**Docker 快速启动 Redis**：
```bash
docker run -d \
  --name copaw-redis \
  -p 6379:6379 \
  redis:7
```

**手动安装 Redis**：
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# 启动 Redis
redis-server
```

---

### 🔧 数据库初始化

**方式 1: 自动初始化**
```bash
# 使用 init 命令自动创建数据库表
copaw init --defaults
```

**方式 2: 手动执行迁移**
```bash
# 连接到数据库
psql -h localhost -U copaw -d copaw

# 运行迁移
psql -h localhost -U copaw -d copaw \
  -f src/copaw/db/migrations/001_categories.sql
```

---

### 🔍 验证连接

**测试 PostgreSQL**：
```bash
psql -h localhost -U copaw -d copaw -c "SELECT 1"
```

**测试 Redis**：
```bash
redis-cli ping
# 期望输出：PONG
```

**Python 验证**：
```bash
python -c "from copaw.db.database import db; import asyncio; asyncio.run(db.connect())"
```

---

### 📊 配置参数说明

| 变量 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `DATABASE_HOST` | PostgreSQL 主机地址 | `localhost` | ✅ |
| `DATABASE_PORT` | PostgreSQL 端口 | `5432` | ✅ |
| `DATABASE_USER` | 数据库用户名 | `copaw` | ✅ |
| `DATABASE_PASSWORD` | 数据库密码 | `copaw_password` | ✅ |
| `DATABASE_NAME` | 数据库名称 | `copaw` | ✅ |
| `REDIS_HOST` | Redis 主机地址 | `localhost` | ✅ |
| `REDIS_PORT` | Redis 端口 | `6379` | ✅ |
| `REDIS_PASSWORD` | Redis 密码 | (空) | ❌ |

---

### 🐛 常见问题

**问题 1: 无法连接 PostgreSQL**
```bash
# 检查服务状态
docker ps | grep postgres
# 或
pg_isready -h localhost -p 5432
```

**问题 2: 认证失败**
```bash
# 重置密码
docker exec -it copaw-postgres psql -U postgres \
  -c "ALTER USER copaw WITH PASSWORD 'new_password';"
```

**问题 3: 数据库不存在**
```bash
docker exec -it copaw-postgres psql -U copaw \
  -c "CREATE DATABASE copaw;"
```

**问题 4: Redis 连接失败**
```bash
# 检查 Redis 是否运行
docker ps | grep redis
# 或
redis-cli ping
```

📖 [完整数据库配置指南](docs/dev/DATABASE_CONFIG.md)

---

## 核心功能

### 🔐 认证系统

CoPaw 支持 JWT 认证，保护 API 访问和 Web Console。

**启用认证**：
```bash
# 在 .env 文件中添加
AUTH_ENABLED=true
AUTH_ALLOW_REGISTRATION=true
```

**功能特性**：
- ✅ 用户注册/登录
- ✅ JWT Token 认证
- ✅ 可选启用/禁用
- ✅ 密码加密存储

📖 [详细配置指南](docs/auth/AUTH_GUIDE.md)

---

### 📂 MCP 客户端管理

MCP (Model Context Protocol) 提供模型上下文协议支持，扩展 AI 能力。

**支持的 MCP 类型**：
- 🔍 **搜索服务** - Tavily Search 等
- 📁 **文件系统** - 本地/远程文件访问
- 🗄️ **数据库** - PostgreSQL, MySQL 等
- 🌐 **API 集成** - GitHub, Weather 等

**CLI 管理命令**：
```bash
copaw mcp list              # 列出所有客户端
copaw mcp add <name>        # 添加新客户端
copaw mcp enable <name>     # 启用客户端
copaw mcp disable <name>    # 禁用客户端
copaw mcp interactive       # 交互式管理
```

📖 [MCP 完整指南](docs/mcp/MCP_COMPLETE_GUIDE.md)

---

### 🛠️ Skills 技能管理

Skills 定义 CoPaw 可以做什么，支持分类管理。

**技能分类**：
- 📄 **文档处理** - PDF, DOCX, PPTX, XLSX
- 🤖 **自动化** - Cron, 定时任务
- 🌐 **浏览器** - 网页浏览，信息提取
- 📰 **信息获取** - 新闻，天气，搜索
- 💬 **通讯工具** - 邮件，消息发送

**CLI 管理命令**：
```bash
copaw skills list           # 列出所有技能
copaw skills enable <name>  # 启用技能
copaw skills disable <name> # 禁用技能
copaw skills search <query> # 搜索 Hub 技能
copaw skills install <url>  # 安装新技能
copaw skills interactive    # 交互式管理
```

📖 [Skills 使用指南](docs/cli/SKILLS_CLI_GUIDE.md)

---

### 🎨 主题切换

支持深色/浅色模式切换，保护你的眼睛。

**切换方式**：
- 🖱️ **UI 按钮** - 点击控制台右上角主题按钮
- ⚙️ **系统偏好** - 自动跟随系统主题
- 💾 **持久化** - 主题偏好本地存储

**主题变量规范**：
```less
// 背景色
--theme-bg-base         // 基础背景
--theme-bg-container    // 容器背景
--theme-bg-elevated     // 浮层背景

// 文本色
--theme-text-primary    // 主文本
--theme-text-secondary  // 次级文本
--theme-text-tertiary   // 第三级文本

// 边框色
--theme-border-primary  // 主边框
--theme-border-secondary// 次级边框
```

📖 [主题实现细节](docs/theme/THEME_COMPLETE.md)

---

### 📊 版本控制

为 Skills、记忆文件和 MCP 客户端提供版本追踪能力。

#### Skills 版本控制

```bash
# 生成版本锁定文件
copaw skills version lock

# 检查更新
copaw skills version status

# 更新所有技能
copaw skills version update --all
```

#### 记忆文件版本控制

```bash
# 保存当前版本
copaw memory version save MEMORY.md

# 查看历史版本
copaw memory version list MEMORY.md

# 恢复历史版本
copaw memory version restore <version_path>

# 清理旧版本
copaw memory version cleanup
```

#### MCP 版本追踪

```bash
# 查看 MCP 客户端状态
copaw mcp version status

# 查看客户端详情
copaw mcp version info <client>

# 回滚到历史版本
copaw mcp version rollback <client> <version>

# 健康检查
copaw mcp version health-check
```

📖 [版本控制快速入门](docs/VERSION_CONTROL_QUICKSTART.md)  
📖 [版本控制完整指南](docs/VERSION_CONTROL_USER_GUIDE.md)

---

## CLI 工具

### 完整命令列表

```bash
# 应用管理
copaw init              # 初始化配置
copaw app               # 启动应用
copaw start             # 启动服务
copaw restart           # 重启服务
copaw stop              # 停止服务

# MCP 管理
copaw mcp list          # 列出客户端
copaw mcp add           # 添加客户端
copaw mcp remove        # 删除客户端
copaw mcp enable        # 启用客户端
copaw mcp disable       # 禁用客户端
copaw mcp info          # 查看详情
copaw mcp export        # 导出配置
copaw mcp import        # 导入配置
copaw mcp interactive   # 交互模式

# Skills 管理
copaw skills list       # 列出技能
copaw skills info       # 查看详情
copaw skills enable     # 启用技能
copaw skills disable    # 禁用技能
copaw skills config     # 交互配置
copaw skills search     # 搜索 Hub
copaw skills install    # 安装技能
copaw skills export     # 导出配置
copaw skills import     # 导入配置
copaw skills interactive# 交互模式

# 版本控制
copaw skills version lock      # 锁定技能版本
copaw skills version status    # 检查更新
copaw skills version update    # 更新技能
copaw memory version save      # 保存记忆版本
copaw memory version list      # 查看历史
copaw memory version restore   # 恢复版本
copaw mcp version status       # MCP 状态
copaw mcp version info         # MCP 详情
copaw mcp version rollback     # MCP 回滚

# 其他
copaw logs              # 查看日志
copaw --help            # 查看帮助
```

📖 [CLI 快速参考](docs/cli/CLI_QUICK_REFERENCE.md)

---

## 认证系统

### 快速配置

**方式 1: 环境变量**
```bash
# 在 .env 文件中添加
AUTH_ENABLED=true
AUTH_ALLOW_REGISTRATION=true
AUTH_JWT_SECRET_KEY=your-secret-key
AUTH_JWT_EXPIRATION_MINUTES=1440
```

**方式 2: config.json**
```json
{
  "auth": {
    "enabled": true,
    "allow_registration": true
  }
}
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/logout` | POST | 用户登出 |
| `/api/auth/me` | GET | 获取当前用户 |
| `/api/auth/status` | GET | 认证状态 |

### 安全建议

1. 🔒 **生产环境** - 设置强 `AUTH_JWT_SECRET_KEY`
2. 🔐 **HTTPS** - 使用 HTTPS 保护传输
3. 🛡️ **密码策略** - 至少 8 位，包含大小写字母和数字
4. 🔄 **定期更新** - 定期更新 JWT 密钥和用户密码

📖 [认证配置完整指南](docs/auth/AUTH_GUIDE.md)

---

## API Key 配置

若使用**云端大模型**，需要配置 API Key。

**配置方式**:
1. **控制台** - 打开 http://127.0.0.1:8088/ → **设置** → **模型**
2. **环境变量** - 在 `.env` 文件中设置 `DASHSCOPE_API_KEY`

> **仅用本地模型？** 若使用本地模型，则**无需**任何 API Key。

---

## 本地模型

CoPaw 支持本地运行大模型，无需 API Key。

| 后端 | 适用场景 | 安装 |
|------|---------|------|
| **llama.cpp** | 跨平台 | `pip install llama-cpp-python` |
| **MLX** | Apple Silicon | `pip install mlx-lm` |
| **Ollama** | 跨平台 | 需运行 Ollama 服务 |

---

## 文档导航

### 📖 核心文档

| 文档 | 说明 |
|------|------|
| [INDEX.md](INDEX.md) | 📍 统一文档索引 |
| [README.md](README.md) | 项目主文档（英文） |
| [README_ja.md](README_ja.md) | 项目主文档（日文） |

### 🛠️ 开发文档

| 文档 | 说明 |
|------|------|
| [docs/CONTRIBUTING_zh.md](docs/CONTRIBUTING_zh.md) | 贡献者指南 |
| [docs/TESTING.md](docs/TESTING.md) | 测试指南 |
| [docs/DEPRECATION_FIXES.md](docs/DEPRECATION_FIXES.md) | 弃用修复报告 |

### 📚 功能文档

| 分类 | 文档 |
|------|------|
| **认证系统** | [docs/auth/AUTH_GUIDE.md](docs/auth/AUTH_GUIDE.md) |
| **MCP 管理** | [docs/mcp/MCP_COMPLETE_GUIDE.md](docs/mcp/MCP_COMPLETE_GUIDE.md) |
| **Skills 管理** | [docs/cli/SKILLS_CLI_GUIDE.md](docs/cli/SKILLS_CLI_GUIDE.md) |
| **版本控制** | [docs/VERSION_CONTROL_QUICKSTART.md](docs/VERSION_CONTROL_QUICKSTART.md) |
| **主题切换** | [docs/theme/THEME_COMPLETE.md](docs/theme/THEME_COMPLETE.md) |
| **数据库配置** | [docs/dev/DATABASE_CONFIG.md](docs/dev/DATABASE_CONFIG.md) |

### 📊 测试与质量

| 文档 | 说明 |
|------|------|
| [docs/TESTING.md](docs/TESTING.md) | 测试指南 - 如何运行测试 |
| [docs/DEPRECATION_FIXES.md](docs/DEPRECATION_FIXES.md) | 弃用警告修复报告 |
| [docs/test-reports/](docs/test-reports/) | 测试报告归档 |

📍 [查看完整文档索引](INDEX.md)

---

## 常见问题

### 1. 如何启用认证系统？

在 `config.json` 中添加：
```json
{
  "auth": {
    "enabled": true,
    "allow_registration": true
  }
}
```

或在 `.env` 文件中设置：
```bash
AUTH_ENABLED=true
AUTH_ALLOW_REGISTRATION=true
```

📖 [详细配置指南](docs/auth/AUTH_GUIDE.md)

---

### 2. MCP/Skills 分类如何使用？

启动后在控制台界面自动显示分类，无需额外配置。

**CLI 管理**：
```bash
# MCP 管理
copaw mcp list
copaw mcp interactive

# Skills 管理
copaw skills list
copaw skills interactive
```

📖 [MCP 指南](docs/mcp/MCP_COMPLETE_GUIDE.md) | [Skills 指南](docs/cli/SKILLS_CLI_GUIDE.md)

---

### 3. 如何切换主题？

点击控制台右上角的主题切换按钮即可。

**主题类型**：
- 🌞 浅色模式
- 🌙 深色模式
- 💻 跟随系统

📖 [主题实现细节](docs/theme/THEME_COMPLETE.md)

---

### 4. 如何检查技能更新？

```bash
# 生成锁定文件
copaw skills version lock

# 检查更新
copaw skills version status

# 更新所有
copaw skills version update --all
```

📖 [版本控制指南](docs/VERSION_CONTROL_QUICKSTART.md)

---

### 5. MCP 客户端无法启动？

**排查步骤**：
```bash
# 1. 检查依赖
copaw mcp check-deps

# 2. 安装依赖
copaw mcp install-deps <client>

# 3. 查看状态
copaw mcp status

# 4. 查看日志
copaw logs mcp
```

📖 [MCP 故障排除](docs/mcp/MCP_COMPLETE_GUIDE.md#故障排除)

---

### 6. 如何备份和恢复配置？

**MCP 配置**：
```bash
# 导出
copaw mcp export backup.json

# 导入
copaw mcp import backup.json
```

**Skills 配置**：
```bash
# 导出
copaw skills export backup.json

# 导入
copaw skills import backup.json
```

---

### 7. 测试如何运行？

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py -v

# 前端测试
cd console && npm run test
```

📖 [测试完整指南](docs/TESTING.md)

---

### 8. Docker 部署？

> ⚠️ **注意**: Docker 部署支持正在完善中，建议使用源码部署。

```bash
# 查看 deploy 目录
ls deploy/

# Docker Compose (开发中)
docker-compose up -d
```

---

### 9. 如何安装 PostgreSQL 和 Redis？

**PostgreSQL 安装**：
```bash
# Docker (推荐)
docker run -d --name copaw-postgres \
  -e POSTGRES_USER=copaw \
  -e POSTGRES_PASSWORD=copaw_password \
  -e POSTGRES_DB=copaw \
  -p 5432:5432 \
  postgres:15

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@15
```

**Redis 安装**：
```bash
# Docker (推荐)
docker run -d --name copaw-redis \
  -p 6379:6379 \
  redis:7

# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

📖 [完整数据库配置指南](docs/dev/DATABASE_CONFIG.md)

---

### 10. 数据库连接失败怎么办？

**PostgreSQL 连接失败**：
```bash
# 检查服务状态
docker ps | grep postgres
# 或
pg_isready -h localhost -p 5432

# 测试连接
psql -h localhost -U copaw -d copaw -c "SELECT 1"
```

**Redis 连接失败**：
```bash
# 检查服务状态
docker ps | grep redis
# 或
redis-cli ping  # 期望输出：PONG
```

**常见错误解决**：
```bash
# 认证失败 - 重置密码
docker exec -it copaw-postgres psql -U postgres \
  -c "ALTER USER copaw WITH PASSWORD 'new_password';"

# 数据库不存在 - 创建数据库
docker exec -it copaw-postgres psql -U copaw \
  -c "CREATE DATABASE copaw;"
```

---

### 11. 如何备份数据库？

**PostgreSQL 备份**：
```bash
# 备份数据库
pg_dump -h localhost -U copaw copaw > backup.sql

# 恢复数据库
psql -h localhost -U copaw copaw < backup.sql
```

**Redis 备份**：
```bash
# 保存数据到 RDB 文件
redis-cli SAVE

# 备份文件位置
# /var/lib/redis/dump.rdb (Linux)
# /usr/local/var/db/redis/dump.rdb (macOS)
```

---

## 参与贡献

欢迎提交 Issue 和 PR！

### 贡献方式

- 🐛 [报告问题](https://github.com/Timexscz/CoPaw/issues)
- 💡 [功能建议](https://github.com/Timexscz/CoPaw/issues)
- 🔧 [提交 PR](https://github.com/Timexscz/CoPaw/pulls)
- 📖 [改进文档](docs/CONTRIBUTING_zh.md)

### 贡献者指南

1. **阅读贡献指南** - [docs/CONTRIBUTING_zh.md](docs/CONTRIBUTING_zh.md)
2. **设置开发环境** - 见下方"从源码安装"
3. **运行测试** - 确保所有测试通过
4. **提交 PR** - 遵循 [Conventional Commits](https://www.conventionalcommits.org/)

### 贡献领域

我们欢迎以下类型的贡献：

| 领域 | 说明 |
|------|------|
| 🔌 **新频道** | 添加新的聊天应用支持（钉钉、飞书、QQ 等） |
| 🧠 **新模型** | 添加新的模型后端或提供商 |
| 🛠️ **新 Skills** | 创建新的基础技能（文档处理、自动化等） |
| 🔍 **MCP 工具** | 开发新的 MCP 服务器或工具 |
| 📚 **文档** | 改进文档、教程、示例 |
| 🐛 **Bug 修复** | 修复问题、优化性能 |
| 🌍 **平台支持** | 改进 Windows、Linux、macOS 兼容性 |

📖 [完整贡献指南](docs/CONTRIBUTING_zh.md)

---

## 从源码安装

### 开发环境设置

```bash
# 1. 克隆仓库
git clone https://github.com/Timexscz/CoPaw.git
cd CoPaw

# 2. 安装开发依赖
pip install -e ".[dev]"

# 3. 安装 pre-commit
pre-commit install
```

### 运行测试

```bash
# 后端测试
pytest tests/ -v

# 前端测试
cd console && npm install && npm run test

# 生成测试覆盖率
pytest --cov=copaw --cov-report=html
```

### 代码质量

```bash
# 运行 pre-commit
pre-commit run --all-files
```

📖 [测试指南](docs/TESTING.md) | [贡献指南](docs/CONTRIBUTING_zh.md)

---

## 为什么叫 CoPaw？

CoPaw = **Co** Personal **Paw** Assistant Workstation

---

## 由谁构建

这是基于官方 [CoPaw](https://github.com/agentscope-ai/CoPaw) 的社区增强版本。

**主要贡献**:
- 🔐 **认证系统** - JWT 认证，保护 API 访问
- 🔧 **MCP/skills cli 拓展** - 完善的命令行工具
- 📂 **MCP/Skills 分类管理** - 智能分类
- 🎨 **主题切换** - 深色/浅色模式
- 📚 **文档优化** - 统一索引，精简 40%
- ✅ **测试完善** - 56 个测试 100% 通过
- 🔧 **弃用修复** - 符合 Pydantic V2、Python 3.12 标准
- 📊 **版本控制** - Skills、记忆、MCP 版本追踪

### 质量指标

| 指标 | 状态 |
|------|------|
| 测试覆盖率 | ✅ 100% (56/56) |
| 弃用警告 | ✅ 0 个 |
| 文档精简 | ✅ -46% |
| 代码规范 | ✅ Pydantic V2 |
| Python 兼容 | ✅ 3.10-3.13 |

📖 [弃用修复报告](docs/DEPRECATION_FIXES.md) | [文档清理报告](docs/DOCUMENT_CLEANUP_REPORT.md)

---

## 许可证

Apache 2.0 License - 与官方 CoPaw 保持一致。
免责声明：本项目并非Copaw Development Team 得官方产品，未获得其背书或支持。如有问题请联系本人。
---

## 官方社区与联系

| 平台 | 链接 |
|------|------|
| 💬 Discord | [加入社区](https://discord.gg/eYMpfnkG8h) |
| 🐦 X (Twitter) | [@agentscope_ai](https://x.com/agentscope_ai) |
| 📱 钉钉 | [扫码加入](https://qr.dingtalk.com/action/joingroup?code=v1,k1,OmDlBXpjW+I2vWjKDsjvI9dhcXjGZi3bQiojOq3dlDw=&_dt_no_comment=1&origin=11) |
| 🌐 官方网站 | [agentscope.io](https://agentscope.io/) |

---

<div align="center">

**CoPaw-CE v0.0.6.ce.1** | 基于 CoPaw v0.0.5.post1 | 当前维护者：Timexscz | 本人邮箱：timexscz@qq.com

[返回顶部](#-社区增强版)

</div>
>
