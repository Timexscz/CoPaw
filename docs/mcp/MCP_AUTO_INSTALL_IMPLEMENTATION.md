# MCP 依赖自动安装功能实现总结

## 📋 实现概述

根据 MCP 协议的几种主要类型（stdio、http:sse、streamable http），实现了一个智能的依赖自动识别和安装系统。

## 🎯 解决的问题

1. **MCP 服务打开后初始化时，command 有 possibilities 缺失依赖的问题**
   - 现在会在客户端连接前自动检测依赖
   - 提供友好的安装提示和自动安装选项

2. **远程 MCP 打开报错的问题**
   - 远程客户端（HTTP/SSE）不再进行本地依赖检查
   - 明确区分本地和远程客户端的依赖需求

3. **自动识别安装依赖**
   - 根据 command 类型自动识别所需工具
   - 支持多种协议类型的智能判断

## 📁 新增文件

### 1. `src/copaw/cli/mcp_deps_installer.py`
核心依赖检测和安装模块

**主要类：**
- `MCPDependencyInstaller` - 依赖安装器主类
- `CommandTool` - 支持的工具枚举（npx, uv, uvx, python, docker, node, pip, pipx）
- `TransportType` - 传输类型枚举（stdio, streamable_http, http, sse）
- `CheckResult` - 检查结果数据类

**主要函数：**
- `check_mcp_client_dependencies()` - 检查单个客户端依赖
- `check_all_mcp_clients()` - 批量检查所有客户端依赖

### 2. `MCP_DEPENDENCY_AUTO_INSTALL.md`
用户使用指南文档

### 3. `test_mcp_deps.py`
自动化测试脚本

## 🔧 修改的文件

### 1. `src/copaw/cli/mcp_cmd.py`
**新增命令：**
- `check-deps` - 检查和安装依赖
- `install-deps` - 快速安装依赖（自动确认）

**新增导入：**
```python
from .mcp_deps_installer import (
    check_mcp_client_dependencies,
    check_all_mcp_clients,
)
```

### 2. `src/copaw/app/mcp/manager.py`
**增强功能：**
- 在 `_add_client()` 方法中添加依赖预检查
- 在连接前检测工具是否已安装
- 提供友好的缺失工具警告

## 🚀 支持的协议类型

### 1. stdio (本地服务)
需要检测依赖的工具：
- `npx` - Node.js 包执行器
- `uv` / `uvx` - 快速 Python 包管理器
- `python` / `python3` - Python 解释器
- `docker` - 容器运行时
- `node` - Node.js 运行时
- `pip` / `pipx` - Python 包安装器

### 2. streamable_http (远程 HTTP)
- 无需本地依赖检查
- 直接连接远程端点

### 3. sse (Server-Sent Events)
- 无需本地依赖检查
- 直接连接远程端点

### 4. http (远程 HTTP)
- 无需本地依赖检查
- 直接连接远程端点

## 💡 使用示例

### 检查所有客户端依赖
```bash
copaw mcp check-deps
```

### 检查特定客户端
```bash
copaw mcp check-deps tavily_search
```

### 自动确认安装
```bash
copaw mcp check-deps -y
```

### 仅检查，不安装（Dry Run）
```bash
copaw mcp check-deps --dry-run
```

### 快速安装依赖
```bash
copaw mcp install-deps
```

## 📊 功能特性

### 1. 智能检测
- 自动识别命令类型
- 智能提取包名和版本
- 区分本地和远程客户端

### 2. 友好的用户界面
- 进度条显示
- 彩色状态输出
- 详细的安装说明

### 3. 交互式确认
- 安装前询问用户
- 支持自动确认模式
- 支持 dry-run 模式

### 4. 错误处理
- 优雅的安装失败处理
- 提供手动安装说明
- 详细的错误信息

### 5. 状态报告
- 表格形式的汇总报告
- 每个客户端的状态详情
- 缺失依赖的安装指导

## 🧪 测试结果

```
============================================================
Testing Command Detection
============================================================

✓ Command: npx                  → Tool: npx        (Expected: npx)
✓ Command: uvx                  → Tool: uvx        (Expected: uvx)
✓ Command: python               → Tool: python     (Expected: python)
✓ Command: docker               → Tool: docker     (Expected: docker)
✓ Command: node                 → Tool: node       (Expected: node)
✓ Command: pip                  → Tool: pip        (Expected: pip)
✓ Command: /usr/bin/python3     → Tool: python     (Expected: python)

============================================================
Testing Transport Detection
============================================================

✓ Transport: stdio                → Needs check: True
✓ Transport: streamable_http      → Needs check: False
✓ Transport: http                 → Needs check: False
✓ Transport: sse                  → Needs check: False

============================================================
Testing Tool Installation Check
============================================================

✓ npx       : Installed
✓ uv        : Installed
✓ uvx       : Installed
✓ python    : Installed
✓ docker    : Installed
✓ pip       : Installed
```

## 📝 集成说明

### 在应用启动时
MCP 客户端管理器会在连接前自动检查依赖：

```python
async def _add_client(self, key: str, client_config: "MCPClientConfig", ...):
    # Auto-check dependencies for stdio clients
    if client_config.transport == "stdio" and client_config.command:
        # 检查工具是否安装
        tool = installer.detect_command_tool(client_config.command)
        is_installed = await installer.check_tool_installed(tool)
        
        if not is_installed:
            logger.warning(
                f"MCP client '{key}' requires '{tool.value}' which is not installed. "
                f"Run 'copaw mcp install-deps {key}' to install dependencies."
            )
```

### 在 CLI 中
用户可以通过命令行手动检查和安装：

```bash
# 添加新客户端后
copaw mcp add my-mcp --name "My MCP" --type local \
  --command npx --args "-y,@modelcontextprotocol/server-example"

# 立即检查依赖
copaw mcp check-deps my-mcp
```

## 🔗 相关文档

- [MCP 依赖自动安装指南](./MCP_DEPENDENCY_AUTO_INSTALL.md)
- [MCP CLI 使用指南](./MCP_CLI_GUIDE.md)
- [MCP 分类配置](./src/copaw/config/mcpCategories.py)

## 🎨 输出示例

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

## 🚧 未来改进

1. **缓存机制** - 缓存已检查的结果，避免重复检查
2. **后台安装** - 支持后台异步安装依赖
3. **依赖锁定** - 支持锁定特定版本
4. **批量操作** - 支持按类别批量检查和安装
5. **自动修复** - 检测到问题时自动尝试修复

## 📦 依赖要求

- Python 3.10+
- rich (终端美化输出)
- click (CLI 框架)
- asyncio (异步支持)

## ✅ 完成状态

- [x] 核心依赖检测模块
- [x] CLI 命令集成
- [x] MCP 管理器集成
- [x] 交互式确认
- [x] 进度显示
- [x] 文档编写
- [x] 测试脚本
- [x] 错误处理
- [x] 状态报告

---

**实现日期**: 2026-03-12
**版本**: v0.0.6
**作者**: Timexscz
