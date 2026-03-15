# MCP 远程连接问题诊断指南

## 📋 问题症状

```
McpError: Session terminated
Traceback (most recent call last):
  File ".../mcp/client/session.py", line 171, in initialize
    result = await self.send_request(...)
mcp.shared.exceptions.McpError: Session terminated
```

## 🛠️ 诊断工具

### 使用诊断命令

```bash
# 诊断特定客户端
copaw mcp diagnose bing-cn-mcp-server

# 诊断所有远程客户端
copaw mcp diagnose --all
```

### 诊断工具会检查

1. **配置验证**
   - Transport 类型是否正确
   - URL 格式是否正确
   - 远程客户端是否错误配置了 command

2. **HTTP 连通性测试**
   - 服务器是否可访问
   - HTTP 状态码检查
   - 网络连接测试

3. **MCP 协议测试**
   - MCP 会话初始化
   - 协议版本兼容性
   - 工具列表获取

## 🔍 常见错误及解决方案

### 错误 1: Session terminated

**错误信息：**
```
McpError: Session terminated
```

**可能原因：**
- MCP 协议版本不匹配
- 服务器在 initialize 阶段拒绝了请求
- 服务器需要认证但未提供
- 服务器配置错误

**解决步骤：**

```bash
# 1. 运行诊断
copaw mcp diagnose bing-cn-mcp-server

# 2. 检查服务器日志
# 查看远程 MCP 服务器的日志输出

# 3. 验证 MCP 协议版本
# 确保客户端和服务器使用兼容的 MCP 版本

# 4. 检查是否需要认证
# 如果需要，添加 headers
copaw mcp update bing-cn-mcp-server \
  --headers "Authorization=Bearer YOUR_TOKEN"
```

### 错误 2: Connection refused

**错误信息：**
```
httpx.ConnectError: Connection refused
```

**可能原因：**
- 服务器未运行
- URL 或端口错误
- 防火墙阻止连接

**解决步骤：**

```bash
# 1. 检查服务器是否运行
curl -v http://<server-host>:<port>/

# 2. 验证 URL 配置
copaw mcp info bing-cn-mcp-server

# 3. 检查防火墙
# Linux: sudo ufw status
# macOS: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# 4. 测试本地连接
curl http://localhost:<port>/mcp
```

### 错误 3: Timeout

**错误信息：**
```
asyncio.TimeoutError: Timeout connecting MCP client
```

**可能原因：**
- 网络延迟过高
- 服务器响应慢
- 服务器挂起

**解决步骤：**

```bash
# 1. 测试网络延迟
ping <server-host>

# 2. 增加超时时间（需要修改配置）
# 在 manager.py 中调整 timeout 参数

# 3. 检查服务器性能
# 查看服务器 CPU/内存使用情况
```

### 错误 4: 404 Not Found

**错误信息：**
```
httpx.HTTPStatusError: 404 Not Found
```

**可能原因：**
- URL 路径错误
- 端点不存在

**解决步骤：**

```bash
# 1. 验证 URL 路径
# streamable_http 通常是：http://host:port/mcp
# SSE 通常是：http://host:port/events

# 2. 检查服务器文档
# 确认正确的端点路径

# 3. 更新配置
copaw mcp remove bing-cn-mcp-server
copaw mcp add bing-cn-mcp-server \
  --name "Bing CN MCP" \
  --type remote \
  --url http://correct-url:port/correct-path \
  --transport streamable_http
```

## 📖 完整的诊断流程

### 步骤 1: 查看配置

```bash
copaw mcp info bing-cn-mcp-server
```

检查输出：
- ✓ Transport 是 `streamable_http` 或 `sse`
- ✓ URL 格式正确（以 http:// 或 https:// 开头）
- ✓ Command 为空（远程客户端不应该有 command）

### 步骤 2: 运行诊断工具

```bash
copaw mcp diagnose bing-cn-mcp-server
```

