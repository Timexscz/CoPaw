# CoPaw Skills 命令行工具使用指南

## 📋 命令列表

```bash
copaw skills          # Skills 管理主命令
  list                # 列出技能
  info                # 显示技能详情
  enable              # 启用技能
  disable             # 禁用技能
  config              # 交互式配置
  export              # 导出技能配置
  import              # 导入技能配置
  search              # 搜索 Hub 技能
  install             # 安装 Hub 技能
  interactive         # 交互式管理界面
```

---

## 🚀 使用示例

### 1. 列出技能

```bash
# 列出所有已启用的技能
copaw skills list

# 列出所有技能（包括已禁用的）
copaw skills list --all

# 只列出内置技能
copaw skills list --source builtin

# 只列出自定义技能
copaw skills list --source customized
```

**输出示例：**
```
Skills                                     
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name             ┃ Source  ┃ Status     ┃ Path                               ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ browser_visible  │ builtin │ ✓ Enabled  │ /root/CoPaw/src/copaw/agents/skil… │
│ cron             │ builtin │ ✗ Disabled │ /root/CoPaw/src/copaw/agents/skil… │
│ docx             │ builtin │ ✓ Enabled  │ /root/CoPaw/src/copaw/agents/skil… │
└──────────────────┴─────────┴────────────┴────────────────────────────────────┘

Total: 10 skill(s)
```

---

### 2. 查看技能详情

```bash
copaw skills info docx
```

**输出示例：**
```
=== Skill: docx ===

Name:       docx
Source:     builtin
Status:     ✓ Enabled
Path:       /root/CoPaw/src/copaw/agents/skills/docx
Description: Use this skill whenever the user wants to create Word documents...
```

---

### 3. 启用/禁用技能

```bash
# 启用技能
copaw skills enable cron

# 禁用技能
copaw skills disable news
```

---

### 4. 导出/导入技能配置

#### 导出所有技能

```bash
copaw skills export skills-config.json
```

#### 导出已启用的技能

```bash
copaw skills export skills-config.json --enabled-only
```

#### 导入技能配置

```bash
copaw skills import skills-config.json
```

#### 导入并启用技能

```bash
copaw skills import skills-config.json --enable
```

---

### 5. 搜索 Hub 技能

```bash
# 搜索技能
copaw skills search "pdf"

# 限制结果数量
copaw skills search "document" --limit 5
```

**输出示例：**
```
Searching for 'pdf'...

Search Results: pdf
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name    ┃ Description            ┃ Version ┃ Source                  ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ pdf     │ PDF processing skill   │ 1.0.0   │ https://github.com/...  │
└─────────┴────────────────────────┴─────────┴─────────────────────────┘

Total: 1 result(s)
```

---

### 6. 安装 Hub 技能

```bash
# 从 GitHub 安装
copaw skills install https://github.com/user/repo/tree/main/skills/pdf

# 指定版本
copaw skills install https://github.com/user/repo/tree/main/skills/pdf --version 1.0.0

# 安装但不启用
copaw skills install https://github.com/user/repo/pdf --no-enable

# 覆盖现有技能
copaw skills install https://github.com/user/repo/pdf --overwrite
```

---

### 7. 交互式管理

```bash
copaw skills interactive
```

**交互界面：**
```
=== Skills Management ===

   1. [✓] browser_visible       (builtin)
   2. [✗] cron                  (builtin)
   3. [✓] dingtalk_channel      (builtin)
   4. [✓] docx                  (builtin)
   5. [✓] file_reader           (builtin)

  e - Enable/Disable skill
  i - Show skill info
  s - Search hub skills
  q - Quit

Choice:
```

---

## 📝 JSON 配置格式

### 导出格式

```json
{
  "skills": [
    {
      "name": "docx",
      "source": "builtin",
      "enabled": true
    },
    {
      "name": "pdf",
      "source": "builtin",
      "enabled": true
    },
    {
      "name": "cron",
      "source": "builtin",
      "enabled": false
    }
  ]
}
```

---

## 🔧 高级用法

### 1. 批量管理技能

```bash
#!/bin/bash
# 批量启用技能
for skill in docx pdf xlsx; do
  copaw skills enable $skill
done

# 批量禁用技能
for skill in cron news; do
  copaw skills disable $skill
done
```

### 2. 备份和恢复

```bash
# 备份当前技能配置
copaw skills export skills-backup.json --enabled-only

# 恢复配置
copaw skills import skills-backup.json --enable
```

### 3. 脚本集成

```bash
#!/bin/bash
# deploy-skills.sh

# 导出生产环境配置
copaw skills export prod-skills.json --enabled-only

# 在新环境导入
copaw skills import prod-skills.json --enable

# 验证配置
copaw skills list
```

---

## 🐛 故障排查

### 问题 1: 技能无法启用

**检查技能是否存在：**
```bash
copaw skills info skill-name
```

**查看技能路径：**
```bash
copaw skills list --all | grep skill-name
```

### 问题 2: 安装技能失败

**检查 URL 格式：**
```bash
# 正确的 URL 格式
copaw skills install https://github.com/user/repo/tree/main/skills/skill-name
```

**检查网络连接：**
```bash
curl https://github.com
```

### 问题 3: 搜索无结果

**尝试不同的关键词：**
```bash
copaw skills search "document"  # 而不是 "doc"
```

**增加结果数量：**
```bash
copaw skills search "skill" --limit 20
```

---

## 📚 相关文档

- [Skills 官方文档](https://copaw.agentscope.io/docs/skills)
- [Skills Hub](https://skills.sh/)
- [自定义技能开发](https://copaw.agentscope.io/docs/skills-development)

---

**更新时间**: 2026-03-09  
**版本**: v0.0.5
