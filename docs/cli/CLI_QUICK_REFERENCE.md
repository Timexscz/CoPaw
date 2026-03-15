# CoPaw CLI 快速参考

## MCP 命令速查

```bash
# 列出客户端
copaw mcp list
copaw mcp list --all

# 添加客户端
copaw mcp add my-mcp --name "My MCP" --type local --command npx --args "-y,@mcp/server"
copaw mcp add remote-mcp --name "Remote" --type remote --url http://localhost:8000/mcp

# 管理客户端
copaw mcp enable my-mcp
copaw mcp disable my-mcp
copaw mcp remove my-mcp

# 查看详情
copaw mcp info my-mcp

# 导入导出
copaw mcp export backup.json
copaw mcp import backup.json --overwrite

# 交互模式
copaw mcp interactive
```

---

## Skills 命令速查

```bash
# 列出技能
copaw skills list
copaw skills list --all
copaw skills list --source builtin

# 管理技能
copaw skills enable docx
copaw skills disable cron
copaw skills info docx

# 搜索和安装
copaw skills search "pdf"
copaw skills install https://github.com/user/skill

# 导入导出
copaw skills export config.json --enabled-only
copaw skills import config.json --enable

# 交互模式
copaw skills interactive
```

---

## 常用场景

### 场景 1: 添加 Tavily 搜索
```bash
copaw mcp add tavily \
  --name "Tavily Search" \
  --type local \
  --command npx \
  --args "-y,tavily-mcp" \
  --env "TAVILY_API_KEY=your-key"
```

### 场景 2: 批量启用技能
```bash
for skill in docx pdf xlsx pptx; do
  copaw skills enable $skill
done
```

### 场景 3: 备份配置
```bash
# 备份 MCP 配置
copaw mcp export mcp-backup.json

# 备份 Skills 配置
copaw skills export skills-backup.json --enabled-only
```

### 场景 4: 恢复配置
```bash
# 恢复 MCP
copaw mcp import mcp-backup.json --overwrite

# 恢复 Skills
copaw skills import skills-backup.json --enable
```

---

## 输出示例

### MCP List
```
MCP Clients                           
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Key           ┃ Name       ┃ Type  ┃ Status    ┃ Description ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Memory        │ Memory     │ Local │ ✓ Enabled │ -           │
│ tavily_search │ tavily_mcp │ Local │ ✓ Enabled │ -           │
└───────────────┴────────────┴───────┴───────────┴─────────────┘
```

### Skills List
```
Skills                                     
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name             ┃ Source  ┃ Status     ┃ Path                               ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ browser_visible  │ builtin │ ✓ Enabled  │ /root/CoPaw/src/copaw/agents/skil… │
│ cron             │ builtin │ ✗ Disabled │ /root/CoPaw/src/copaw/agents/skil… │
│ docx             │ builtin │ ✓ Enabled  │ /root/CoPaw/src/copaw/agents/skil… │
└──────────────────┴─────────┴────────────┴────────────────────────────────────┘
```

---

## 帮助命令

```bash
# 查看帮助
copaw --help
copaw mcp --help
copaw skills --help

# 查看子命令帮助
copaw mcp add --help
copaw skills install --help
```

---

**打印此页面作为快速参考！**
