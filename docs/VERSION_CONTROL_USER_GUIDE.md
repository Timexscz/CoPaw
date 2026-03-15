# CoPaw 版本控制使用指南

> **版本控制功能** 为 CoPaw 的 Skills、记忆文件和 MCP 客户端提供版本追踪、更新检测和回滚能力。

---

## 📋 目录

- [Skills 版本控制](#skills-版本控制)
- [记忆文件版本控制](#记忆文件版本控制)
- [MCP 客户端版本追踪](#mcp-客户端版本追踪)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

---

## Skills 版本控制

### 功能概述

Skills 版本控制功能帮助你：
- 🔒 **锁定技能版本** - 记录已安装技能的精确版本
- 🔍 **检测更新** - 自动检测 GitHub/ClawHub 上的新版本
- 📦 **批量更新** - 一键更新所有过期技能
- 📜 **查看历史** - 追踪技能版本变更历史

### 命令参考

#### 1. 生成版本锁定文件

```bash
# 扫描所有 active_skills 并生成 skills.lock
copaw skills version lock
```

**输出示例**：
```
🔒 Generating skills.lock file...
✅ Generated lock file: /home/user/.copaw/skills.lock
📦 Locked 5 skill(s):
   - pdf_tools v1.2.0 (builtin)
   - docx_handler v0.9.5 (builtin)
   - my_custom_skill v1.0.0 (customized)
   ...
```

**skills.lock 文件内容**：
```json
{
  "version": 1,
  "generated_at": "2025-03-12T10:30:00",
  "skills": {
    "pdf_tools": {
      "name": "PDF Tools",
      "version": "1.2.0",
      "content_hash": "sha256:abc123...",
      "source": "builtin",
      "source_url": "https://github.com/...",
      "installed_at": "2025-03-01T08:00:00"
    }
  }
}
```

---

#### 2. 检查过期技能

```bash
# 检查所有技能是否有更新
copaw skills version status
```

**输出示例**：
```
🔍 Checking for skill updates...

┌─────────────────────────────────────────────────────┐
│                  Outdated Skills                    │
├──────────────┬──────────┬──────────────────────────┤
│ Skill        │ Source   │ Details                  │
├──────────────┼──────────┼──────────────────────────┤
│ pdf_tools    │ github   │ Content changed          │
│ my_custom    │ clawhub  │ 1.0.0 → 1.1.0            │
└──────────────┴──────────┴──────────────────────────┘

💡 Run 'copaw skills version update' to update these skills.
```

---

#### 3. 更新技能

```bash
# 更新单个技能
copaw skills version update pdf_tools

# 更新所有过期技能
copaw skills version update --all

# 预览更新（不实际执行）
copaw skills version update --all --dry-run
```

**输出示例**：
```
🔍 Checking updates for pdf_tools...
✅ Updated: pdf_tools
   Successfully updated from GitHub
```

---

#### 4. 查看版本历史

```bash
# 查看技能的版本历史
copaw skills version history pdf_tools
```

**输出示例**：
```
📋 Version History: pdf_tools

Current Version: 1.2.0
Source: github
Installed At: 2025-03-01T08:00:00

⚠️  Full version history coming soon.
```

---

#### 5. 查看锁定文件信息

```bash
# 查看 skills.lock 基本信息
copaw skills version info

# 显示完整路径
copaw skills version info --show-path
```

---

#### 6. 比较差异（即将推出）

```bash
# 比较本地变化
copaw skills version diff pdf_tools

# 与远程版本比较
copaw skills version diff pdf_tools --remote
```

---

## 记忆文件版本控制

### 功能概述

记忆文件版本控制功能帮助你：
- 💾 **保存版本** - 手动保存记忆文件的任意版本
- 📜 **查看历史** - 列出所有可用版本
- ⏪ **恢复版本** - 回滚到任意历史版本
- 📊 **比较差异** - 查看版本间的变化

### 命令参考

#### 1. 保存当前版本

```bash
# 保存 MEMORY.md 的当前版本
copaw memory version save MEMORY.md

# 保存每日日志版本
copaw memory version save 2025-03-12.md
```

**输出示例**：
```
✅ Saved version: /home/user/.copaw/memory/.versions/MEMORY.md.20250312_143022
```

**版本文件结构**：
```
~/.copaw/memory/
├── MEMORY.md
├── 2025-03-12.md
└── .versions/
    ├── MEMORY.md.20250312_143022
    ├── MEMORY.md.20250312_150000
    └── 2025-03-12.md.20250312_160000
```

---

#### 2. 查看版本历史

```bash
# 列出 MEMORY.md 的所有版本
copaw memory version list MEMORY.md

# 限制显示数量
copaw memory version list MEMORY.md --limit 5
```

**输出示例**：
```
┌──────────────────────────────────────────────────────┐
│              Versions of MEMORY.md                   │
├───────┬──────────────────┬──────────────┬───────────┤
│ Index │ Timestamp        │ Message      │ Size      │
├───────┼──────────────────┼──────────────┼───────────┤
│     1 │ 2025-03-12T15:00 │ Manual save  │ 1234 chars│
│     2 │ 2025-03-12T14:30 │ Auto backup  │ 1100 chars│
│     3 │ 2025-03-12T14:00 │ -            │ 980 chars │
└───────┴──────────────────┴──────────────┴───────────┘

💡 Use 'copaw memory version restore' to restore a version.
```

---

#### 3. 恢复版本

```bash
# 恢复到指定版本
copaw memory version restore /path/to/version

# 恢复时不创建备份
copaw memory version restore /path/to/version --no-backup
```

**输出示例**：
```
✅ Restored: /home/user/.copaw/memory/MEMORY.md
   (Backup created before restore)
```

---

#### 4. 比较版本差异

```bash
# 比较两个版本
copaw memory version diff <version1_path> <version2_path>

# 比较版本与当前文件
copaw memory version diff-current <version_path>
```

**输出示例**：
```
📊 Version Diff:

--- /path/to/version1
+++ /path/to/version2
@@ -1,5 +1,6 @@
 # Memory

-Old content line.
+New content line.
+Added new line.

 Some existing content.
```

---

#### 5. 清理旧版本

```bash
# 清理旧版本（保留最近 10 个）
copaw memory version cleanup

# 预览清理结果
copaw memory version cleanup --dry-run

# 自定义保留数量
copaw memory version cleanup --max-versions 5
```

**输出示例**：
```
🧹 Cleaning up old versions (keeping max 10 per file)...

🗑️  Deleted 5 version(s):
   - /home/user/.copaw/memory/.versions/MEMORY.md.20250310_100000
   - /home/user/.copaw/memory/.versions/MEMORY.md.20250309_100000
   ...

📦 Kept 10 version(s).

(Dry run - no changes made)
```

---

#### 6. 查看系统信息

```bash
copaw memory version info
```

**输出示例**：
```
📊 Memory Version Information

Memory Directory: /home/user/.copaw/memory
Version Directory: /home/user/.copaw/memory/.versions
Max Versions Per File: 10
Total Versions Stored: 25
```

---

## MCP 客户端版本追踪

### 功能概述

MCP 客户端版本追踪功能帮助你：
- 📊 **追踪版本** - 记录 MCP 客户端版本和协议版本
- 🏥 **健康检查** - 监控客户端健康状态
- ⚠️ **兼容性检查** - 检测版本变更的兼容性问题
- ⏪ **版本回滚** - 回滚到历史版本

### 命令参考

#### 1. 查看客户端状态

```bash
# 查看所有 MCP 客户端版本和健康状态
copaw mcp version status
```

**输出示例**：
```
┌────────────────────────────────────────────────────────────────────────┐
│                           MCP Clients                                  │
├──────────────┬─────────┬──────────┬─────────────┬───────┬──────────────┤
│ Client       │ Version │ Protocol │ Health      │ Tools │ Last Updated │
├──────────────┼─────────┼──────────┼─────────────┼───────┼──────────────┤
│ tavily_search│ 1.0.5   │ 2024-11  │ 🟢 Healthy  │ 1     │ 15ms         │
│ file_server  │ 2.1.0   │ 2024-11  │ 🟢 Healthy  │ 5     │ 23ms         │
│ database     │ 0.9.0   │ 2024-01  │ 🔴 Unhealthy│ -     │ -            │
└──────────────┴─────────┴──────────┴─────────────┴───────┴──────────────┘

📊 Summary: 2/3 clients healthy
```

---

#### 2. 查看客户端详情

```bash
# 查看特定客户端的详细信息
copaw mcp version info tavily_search
```

**输出示例**：
```
📋 MCP Client Information: tavily_search

Version: 1.0.5
Protocol Version: 2024-11-05
Health Status: healthy
Last Updated: 2025-03-12T10:30:00

Capabilities:
   ✓ tools
   ✓ resources
   ✗ prompts

Version History (3 entries):
   - v1.0.5 (2025-03-12T10:30)
   - v1.0.4 (2025-03-10T08:00)
   - v1.0.3 (2025-03-05T14:20)

Health History (15 checks):
   Last: healthy, Latency: 15ms
```

---

#### 3. 检查更新

```bash
# 检查特定客户端是否有更新
copaw mcp version check tavily_search
```

**输出示例**：
```
🔍 Checking updates for tavily_search...
⚠️  Version check not yet implemented for this client.
Feature coming soon.
```

---

#### 4. 版本回滚

```bash
# 回滚到指定版本
copaw mcp version rollback tavily_search 1.0.4

# 跳过确认
copaw mcp version rollback tavily_search 1.0.4 --yes
```

**输出示例**：
```
📋 Rollback Information:

Client: tavily_search
Current Version: 1.0.5
Target Version: 1.0.4

⚠️  This will update the tracker record.
You need to reconfigure the client manually.
Continue? [y/N]: y

✅ Rolled back tavily_search:
   1.0.5 → 1.0.4

💡 Note: You need to manually reconfigure the client to apply the rollback.
```

---

#### 5. 健康检查

```bash
# 运行健康检查
copaw mcp version health-check

# 自定义检查间隔
copaw mcp version health-check --interval 120

# 自定义超时
copaw mcp version health-check --timeout 30
```

---

#### 6. 查看追踪器信息

```bash
copaw mcp version info
```

**输出示例**：
```
📊 MCP Version Tracker Information

Tracker File: /home/user/.copaw/mcp_versions.json
Health Check Interval: 300s
Total Clients Tracked: 3
Tracker Version: 1
```

---

## 最佳实践

### Skills 版本管理

#### 1. 定期生成锁定文件

```bash
# 在 CI/CD 流程中生成锁定文件
copaw skills version lock

# 提交到版本控制
git add skills.lock
```

#### 2. 部署前检查更新

```bash
# 部署前检查是否有更新
copaw skills version status

# 如果有更新，评估后再升级
copaw skills version update --all --dry-run
```

#### 3. 自定义技能版本追踪

在 `SKILL.md` 中添加完整元数据：

```yaml
---
name: "My Skill"
version: "1.2.0"           # 语义化版本
source: "github"
source_url: "https://github.com/owner/repo/tree/main/skills/my-skill"
commit_hash: "abc123"      # 安装时的 commit
changelog:
  - version: "1.2.0"
    date: "2025-03-12"
    changes:
      - "Added feature X"
      - "Fixed bug Y"
---
```

---

### 记忆文件版本管理

#### 1. 重要修改前保存版本

```bash
# 在批量修改记忆前保存当前状态
copaw memory version save MEMORY.md
```

#### 2. 定期清理旧版本

```bash
# 每周清理一次，保留最近 10 个版本
copaw memory version cleanup --max-versions 10
```

#### 3. 使用有意义的版本消息

```bash
# 在代码中保存版本时添加消息
from copaw.agents.memory.version_manager import MEMORY_VERSION_MANAGER

MEMORY_VERSION_MANAGER.save_version(
    "MEMORY.md",
    message="Before refactoring project structure",
)
```

---

### MCP 客户端版本管理

#### 1. 监控健康状态

```bash
# 定期检查健康状态
copaw mcp version status

# 在监控系统中集成健康检查
```

#### 2. 记录版本变更

在 `config.json` 中记录 MCP 客户端版本：

```json
{
  "mcp": {
    "clients": {
      "tavily_search": {
        "name": "Tavily Search",
        "command": "npx",
        "args": ["-y", "tavily-mcp@1.0.5"],  // 锁定版本
        "enabled": true
      }
    }
  }
}
```

#### 3. 升级前检查兼容性

```bash
# 升级前查看当前配置
copaw mcp version info tavily_search

# 评估兼容性变更
# 检查 protocol_version 是否变化
# 检查 capabilities 是否有移除
```

---

## 故障排除

### Skills 版本控制

#### 问题 1：找不到 skills.lock 文件

**症状**：
```
⚠️  No skills.lock file found.
```

**解决方案**：
```bash
# 生成锁定文件
copaw skills version lock
```

---

#### 问题 2：技能更新失败

**症状**：
```
❌ Failed: Installation returned failure.
```

**解决方案**：
```bash
# 检查网络连接
ping github.com

# 检查 GitHub token（如果有速率限制）
export GITHUB_TOKEN=your_token

# 手动更新技能
copaw skills disable skill_name
copaw skills enable skill_name
```

---

### 记忆文件版本控制

#### 问题 1：找不到记忆文件

**症状**：
```
❌ Memory file not found: MEMORY.md
```

**解决方案**：
```bash
# 检查记忆目录
ls -la ~/.copaw/memory/

# 创建记忆文件
echo "# Memory" > ~/.copaw/memory/MEMORY.md
```

---

#### 问题 2：版本目录占用过大

**症状**：
```bash
du -sh ~/.copaw/memory/.versions/
# 输出：500M  版本目录
```

**解决方案**：
```bash
# 清理旧版本，保留最近 5 个
copaw memory version cleanup --max-versions 5

# 或者手动清理
rm -rf ~/.copaw/memory/.versions/*
```

---

### MCP 客户端版本追踪

#### 问题 1：客户端显示 unhealthy

**症状**：
```
database  0.9.0  2024-01  🔴 Unhealthy  -  -
```

**解决方案**：
```bash
# 检查 MCP 客户端配置
copaw mcp status

# 重启 MCP 客户端
# 修改 config.json 禁用再启用

# 检查服务端日志
journalctl -u mcp-server
```

---

#### 问题 2：健康检查超时

**症状**：
```
Health check timeout (10s)
```

**解决方案**：
```bash
# 增加超时时间
copaw mcp version health-check --timeout 30

# 检查网络延迟
ping mcp-server-host

# 检查服务端负载
top  # 在服务端执行
```

---

## API 参考

### Python API

#### SkillsLockManager

```python
from copaw.agents.skills_lock import SkillsLockManager
from copaw.constant import WORKING_DIR

# 初始化
lock_mgr = SkillsLockManager(WORKING_DIR)

# 生成锁定文件
lock_mgr.save_lock()

# 检查更新
update_info = lock_mgr.check_updates("pdf_tools")
if update_info.get("has_update"):
    print("Update available!")

# 更新技能
result = lock_mgr.update_skill("pdf_tools")
```

---

#### MemoryVersionManager

```python
from copaw.agents.memory.version_manager import MemoryVersionManager
from copaw.constant import MEMORY_DIR

# 初始化
version_mgr = MemoryVersionManager(MEMORY_DIR, max_versions=10)

# 保存版本
version_path = version_mgr.save_version(
    "MEMORY.md",
    message="Before major changes",
)

# 查看历史
versions = version_mgr.list_versions("MEMORY.md")

# 恢复版本
version_mgr.restore_version(versions[0]["path"])

# 比较差异
diff = version_mgr.diff_versions(versions[0]["path"], versions[1]["path"])
```

---

#### MCPVersionTracker

```python
from copaw.app.mcp.version_tracker import MCPVersionTracker
from copaw.constant import WORKING_DIR

# 初始化
tracker = MCPVersionTracker(WORKING_DIR)

# 记录版本
tracker.record_version(
    "tavily_search",
    {
        "version": "1.0.5",
        "protocol_version": "2024-11-05",
        "capabilities": {"tools": True},
    },
)

# 健康检查
result = await tracker.health_check("tavily_search", client)

# 检查兼容性
compat = tracker.check_compatibility(
    "tavily_search",
    {"version": "2.0.0"},
)
```

---

## 相关文档

- [Skills 管理指南](./skills.zh.md)
- [记忆系统文档](./memory.zh.md)
- [MCP 配置指南](./mcp.zh.md)
- [版本控制策略对比](./VERSION_CONTROL_STRATEGY_COMPARISON.md)

---

**文档版本**: 1.0.0  
**创建日期**: 2025-03-12  
**最后更新**: 2025-03-12