查看诊断结果：
- ✓ Configuration: Pass
- ✓ HTTP Connectivity: Pass
- ✗ MCP Initialize: Fail ← 问题在这里

### 步骤 3: 检查服务器状态

```bash
# 测试 HTTP 连接
curl -v http://<server-url>/

# 查看服务器日志
# 根据服务器部署位置查看相应日志
```

### 步骤 4: 查看服务器日志

服务器日志可能显示：
```
Error: Invalid MCP protocol version
Error: Authentication required
Error: Configuration error
```

### 步骤 5: 根据日志修复

**如果是协议版本问题：**
- 升级服务器或客户端的 MCP SDK

**如果是认证问题：**
```bash
copaw mcp update bing-cn-mcp-server \
  --headers "Authorization=Bearer YOUR_TOKEN"
```

**如果是配置问题：**
- 修复服务器配置后重启

### 步骤 6: 临时禁用问题客户端

如果服务器暂时不可用：

```bash
copaw mcp disable bing-cn-mcp-server
copaw app
```

## 🔧 高级调试

### 启用详细日志

修改日志级别为 DEBUG：

```bash
# 在启动时设置日志级别
LOG_LEVEL=DEBUG copaw app
```

查看日志输出：
```
DEBUG src/copaw/app/mcp/manager.py | Building remote MCP client:
  Name: Bing CN MCP
  Transport: streamable_http
  URL: http://localhost:8000/mcp
  Headers: none
```

### 手动测试 MCP 连接

```python
import asyncio
from agentscope.mcp import HttpStatefulClient

async def test():
    client = HttpStatefulClient(
        name="test",
        transport="streamable_http",
        url="http://localhost:8000/mcp",
    )
    try:
        await client.connect()
        print("✓ Connection successful")
        tools = await client.list_tools()
        print(f"Available tools: {len(tools)}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
    finally:
        await client.close()

asyncio.run(test())
```

## 📊 配置示例

### 正确的 streamable_http 配置

```json
{
  "bing-cn-mcp-server": {
    "name": "Bing CN MCP",
    "enabled": true,
    "transport": "streamable_http",
    "url": "http://localhost:8000/mcp",
    "command": "",
    "args": [],
    "env": {},
    "headers": {}
  }
}
```

### 正确的 sse 配置

```json
{
  "bing-cn-mcp-server": {
    "name": "Bing CN MCP",
    "enabled": true,
    "transport": "sse",
    "url": "http://localhost:8000/events",
    "command": "",
    "args": [],
    "env": {},
    "headers": {}
  }
}
```

### 错误的配置（常见错误）

```json
{
  "bing-cn-mcp-server": {
    "name": "Bing CN MCP",
    "enabled": true,
    "transport": "stdio",  // ❌ 错误：远程客户端用了 stdio
    "url": "http://localhost:8000/mcp",
    "command": "some-command"  // ❌ 错误：远程客户端不应该有 command
  }
}
```

## 🎯 快速解决清单

- [ ] 运行 `copaw mcp diagnose <client-key>`
- [ ] 检查配置 `copaw mcp info <client-key>`
- [ ] 测试 HTTP 连接 `curl -v <url>`
- [ ] 查看服务器日志
- [ ] 验证 MCP 协议版本
- [ ] 检查是否需要认证
- [ ] 确认防火墙设置
- [ ] 临时禁用问题客户端

## 📞 需要更多帮助？

如果以上步骤都无法解决问题，请收集以下信息：

1. **诊断输出**
   ```bash
   copaw mcp diagnose <client-key>
   ```

2. **客户端配置**
   ```bash
   copaw mcp info <client-key>
   ```

3. **完整错误日志**
   ```bash
   LOG_LEVEL=DEBUG copaw app 2>&1 | grep -A 20 "<client-key>"
   ```

4. **服务器日志**
   - 远程 MCP 服务器的完整日志输出

5. **网络测试结果**
   ```bash
   curl -v <mcp-server-url>
   ```

---

**更新时间**: 2026-03-12
**版本**: v0.0.6
