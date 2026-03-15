# MCP 依赖自动安装指南

## 📋 概述

CoPaw 现在支持自动检测和安装 MCP 客户端的依赖项。根据 MCP 协议的类型（stdio、http:sse、streamable http），系统会自动识别所需的工具（如 npx、uv、uvx、python、docker 等）并提供安装指导。

## 🎯 支持的协议类型

### 1. **stdio** (本地服务)
需要本地命令行工具来启动 MCP 服务器：
- `npx` - Node.js 包执行器
- `uv` / `uvx` - 快速 Python 包管理器
- `python` - Python 解释器
- `docker` - 容器运行时
- `node` - Node.js 运行时
- `pip` / `pipx` - Python 包安装器

### 2. **streamable_http** (远程 HTTP)
远程 HTTP 端点，无需本地依赖：
- 直接连接到远程 MCP 服务
- 无本地依赖检查

### 3. **sse** (Server-Sent Events)
远程 SSE 端点，无需本地依赖：
- 直接连接到远程 MCP 服务
- 无本地依赖检查

## 🚀 快速开始

### 1. 检查所有 MCP 客户端的依赖

```bash
copaw mcp check-deps
```

**输出示例：**
```
============================================================
Checking dependencies for 3 MCP client(s)...
============================================================
🔍 Checking dependencies for tavily_mcp...
   Tool: npx
   Package: tavily-mcp@latest

✓ Dependencies satisfied for tavily-mcp

============================================================
Dependency Check Summary
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Client        ┃ Name       ┃ Transport   ┃ Status     ┃ Message            ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ tavily_search │ tavily_mcp │ stdio       │ ✓ Ready    │ Dependencies       │
│               │            │             │            │ satisfied          │
│ remote-mcp    │ Remote MCP │ streamable… │ ✓ Ready    │ Remote client (no  │
│               │            │             │            │ dependencies)      │
│ local-py      │ Python MCP │ stdio       │ ✗ Missing… │ Missing            │
│               │            │             │            │ dependencies       │
└───────────────┴────────────┴─────────────┴────────────┴────────────────────┘

Summary: 2/3 client(s) ready

✗ Failed to install: python
⚠ Some clients may not work until dependencies are installed manually

Installation instructions:
  • Python: https://python.org/
============================================================
```

### 2. 检查特定客户端

```bash
copaw mcp check-deps tavily_search
```

### 3. 自动确认安装（非交互模式）

```bash
copaw mcp check-deps -y
```

### 4. 仅检查，不安装（Dry Run）

```bash
copaw mcp check-deps --dry-run
```

### 5. 安装缺失的依赖

```bash
copaw mcp install-deps
```

这等同于 `check-deps -y`，会自动确认所有安装。

## 📖 命令详解

### `copaw mcp check-deps [key]`

检查并安装 MCP 客户端的依赖。

**参数：**
- `key` (可选) - 指定要检查的客户端密钥

**选项：**
- `-y, --yes` - 自动确认所有安装
- `--dry-run` - 仅检查，不实际安装

**示例：**
```bash
# 检查所有启用的客户端
copaw mcp check-deps

# 检查特定客户端
copaw mcp check-deps my-mcp

# 自动确认安装
copaw mcp check-deps -y

# 仅检查，显示将执行的操作
copaw mcp check-deps --dry-run
```

### `copaw mcp install-deps [key]`

安装缺失的依赖（自动确认）。

**参数：**
- `key` (可选) - 指定要安装的客户端密钥

**选项：**
- `-y, --yes` - 自动确认（此命令默认自动确认）

**示例：**
```bash
# 为所有客户端安装依赖
copaw mcp install-deps

# 为特定客户端安装
copaw mcp install-deps my-mcp
```

## 🔧 工具安装说明

### Node.js (npx)

**自动检测：** 检查 `npx` 或 `node` 命令

**手动安装：**
- macOS: `brew install node`
- Ubuntu/Debian: `sudo apt install nodejs npm`
- Fedora: `sudo dnf install nodejs npm`
- 官方：https://nodejs.org/

### uv / uvx

**自动检测：** 检查 `uv` 或 `uvx` 命令

**自动安装：** `curl -LsSf https://astral.sh/uv/install.sh | sh`

**手动安装：** 参考 https://github.com/astral-sh/uv

### Python

**自动检测：** 检查 `python` 或 `python3` 命令

**手动安装：**
- macOS: `brew install python`
- Ubuntu/Debian: `sudo apt install python3 python3-pip`
- Fedora: `sudo dnf install python3 python3-pip`
- 官方：https://python.org/

### Docker

**自动检测：** 检查 `docker` 命令

**手动安装：** https://docker.com/

### pip / pipx

**自动安装：** 
- pip: `python -m ensurepip --upgrade`
- pipx: `python -m pip install pipx && python -m pipx ensurepath`

## 💡 最佳实践

### 1. 初始化后检查

在首次安装或导入 MCP 配置后，运行：

```bash
copaw mcp check-deps -y
```

### 2. 添加新客户端时

添加新的 MCP 客户端后，立即检查依赖：

```bash
copaw mcp add my-mcp --name "My MCP" --type local \
  --command npx --args "-y,@modelcontextprotocol/server-example"

copaw mcp check-deps my-mcp
```

### 3. CI/CD 集成

在自动化脚本中使用：

```bash
#!/bin/bash
# 检查依赖（失败时退出）
copaw mcp check-deps -y || exit 1

# 启动应用
copaw app
```

### 4. 远程客户端

远程客户端（HTTP/SSE）不需要本地依赖检查：

```bash
copaw mcp add remote-mcp --name "Remote" --type remote \
  --url http://localhost:8000/mcp --transport streamable_http

# 这将显示 "Remote client (no dependencies)"
copaw mcp check-deps remote-mcp
```

## 🐛 故障排查

### 问题 1: 工具已安装但检测失败

**原因：** 命令不在 PATH 中

**解决：**
```bash
# 检查命令位置
which npx
which uv
which python

# 如果未找到，添加到 PATH 或重新安装
```

### 问题 2: 安装失败

**原因：** 权限问题或网络问题

**解决：**
```bash
# 查看详细的安装说明
copaw mcp check-deps

# 手动访问提供的 URL 进行安装
```

### 问题 3: 远程客户端连接失败

**原因：** 这不是依赖问题，而是网络或配置问题

**解决：**
```bash
# 检查 URL 是否可访问
curl http://localhost:8000/mcp

# 检查客户端配置
copaw mcp info remote-mcp
```

## 📊 状态码说明

| 状态 | 说明 |
|------|------|
| ✓ Ready | 依赖已满足，客户端可以运行 |
| ✗ Missing deps | 缺少依赖，需要安装 |
| Remote client (no dependencies) | 远程客户端，无需本地依赖 |

## 🔗 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [CoPaw MCP 使用指南](./MCP_CLI_GUIDE.md)
- [uv 文档](https://github.com/astral-sh/uv)
- [Node.js 文档](https://nodejs.org/)

## 📝 更新日志

- **v0.0.6** (2026-03-12): 初始版本
  - 支持 npx, uv, uvx, python, docker, node, pip, pipx
  - 自动检测和安装
  - 交互式确认
  - 详细的安装说明

---

**更新时间**: 2026-03-12
**版本**: v0.0.6
