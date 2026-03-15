# CoPaw MCP 命令行工具使用指南

## 📋 命令列表

```bash
copaw mcp           # MCP 客户端管理主命令
  list              # 列出 MCP 客户端
  add               # 添加新的 MCP 客户端
  remove            # 删除 MCP 客户端
  enable            # 启用 MCP 客户端
  disable           # 禁用 MCP 客户端
  info              # 显示 MCP 客户端详情
  export            # 导出 MCP 客户端配置
  import            # 导入 MCP 客户端配置
  interactive       # 交互式管理界面
```

---

## 🚀 使用示例

### 1. 列出 MCP 客户端

```bash
# 列出所有已启用的客户端
copaw mcp list

# 列出所有客户端（包括已禁用的）
copaw mcp list --all
```

**输出示例：**
```
MCP Clients                           
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Key           ┃ Name       ┃ Type  ┃ Status    ┃ Description ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Memory        │ Memory     │ Local │ ✓ Enabled │ -           │
│ tavily_search │ tavily_mcp │ Local │ ✓ Enabled │ -           │
└───────────────┴────────────┴───────┴───────────┴─────────────┘

Total: 2 client(s)
```

---

### 2. 添加 MCP 客户端

#### 添加本地客户端（stdio）

```bash
copaw mcp add my-mcp \
  --name "My MCP Server" \
  --type local \
  --command npx \
  --args "-y,@modelcontextprotocol/server-example" \
  --env "API_KEY=your-api-key"
```

#### 添加远程客户端（HTTP）

```bash
copaw mcp add remote-mcp \
  --name "Remote MCP" \
  --type remote \
  --url http://localhost:8000/mcp \
  --transport streamable_http
```

#### 添加远程客户端（SSE）

```bash
copaw mcp add sse-mcp \
  --name "SSE MCP" \
  --type remote \
  --url http://localhost:8001/events \
  --transport sse
```

---

### 3. 删除 MCP 客户端

```bash
# 删除前确认
copaw mcp remove my-mcp

# 跳过确认
copaw mcp remove my-mcp -y
```

---

### 4. 启用/禁用 MCP 客户端

```bash
# 启用客户端
copaw mcp enable my-mcp

# 禁用客户端
copaw mcp disable my-mcp
```

---

### 5. 查看 MCP 客户端详情

```bash
copaw mcp info my-mcp
```

**输出示例：**
```
=== MCP Client: my-mcp ===

Name:         My MCP Server
Enabled:      ✓ Yes
Type:         Local
Transport:    stdio
Command:      npx -y @modelcontextprotocol/server-example

Environment Variables:
  API_KEY=****pi-key
```

---

### 6. 导出/导入 MCP 客户端配置

#### 导出所有客户端

```bash
copaw mcp export mcp-clients.json
```

#### 导出指定客户端

```bash
copaw mcp export mcp-clients.json --keys "my-mcp,remote-mcp"
```

#### 导入客户端

```bash
copaw mcp import mcp-clients.json
```

#### 导入并启用

```bash
copaw mcp import mcp-clients.json --enable
```

#### 导入并覆盖现有配置

```bash
copaw mcp import mcp-clients.json --overwrite
```

---

### 7. 交互式管理

```bash
copaw mcp interactive
```

**交互界面：**
```
=== MCP Client Management ===

  1. [✓] Memory - Memory (Local)
  2. [✓] tavily_search - tavily_mcp (Local)

  a - Add client
  r - Remove client
  e - Enable/Disable client
  i - Show client info
  q - Quit

Choice:
```

---

## 📝 JSON 配置格式

### 导出格式

```json
{
  "mcpServers": {
    "my-mcp": {
      "name": "My MCP Server",
      "description": "Local MCP client",
      "enabled": true,
      "transport": "stdio",
      "url": "",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-example"],
      "env": {
        "API_KEY": "your-api-key"
      },
      "cwd": ""
    },
    "remote-mcp": {
      "name": "Remote MCP",
      "description": "Remote MCP client",
      "enabled": true,
      "transport": "streamable_http",
      "url": "http://localhost:8000/mcp",
      "command": "",
      "args": [],
      "env": {},
      "cwd": ""
    }
  }
}
```

---

## 🔧 高级用法

### 1. 批量管理

```bash
# 导出所有客户端
copaw mcp export backup.json

# 编辑配置文件
vim backup.json

# 导入修改后的配置
copaw mcp import backup.json --overwrite
```

### 2. 环境安全管理

敏感环境变量会被自动脱敏显示：

```bash
copaw mcp info my-mcp
```

输出：
```
Environment Variables:
  API_KEY=****pi-key    # 只显示最后 4 个字符
  DB_PASSWORD=****word
```

### 3. 脚本集成

```bash
#!/bin/bash
# 批量启用客户端
for client in mcp1 mcp2 mcp3; do
  copaw mcp enable $client
done

# 检查客户端状态
copaw mcp list --all | grep "my-mcp"
```

---

## 🐛 故障排查

### 问题 1: 客户端无法启动

**检查配置：**
```bash
copaw mcp info my-mcp
```

**验证命令：**
```bash
# 对于本地客户端
which npx  # 检查命令是否存在
```

### 问题 2: 远程客户端连接失败

**检查 URL：**
```bash
curl http://localhost:8000/mcp
```

**检查传输类型：**
```bash
copaw mcp info remote-mcp
# 确认 transport 是 streamable_http 或 sse
```

### 问题 3: 环境变量未生效

**重新导入配置：**
```bash
copaw mcp import mcp-clients.json --overwrite
```

**重启应用：**
```bash
pkill -f "copaw app"
copaw app
```

---

## 📚 相关文档

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [CoPaw 文档](https://copaw.agentscope.io/docs/mcp)
- [MCP 客户端配置](https://copaw.agentscope.io/docs/mcp-clients)

---

**更新时间**: 2026-03-09  
**版本**: v0.0.5
