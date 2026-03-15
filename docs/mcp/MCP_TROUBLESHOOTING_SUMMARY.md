# MCP 问题诊断工具总结

## 🎯 问题分类

根据你描述的问题，我们实现了两套工具来诊断和解决 MCP 相关问题：

### 1. 本地依赖问题 ✓
**症状：** 添加本地 MCP 客户端后，启动时报缺少工具（npx, uv, python 等）

**解决方案：** 使用依赖自动安装工具
```bash
copaw mcp check-deps -y
```

### 2. 远程连接问题 ✓
**症状：** 添加远程 MCP 客户端后，启动时报 `Session terminated`

**解决方案：** 使用远程诊断工具
```bash
copaw mcp diagnose bing-cn-mcp-server
```

---

## 📦 新增工具

### 工具 1: 依赖自动安装器

**文件：** `src/copaw/cli/mcp_deps_installer.py`

**功能：**
- 自动检测 MCP 客户端需要的工具（npx, uv, python, docker 等）
- 支持 4 种协议类型识别（stdio, streamable_http, http, sse）
- 自动安装或提供安装指导
- 交互式确认和进度显示

**命令：**
```bash
# 检查所有客户端
copaw mcp check-deps

# 自动确认安装
copaw mcp check-deps -y

# 仅检查特定客户端
copaw mcp check-deps tavily_search

# Dry run 模式
copaw mcp check-deps --dry-run
```

### 工具 2: 远程连接诊断器

**文件：** `src/copaw/cli/mcp_diagnose.py`

**功能：**
- 检查客户端配置是否正确
- 测试 HTTP/SSE 连接是否通畅
- 测试 MCP 协议初始化
- 提供详细的错误原因分析

**命令：**
```bash
# 诊断特定客户端
copaw mcp diagnose bing-cn-mcp-server

# 诊断所有远程客户端
copaw mcp diagnose --all
```

---

## 🔧 针对你的问题的解决方案

### 问题：`bing-cn-mcp-server` 连接失败

**错误信息：**
```
McpError: Session terminated
```

**诊断步骤：**

```bash
# 1. 查看客户端配置
copaw mcp info bing-cn-mcp-server

# 2. 运行诊断工具
copaw mcp diagnose bing-cn-mcp-server

# 3. 根据诊断结果修复
# 如果诊断显示配置问题
copaw mcp remove bing-cn-mcp-server
copaw mcp add bing-cn-mcp-server \
  --name "Bing CN MCP" \
  --type remote \
  --url http://correct-url:port/mcp \
  --transport streamable_http

# 如果服务器暂时不可用，先禁用
copaw mcp disable bing-cn-mcp-server

# 重启 CoPaw
copaw app
```

---

## 📊 输出示例

### 依赖检查输出

```
============================================================
Checking dependencies for 3 MCP client(s)...
============================================================
Dependency Check Summary
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Client        ┃ Name       ┃ Transport   ┃ Status     ┃ Message            ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ tavily_search │ tavily_mcp │ stdio       │ ✓ Ready    │ Dependencies       │
│               │            │             │            │ satisfied          │
│ remote-mcp    │ Remote MCP │ streamable… │ ✓ Ready    │ Remote client (no  │
│               │            │             │            │ dependencies)      │
└───────────────┴────────────┴─────────────┴────────────┴────────────────────┘

Summary: 2/3 client(s) ready
```

### 诊断工具输出

```
============================================================
MCP Client Diagnostic: bing-cn-mcp-server
============================================================

Client Info
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ MCP Client Diagnostic: bing-cn-mcp-server┃
┃                                         ┃
┃ Name: Bing CN MCP                       ┃
┃ Enabled: True                           ┃
┃ Transport: streamable_http              ┃
┃ URL: http://localhost:8000/mcp          ┃
┃ Command: N/A                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Checking configuration for: bing-cn-mcp-server
✓ Configuration looks good

Testing connection to: http://localhost:8000/mcp
Transport type: streamable_http
Status Code: 200
✓ Server is reachable

Testing MCP initialization for: bing-cn-mcp-server
Attempting to connect...
✗ MCP connection failed: Session terminated

Diagnosis
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Session terminated during initialize    ┃
┃ phase.                                  ┃
┃                                         ┃
┃ Possible causes:                        ┃
┃ • MCP protocol version mismatch         ┃
┃ • Server rejected the connection        ┃
┃ • Authentication required but not       ┃
┃   provided                              ┃
┃ • Server configuration error            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

============================================================
Diagnostic Summary
============================================================
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Check               ┃ Status       ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Configuration       │ ✓ Pass       │
│ HTTP Connectivity   │ ✓ Pass       │
│ MCP Initialize      │ ✕ Fail       │
└─────────────────────┴──────────────┘

✗ MCP connection failed. Check the errors above.

Suggestions:
  1. Verify the remote MCP server is running
  2. Check server logs for error messages
  3. Verify MCP protocol version compatibility
  4. Try accessing the URL from a browser or curl
```

---

## 📁 修改的文件

### 1. `src/copaw/cli/mcp_cmd.py`
**新增命令：**
- `check-deps` - 检查和安装依赖
- `install-deps` - 快速安装依赖
- `diagnose` - 诊断远程连接问题

### 2. `src/copaw/app/mcp/manager.py`
**增强功能：**
- 连接失败时提供详细的错误日志
- 包含可能的原因分析
- 提供诊断工具的使用建议

### 3. `src/copaw/cli/mcp_deps_installer.py` (新增)
- 依赖检测和安装核心模块

### 4. `src/copaw/cli/mcp_diagnose.py` (新增)
- 远程连接诊断核心模块

---

## 📖 相关文档

1. **[MCP_DEPENDENCY_AUTO_INSTALL.md](./MCP_DEPENDENCY_AUTO_INSTALL.md)**
   - 依赖自动安装的完整使用指南

2. **[MCP_REMOTE_DIAGNOSIS_GUIDE.md](./MCP_REMOTE_DIAGNOSIS_GUIDE.md)**
   - 远程连接问题的详细诊断流程

3. **[MCP_AUTO_INSTALL_IMPLEMENTATION.md](./MCP_AUTO_INSTALL_IMPLEMENTATION.md)**
   - 依赖自动安装的实现细节

4. **[MCP_DEPS_QUICK_REFERENCE.md](./MCP_DEPS_QUICK_REFERENCE.md)**
   - 快速参考卡片

---

## 🎯 快速解决你的问题

```bash
# 对于 bing-cn-mcp-server 连接问题

# 1. 运行诊断
copaw mcp diagnose bing-cn-mcp-server

# 2. 根据诊断结果修复
# 如果配置错误
copaw mcp remove bing-cn-mcp-server
copaw mcp add bing-cn-mcp-server \
  --name "Bing CN MCP" \
  --type remote \
  --url http://correct-url:port/mcp \
  --transport streamable_http

# 如果服务器问题，先禁用
copaw mcp disable bing-cn-mcp-server

# 3. 重启 CoPaw
copaw app
```

---

**更新时间**: 2026-03-12
**版本**: v0.0.6
