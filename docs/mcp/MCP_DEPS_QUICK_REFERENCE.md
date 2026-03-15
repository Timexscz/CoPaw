# MCP 依赖自动安装 - 快速参考

## 🎯 一句话解决

```bash
copaw mcp check-deps -y
```

## 📋 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `check-deps` | 检查并安装依赖 | `copaw mcp check-deps` |
| `check-deps [key]` | 检查特定客户端 | `copaw mcp check-deps tavily_search` |
| `check-deps -y` | 自动确认安装 | `copaw mcp check-deps -y` |
| `check-deps --dry-run` | 仅检查，不安装 | `copaw mcp check-deps --dry-run` |
| `install-deps` | 快速安装（同 -y） | `copaw mcp install-deps` |

## 🔍 支持的协议类型

| 类型 | 依赖检查 | 说明 |
|------|---------|------|
| **stdio** | ✅ 需要 | 本地服务（npx, uv, python, docker 等） |
| **streamable_http** | ❌ 不需要 | 远程 HTTP 端点 |
| **http** | ❌ 不需要 | 远程 HTTP 端点 |
| **sse** | ❌ 不需要 | 远程 SSE 端点 |

## 🛠️ 支持的工具

| 工具 | 自动安装 | 手动安装链接 |
|------|---------|-------------|
| **npx** | ❌ 系统安装 | https://nodejs.org/ |
| **uv/uvx** | ✅ 自动 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **python** | ❌ 系统安装 | https://python.org/ |
| **docker** | ❌ 系统安装 | https://docker.com/ |
| **pip** | ✅ 自动 | `python -m ensurepip --upgrade` |
| **pipx** | ✅ 自动 | `python -m pip install pipx` |

## 🚀 典型使用场景

### 场景 1: 新安装 CoPaw 后
```bash
# 一键检查并安装所有依赖
copaw mcp check-deps -y
```

### 场景 2: 添加新的 MCP 客户端后
```bash
# 添加客户端
copaw mcp add my-mcp --name "My MCP" --type local \
  --command npx --args "-y,@modelcontextprotocol/server-example"

# 检查依赖
copaw mcp check-deps my-mcp
```

### 场景 3: 导入配置后
```bash
# 导入配置
copaw mcp import mcp-clients.json

# 检查所有客户端
copaw mcp check-deps
```

### 场景 4: CI/CD 自动化
```bash
#!/bin/bash
# 非交互式自动安装
copaw mcp check-deps -y || exit 1
copaw app
```

### 场景 5: 仅查看问题
```bash
# Dry run - 查看需要做什么，但不实际安装
copaw mcp check-deps --dry-run
```

## 📊 状态说明

| 状态 | 含义 | 操作 |
|------|------|------|
| ✓ Ready | 依赖已满足 | 无需操作 |
| ✗ Missing deps | 缺少依赖 | 运行 `check-deps` |
| Remote client | 远程客户端 | 无需本地依赖 |

## 🐛 快速故障排除

### 问题：工具已安装但检测失败
```bash
# 检查命令是否在 PATH 中
which npx
which uv
which python

# 如果未找到，需要安装或添加到 PATH
```

### 问题：安装失败
```bash
# 查看详细错误信息
copaw mcp check-deps

# 根据提示手动安装
# 例如：访问 https://nodejs.org/ 安装 Node.js
```

### 问题：远程客户端连接失败
```bash
# 这不是依赖问题，检查网络和配置
curl http://localhost:8000/mcp
copaw mcp info remote-mcp
```

## 💡 提示

1. **首次使用建议**：运行 `copaw mcp check-deps -y` 确保所有依赖就绪
2. **远程客户端**：HTTP/SSE 客户端不需要本地依赖检查
3. **系统工具**：Node.js、Python、Docker 需要手动安装（系统级）
4. **Python 工具**：uv、pip、pipx 可以自动安装

## 📖 详细文档

- [MCP_DEPENDENCY_AUTO_INSTALL.md](./MCP_DEPENDENCY_AUTO_INSTALL.md) - 完整使用指南
- [MCP_CLI_GUIDE.md](./MCP_CLI_GUIDE.md) - MCP CLI 完整指南
- [MCP_AUTO_INSTALL_IMPLEMENTATION.md](./MCP_AUTO_INSTALL_IMPLEMENTATION.md) - 实现细节

---

**更新时间**: 2026-03-12  
**版本**: v0.0.6
