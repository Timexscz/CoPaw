# MCP 完整使用指南

> **整合日期**: 2026-03-14  
> **整合文档**: MCP_CLI_GUIDE, MCP_COMMANDS_SUMMARY, MCP_TROUBLESHOOTING_SUMMARY 等 7 个文档

---

## 📚 文档整合说明

本文档整合了以下 MCP 相关文档：
- `MCP_CLI_GUIDE.md` - CLI 使用指南
- `MCP_COMMANDS_SUMMARY.md` - 命令汇总
- `MCP_TROUBLESHOOTING_SUMMARY.md` - 故障排除
- `MCP_AUTO_INSTALL_IMPLEMENTATION.md` - 自动安装实现
- `MCP_DEPENDENCY_AUTO_INSTALL.md` - 依赖自动安装
- `MCP_DEPS_QUICK_REFERENCE.md` - 依赖快速参考
- `MCP_REMOTE_DIAGNOSIS_GUIDE.md` - 远程诊断指南

---

## 🚀 快速开始

### 1. 配置 MCP 客户端

在 `config.json` 中添加：

```json
{
  "mcp": {
    "clients": {
      "tavily_search": {
        "name": "Tavily Search",
        "command": "npx",
        "args": ["-y", "tavily-mcp@latest"],
        "env": {
          "TAVILY_API_KEY": "your-api-key"
        },
        "enabled": true
      }
    }
  }
}
```

### 2. 启动 MCP

```bash
copaw app
```

### 3. 验证连接

```bash
copaw mcp status
```

---

## 📋 命令参考

### 基础命令

| 命令 | 说明 | 示例 |
|-----|------|------|
| `copaw mcp status` | 查看 MCP 状态 | 查看所有客户端 |
| `copaw mcp list` | 列出 MCP 客户端 | 显示详细信息 |
| `copaw mcp restart` | 重启 MCP | 重新加载配置 |

### 版本控制命令

| 命令 | 说明 | 示例 |
|-----|------|------|
| `copaw mcp-version status` | 查看版本状态 | 查看健康状态 |
| `copaw mcp-version info` | 查看版本详情 | `copaw mcp-version info tavily` |
| `copaw mcp-version rollback` | 回滚版本 | `copaw mcp-version rollback tavily 1.0.4` |

---

## 🔧 自动安装依赖

### 支持的 MCP 工具

| 工具 | 依赖 | 自动检测 |
|-----|------|---------|
| Tavily Search | `npx` | ✅ |
| GitHub | `npx` | ✅ |
| File System | `npx` | ✅ |
| Database | `psql`, `mysql` | ✅ |

### 安装命令

```bash
# 自动安装依赖
copaw mcp install-deps <client-name>

# 示例
copaw mcp install-deps tavily_search
```

### 依赖检测

```bash
# 检测缺失的依赖
copaw mcp check-deps

# 输出示例
⚠️  tavily_search: 缺少 npx
✅  file_server: 依赖完整
```

---

## 🏥 故障排除

### 问题 1: MCP 客户端无法启动

**症状**:
```
Error: Failed to connect MCP client 'tavily_search'
```

**解决方案**:
```bash
# 1. 检查依赖
copaw mcp check-deps

# 2. 安装依赖
copaw mcp install-deps tavily_search

# 3. 验证配置
cat ~/.copaw/config.json | jq '.mcp.clients'

# 4. 重启 MCP
copaw mcp restart
```

---

### 问题 2: 版本不匹配

**症状**:
```
MCP protocol version mismatch
```

**解决方案**:
```bash
# 1. 查看版本
copaw mcp-version status

# 2. 回滚到兼容版本
copaw mcp-version rollback tavily_search 1.0.4

# 3. 或升级到最新版
npm install -g tavily-mcp@latest
```

---

### 问题 3: 健康检查失败

**症状**:
```
Health check failed: Connection timeout
```

**解决方案**:
```bash
# 1. 检查网络
ping api.tavily.com

# 2. 检查 API Key
echo $TAVILY_API_KEY

# 3. 测试连接
curl -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TAVILY_API_KEY"
```

---

### 问题 4: 配置不生效

**症状**: 修改 config.json 后无变化

**解决方案**:
```bash
# 1. 验证 JSON 格式
cat ~/.copaw/config.json | jq .

# 2. 重启应用
copaw daemon restart

# 3. 清除缓存
rm -rf ~/.copaw/.cache
```

---

## 📊 故障诊断流程

```
开始
  ↓
检查状态 → copaw mcp status
  ↓
查看日志 → copaw logs mcp
  ↓
检查依赖 → copaw mcp check-deps
  ↓
验证配置 → cat config.json | jq .mcp
  ↓
测试连接 → curl API
  ↓
查看版本 → copaw mcp-version status
  ↓
解决！
```

---

## 🔍 远程诊断

### 1. 收集诊断信息

```bash
# 运行诊断
copaw mcp diagnose

# 输出诊断报告
MCP Diagnostic Report
=====================
Client: tavily_search
Status: unhealthy
Version: 1.0.5
Protocol: 2024-11-05
Last Error: Connection timeout
```

### 2. 发送诊断报告

```bash
# 保存到文件
copaw mcp diagnose > mcp_diagnosis.txt

# 发送给支持团队
email support@copaw.ai < mcp_diagnosis.txt
```

---

## 📈 性能优化

### 1. 调整连接池

```json
{
  "mcp": {
    "pool_size": 10,
    "timeout": 30
  }
}
```

### 2. 启用缓存

```json
{
  "mcp": {
    "cache": {
      "enabled": true,
      "ttl": 300
    }
  }
}
```

### 3. 监控健康

```bash
# 定期检查
copaw mcp-version health-check --interval 60
```

---

## 🎯 最佳实践

### 配置管理

1. **使用环境变量**
   ```json
   {
     "env": {
       "API_KEY": "${TAVILY_API_KEY}"
     }
   }
   ```

2. **版本锁定**
   ```json
   {
     "args": ["-y", "tavily-mcp@1.0.5"]
   }
   ```

3. **健康检查**
   ```bash
   # 添加到 cron
   0 * * * * copaw mcp-version health-check
   ```

---

## 📊 命令速查表

### 日常操作

```bash
# 查看状态
copaw mcp status

# 重启
copaw mcp restart

# 查看日志
copaw logs mcp
```

### 版本管理

```bash
# 查看版本
copaw mcp-version status

# 回滚
copaw mcp-version rollback <client> <version>

# 健康检查
copaw mcp-version health-check
```

### 依赖管理

```bash
# 检查依赖
copaw mcp check-deps

# 安装依赖
copaw mcp install-deps <client>
```

---

## 🔗 相关文档

- [版本控制使用指南](../VERSION_CONTROL_USER_GUIDE.md)
- [CLI 快速参考](../cli/CLI_QUICK_REFERENCE.md)
- [远程诊断指南](MCP_REMOTE_DIAGNOSIS_GUIDE.md)

---

**原文档**:
- MCP_CLI_GUIDE.md
- MCP_COMMANDS_SUMMARY.md
- MCP_TROUBLESHOOTING_SUMMARY.md
- MCP_AUTO_INSTALL_IMPLEMENTATION.md
- MCP_DEPENDENCY_AUTO_INSTALL.md
- MCP_DEPS_QUICK_REFERENCE.md
- MCP_REMOTE_DIAGNOSIS_GUIDE.md

**整合完成**: 2026-03-14  
**维护者**: CoPaw Development Team
