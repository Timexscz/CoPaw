# CoPaw 版本控制 - 5 分钟快速入门

> 无需阅读完整文档，5 分钟即可上手版本控制功能！

---

## 🚀 立即开始

### 1️⃣ Skills 版本锁定（30 秒）

```bash
# 生成技能版本锁定文件
copaw skills version lock
```

**你会看到**：
```
✅ Generated lock file: /home/user/.copaw/skills.lock
📦 Locked 5 skill(s):
   - pdf_tools v1.2.0 (builtin)
   - docx_handler v0.9.5 (builtin)
   ...
```

**作用**：记录当前所有技能的版本，便于重现和更新检测。

---

### 2️⃣ 检查技能更新（10 秒）

```bash
# 检查是否有技能可以更新
copaw skills version status
```

**如果有更新**：
```
┌─────────────────────────────┐
│    Outdated Skills          │
├──────────┬────────┬─────────┤
│ Skill    │ Source │ Details │
├──────────┼────────┼─────────┤
│ pdf_tools│ github │ Changed │
└──────────┴────────┴─────────┘
```

**如果没有更新**：
```
✅ All skills are up to date!
```

---

### 3️⃣ 保存记忆版本（10 秒）

```bash
# 保存当前 MEMORY.md 的版本
copaw memory version save MEMORY.md
```

**你会看到**：
```
✅ Saved version: /home/user/.copaw/memory/.versions/MEMORY.md.20250312_143022
```

**作用**：在重要修改前保存版本，随时可以回滚。

---

### 4️⃣ 查看 MCP 状态（10 秒）

```bash
# 查看所有 MCP 客户端的健康状态
copaw mcp version status
```

**你会看到**：
```
┌───────────────┬─────────┬──────────┬──────────────┐
│ Client        │ Version │ Protocol │ Health       │
├───────────────┼─────────┼──────────┼──────────────┤
│ tavily_search │ 1.0.5   │ 2024-11  │ 🟢 Healthy   │
│ file_server   │ 2.1.0   │ 2024-11  │ 🟢 Healthy   │
└───────────────┴─────────┴──────────┴──────────────┘
```

---

## 📋 常用命令速查

### Skills 版本

```bash
copaw skills version lock           # 生成锁定文件
copaw skills version status         # 检查更新
copaw skills version update --all   # 更新所有
copaw skills version info           # 查看信息
```

### 记忆版本

```bash
copaw memory version save MEMORY.md          # 保存版本
copaw memory version list MEMORY.md          # 查看历史
copaw memory version restore <path>          # 恢复版本
copaw memory version cleanup                 # 清理旧版本
```

### MCP 版本

```bash
copaw mcp version status          # 查看状态
copaw mcp version info <client>   # 查看详情
copaw mcp version health-check    # 健康检查
```

---

## 💡 典型使用场景

### 场景 1：更新技能前

```bash
# 1. 生成锁定文件（记录当前状态）
copaw skills version lock

# 2. 检查是否有更新
copaw skills version status

# 3. 更新所有技能
copaw skills version update --all

# 4. 如果有问题，可以重新安装锁定版本
copaw skills disable <skill>
copaw skills enable <skill>
```

---

### 场景 2：修改记忆前

```bash
# 1. 保存当前版本
copaw memory version save MEMORY.md

# 2. 进行修改...
# (通过 Agent 或手动编辑)

# 3. 如果改错了，恢复版本
copaw memory version list MEMORY.md  # 查看可用版本
copaw memory version restore <path>  # 恢复
```

---

### 场景 3：MCP 出问题

```bash
# 1. 查看状态
copaw mcp version status

# 2. 查看详细信息
copaw mcp version info tavily_search

# 3. 如果刚升级过，可以回滚
copaw mcp version rollback tavily_search 1.0.4
```

---

## 🔍 故障排除

### 问题 1：找不到命令

```bash
# 确保使用最新版本的 CoPaw
copaw --version

# 如果命令不存在，可能需要重启或重新加载
```

---

### 问题 2：没有 skills.lock 文件

```bash
# 第一次使用时需要生成
copaw skills version lock
```

---

### 问题 3：记忆目录不存在

```bash
# 确保 CoPaw 已初始化
copaw init

# 或者手动创建
mkdir -p ~/.copaw/memory
```

---

## 📖 深入学习

完成快速入门后，可以阅读：

1. **完整使用指南** → `VERSION_CONTROL_USER_GUIDE.md`
2. **策略对比分析** → `VERSION_CONTROL_STRATEGY_COMPARISON.md`
3. **技术实现细节** → `SKILLS_MCP_VERSION_CONTROL_ANALYSIS.md`

---

## ✅ 验证安装

运行验证脚本：

```bash
python verify_version_control.py
```

**期望输出**：
```
============================================================
✅ All core modules verified successfully!
============================================================
```

---

**恭喜！你已经掌握了 CoPaw 版本控制的基础！** 🎉

遇到问题？查看 `VERSION_CONTROL_USER_GUIDE.md` 获取完整文档。
