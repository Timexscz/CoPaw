# CoPaw Skills & MCP 版本控制分析

## 📋 目录

- [当前实现架构](#当前实现架构)
- [Skills 版本管理现状](#skills-版本管理现状)
- [MCP 版本管理现状](#mcp-版本管理现状)
- [存在的问题](#存在的问题)
- [优化方案](#优化方案)

---

## 当前实现架构

### Skills 三层结构

```
┌─────────────────────────────────────────────────────────────┐
│                    Skills 架构                               │
├─────────────────────────────────────────────────────────────┤
│  builtin_skills/ (源码内置)                                  │
│  ├── src/copaw/agents/skills/                               │
│  │   ├── pdf/                                               │
│  │   ├── docx/                                              │
│  │   └── ...                                                │
├─────────────────────────────────────────────────────────────┤
│  customized_skills/ (用户自定义)                             │
│  ├── ~/.copaw/customized_skills/                            │
│  │   ├── my_skill/                                          │
│  │   │   ├── SKILL.md                                       │
│  │   │   ├── scripts/                                       │
│  │   │   └── references/                                    │
├─────────────────────────────────────────────────────────────┤
│  active_skills/ (运行态)                                     │
│  ├── ~/.copaw/active_skills/                                │
│  │   └── (从 builtin 或 customized 同步)                     │
└─────────────────────────────────────────────────────────────┘
```

### MCP 客户端架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP 管理架构                              │
├─────────────────────────────────────────────────────────────┤
│  MCPClientManager                                            │
│  ├── _clients: Dict[str, StatefulClient]                    │
│  ├── init_from_config()                                     │
│  ├── replace_client()  # 热更新                             │
│  └── close_all()                                            │
├─────────────────────────────────────────────────────────────┤
│  MCPConfigWatcher                                            │
│  ├── 轮读 config.json                                        │
│  ├── 检测配置变化                                            │
│  └── 触发热更新                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Skills 版本管理现状

### 当前实现

#### 1. Skills Hub 版本字段

```python
# src/copaw/agents/skills_hub.py
@dataclass
class HubSkillResult:
    slug: str
    name: str
    description: str = ""
    version: str = ""      # ← 版本字段存在
    source_url: str = ""
```

**问题**: `version` 字段仅用于显示，**不用于版本追踪或更新检测**

#### 2. Skills 同步逻辑

```python
# src/copaw/agents/skills_manager.py
def sync_skills_to_working_dir(
    skill_names: list[str] | None = None,
    force: bool = False,
) -> tuple[int, int]:
    """同步技能到 active_skills"""
    
    for skill_name, skill_dir in skills_to_sync.items():
        target_dir = active_skills / skill_name
        
        # 仅检查是否存在，不检查版本变化
        if target_dir.exists() and not force:
            logger.debug("Skill already exists, skipping")
            skipped_count += 1
            continue
        
        # 直接覆盖
        shutil.copytree(skill_dir, target_dir)
```

**问题**: 
- 无版本比较
- 无变更检测
- 需要手动 `force=True` 才能更新

#### 3. GitHub 技能安装

```python
# src/copaw/agents/skills_hub.py
def install_from_github(
    owner: str,
    repo: str,
    branch: str,
    skill_path: str,
) -> HubInstallResult:
    """从 GitHub 安装技能"""
    
    # 1. 下载 SKILL.md
    content = _download_github_file(owner, repo, branch, f"{skill_path}/SKILL.md")
    
    # 2. 解析 Front Matter
    post = frontmatter.loads(content)
    skill_name = post.get("name")
    
    # 3. 写入本地
    SkillService.create_skill(
        name=skill_name,
        content=content,
        overwrite=False,  # ← 默认不覆盖
    )
```

**问题**: 
- 不记录安装的 commit/branch
- 无法检测远程更新
- 无 `update` 命令

---

## MCP 版本管理现状

### 当前实现

#### 1. MCP 配置结构

```python
# src/copaw/config/config.py
class MCPClientConfig(BaseModel):
    name: str
    description: str = ""
    enabled: bool = True
    transport: Literal["stdio", "streamable_http", "sse"]
    url: str = ""
    command: str = ""
    args: List[str] = []
    env: Dict[str, str] = {}
```

**问题**: **无 `version` 字段**，无法追踪 MCP 服务器版本

#### 2. MCP 热更新机制

```python
# src/copaw/app/mcp/manager.py
class MCPClientManager:
    async def replace_client(
        self,
        key: str,
        client_config: "MCPClientConfig",
        timeout: float = 60.0,
    ) -> None:
        """替换 MCP 客户端（热更新）"""
        
        # 1. 创建新客户端
        new_client = self._build_client(client_config)
        await new_client.connect()
        
        # 2. 交换并关闭旧客户端
        async with self._lock:
            old_client = self._clients.get(key)
            self._clients[key] = new_client
            if old_client:
                await old_client.close()
```

**优点**: 支持运行时热更新

**问题**: 
- 被动触发（依赖 config.json 变化）
- 不验证版本兼容性
- 无更新日志

#### 3. MCP 配置监控

```python
# src/copaw/app/mcp/watcher.py
class MCPConfigWatcher:
    async def watch(self):
        """轮询 config.json 检测变化"""
        
        while True:
            await asyncio.sleep(self._poll_interval)
            
            # 检测配置变化
            if self._config_changed():
                await self._reload_changed_clients()
```

**问题**: 
- 仅检测本地配置变化
- 不检查远程 MCP 服务器更新
- 无版本回滚机制

---

## 存在的问题

### Skills 版本管理问题

| 问题 | 影响 | 优先级 |
|-----|------|--------|
| **无版本锁定** | 无法重现安装的技能版本 | 🔴 高 |
| **无更新检测** | 用户不知道技能有更新 | 🔴 高 |
| **无 changelog** | 不知道更新了什么内容 | 🟡 中 |
| **GitHub 技能无 commit 追踪** | 无法追溯到具体版本 | 🟡 中 |
| **强制覆盖风险** | `force=True` 可能丢失用户修改 | 🟡 中 |

### MCP 版本管理问题

| 问题 | 影响 | 优先级 |
|-----|------|--------|
| **配置无 version 字段** | 无法记录期望版本 | 🔴 高 |
| **无协议版本检查** | 可能导致兼容性问题 | 🔴 高 |
| **被动更新** | 不主动通知服务器更新 | 🟡 中 |
| **无回滚机制** | 更新失败后恢复困难 | 🟡 中 |
| **无健康检查** | 更新后不验证可用性 | 🟡 中 |

---

## 优化方案

### 方案 1: Skills 版本锁定文件

```python
# src/copaw/agents/skills_lock.py
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

class SkillsLockManager:
    """Skills 版本锁定管理器"""
    
    def __init__(self, working_dir: Path):
        self.lock_file = working_dir / "skills.lock"
        self.skills_dir = working_dir / "active_skills"
    
    def generate_lock(self) -> dict[str, Any]:
        """生成版本锁定文件"""
        lock_data = {
            "version": 1,
            "generated_at": datetime.now().isoformat(),
            "skills": {},
        }
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            
            content = skill_md.read_text(encoding="utf-8")
            
            # 解析 Front Matter
            post = frontmatter.loads(content)
            
            lock_data["skills"][skill_dir.name] = {
                "name": post.get("name"),
                "version": post.get("version", "0.0.0"),
                "description": post.get("description"),
                "content_hash": hashlib.sha256(
                    content.encode()
                ).hexdigest(),
                "source": post.get("source", "unknown"),
                "source_url": post.get("source_url", ""),
                "installed_at": datetime.fromtimestamp(
                    skill_md.stat().st_ctime
                ).isoformat(),
            }
        
        return lock_data
    
    def save_lock(self) -> None:
        """保存锁定文件"""
        lock_data = self.generate_lock()
        self.lock_file.write_text(
            json.dumps(lock_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    
    def load_lock(self) -> dict[str, Any] | None:
        """读取锁定文件"""
        if not self.lock_file.exists():
            return None
        
        content = self.lock_file.read_text(encoding="utf-8")
        return json.loads(content)
    
    def check_updates(self, skill_name: str) -> dict[str, Any]:
        """检查技能是否有更新"""
        lock_data = self.load_lock()
        if not lock_data or skill_name not in lock_data["skills"]:
            return {"has_update": False, "reason": "Skill not in lock file"}
        
        skill_info = lock_data["skills"][skill_name]
        source_url = skill_info.get("source_url")
        
        if not source_url:
            return {"has_update": False, "reason": "No source URL"}
        
        # 检查 GitHub 源
        if "github.com" in source_url:
            return self._check_github_update(skill_info)
        
        # 检查 ClawHub 源
        if "clawhub.ai" in source_url:
            return self._check_clawhub_update(skill_info)
        
        return {"has_update": False, "reason": "Unknown source"}
    
    def _check_github_update(self, skill_info: dict) -> dict[str, Any]:
        """检查 GitHub 技能更新"""
        # 解析 GitHub URL
        owner, repo, branch, path = _extract_github_spec(
            skill_info["source_url"]
        )
        
        # 获取远程 commit hash
        remote_hash = _get_github_file_hash(
            owner, repo, branch, f"{path}/SKILL.md"
        )
        
        has_update = remote_hash != skill_info["content_hash"]
        
        return {
            "has_update": has_update,
            "local_hash": skill_info["content_hash"],
            "remote_hash": remote_hash,
            "source": "github",
        }
    
    def list_outdated_skills(self) -> list[str]:
        """列出所有有过期更新的技能"""
        outdated = []
        
        lock_data = self.load_lock()
        if not lock_data:
            return outdated
        
        for skill_name in lock_data["skills"]:
            update_info = self.check_updates(skill_name)
            if update_info.get("has_update"):
                outdated.append(skill_name)
        
        return outdated
    
    def update_skill(
        self,
        skill_name: str,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """更新单个技能"""
        lock_data = self.load_lock()
        if not lock_data or skill_name not in lock_data["skills"]:
            return {"success": False, "error": "Skill not found in lock"}
        
        skill_info = lock_data["skills"][skill_name]
        source_url = skill_info["source_url"]
        
        # 下载新版本
        if "github.com" in source_url:
            return self._update_from_github(
                skill_name, skill_info, dry_run
            )
        
        return {"success": False, "error": "Unsupported source"}
```

### 方案 2: MCP 版本追踪

```python
# src/copaw/app/mcp/version_tracker.py
import json
from datetime import datetime
from pathlib import Path
from typing import Any

class MCPVersionTracker:
    """MCP 客户端版本追踪器"""
    
    def __init__(self, working_dir: Path):
        self.tracker_file = working_dir / "mcp_versions.json"
        self.health_check_results: dict[str, Any] = {}
    
    def record_version(
        self,
        client_key: str,
        version_info: dict[str, Any],
    ) -> None:
        """记录 MCP 客户端版本信息"""
        data = self.load()
        
        data["clients"][client_key] = {
            "version": version_info.get("version", "unknown"),
            "protocol_version": version_info.get(
                "protocol_version", "unknown"
            ),
            "capabilities": version_info.get("capabilities", {}),
            "last_updated": datetime.now().isoformat(),
            "config_hash": self._hash_config(version_info),
            "health_status": "healthy",
        }
        
        self.save(data)
    
    def load(self) -> dict[str, Any]:
        """加载版本追踪数据"""
        if not self.tracker_file.exists():
            return {"clients": {}, "version": 1}
        
        content = self.tracker_file.read_text(encoding="utf-8")
        return json.loads(content)
    
    def save(self, data: dict[str, Any]) -> None:
        """保存版本追踪数据"""
        self.tracker_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    
    def check_compatibility(
        self,
        client_key: str,
        new_version_info: dict[str, Any],
    ) -> dict[str, Any]:
        """检查版本兼容性"""
        data = self.load()
        old_info = data["clients"].get(client_key, {})
        
        issues = []
        
        # 检查协议版本
        old_protocol = old_info.get("protocol_version", "")
        new_protocol = new_version_info.get("protocol_version", "")
        
        if old_protocol != new_protocol:
            issues.append({
                "type": "protocol_mismatch",
                "old": old_protocol,
                "new": new_protocol,
                "severity": "warning",
            })
        
        # 检查能力变化
        old_caps = set(old_info.get("capabilities", {}).keys())
        new_caps = set(new_version_info.get("capabilities", {}).keys())
        
        removed_caps = old_caps - new_caps
        if removed_caps:
            issues.append({
                "type": "capabilities_removed",
                "capabilities": list(removed_caps),
                "severity": "error",
            })
        
        return {
            "compatible": len([
                i for i in issues if i["severity"] == "error"
            ]) == 0,
            "issues": issues,
        }
    
    async def health_check(
        self,
        client_key: str,
        client: Any,
    ) -> dict[str, Any]:
        """执行健康检查"""
        try:
            # 调用 MCP ping 或 list_tools
            tools = await client.list_tools()
            
            result = {
                "status": "healthy",
                "tools_count": len(tools) if tools else 0,
                "latency_ms": 0,  # 可测量响应时间
                "last_check": datetime.now().isoformat(),
            }
        except Exception as e:
            result = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat(),
            }
        
        self.health_check_results[client_key] = result
        return result
    
    def list_clients(self) -> list[dict[str, Any]]:
        """列出所有追踪的客户端"""
        data = self.load()
        return [
            {"key": key, **info}
            for key, info in data["clients"].items()
        ]
    
    @staticmethod
    def _hash_config(config: dict[str, Any]) -> str:
        """计算配置哈希"""
        import hashlib
        
        config_str = json.dumps(
            config, sort_keys=True, ensure_ascii=False
        )
        return hashlib.sha256(
            config_str.encode()
        ).hexdigest()
```

### 方案 3: CLI 命令扩展

```python
# src/copaw/cli/skills_version.py
import click
from ..agents.skills_lock import SkillsLockManager
from ..constant import WORKING_DIR

@click.group()
def skills_version():
    """Skills version management commands."""
    pass

@skills_version.command()
def lock():
    """Generate or update skills.lock file."""
    lock_mgr = SkillsLockManager(WORKING_DIR)
    lock_mgr.save_lock()
    click.echo(f"✅ Generated lock file at {lock_mgr.lock_file}")

@skills_version.command()
def status():
    """Check for outdated skills."""
    lock_mgr = SkillsLockManager(WORKING_DIR)
    outdated = lock_mgr.list_outdated_skills()
    
    if outdated:
        click.echo("⚠️  Outdated skills:")
        for skill in outdated:
            click.echo(f"  - {skill}")
    else:
        click.echo("✅ All skills are up to date")

@skills_version.command()
@click.argument('skill_name')
@click.option('--dry-run', is_flag=True, help='Show what would be updated')
def update(skill_name: str, dry_run: bool):
    """Update a specific skill."""
    lock_mgr = SkillsLockManager(WORKING_DIR)
    result = lock_mgr.update_skill(skill_name, dry_run=dry_run)
    
    if result.get("success"):
        click.echo(f"✅ Updated skill: {skill_name}")
    else:
        click.echo(f"❌ Failed: {result.get('error')}")

@skills_version.command()
def upgrade_all():
    """Update all outdated skills."""
    lock_mgr = SkillsLockManager(WORKING_DIR)
    outdated = lock_mgr.list_outdated_skills()
    
    if not outdated:
        click.echo("✅ All skills are up to date")
        return
    
    click.echo(f"Updating {len(outdated)} skill(s)...")
    for skill in outdated:
        result = lock_mgr.update_skill(skill)
        status = "✅" if result.get("success") else "❌"
        click.echo(f"  {status} {skill}")

# src/copaw/cli/mcp_version.py
@click.group()
def mcp_version():
    """MCP version management commands."""
    pass

@mcp_version.command()
def status():
    """Show MCP client versions and health."""
    from ..app.mcp.version_tracker import MCPVersionTracker
    
    tracker = MCPVersionTracker(WORKING_DIR)
    clients = tracker.list_clients()
    
    if not clients:
        click.echo("No MCP clients tracked")
        return
    
    click.echo("MCP Clients:")
    for client in clients:
        status_icon = "🟢" if client.get(
            "health_status"
        ) == "healthy" else "🔴"
        click.echo(
            f"  {status_icon} {client['key']}: "
            f"v{client.get('version', 'unknown')} "
            f"(protocol: {client.get('protocol_version', '?')})"
        )

@mcp_version.command()
@click.argument('client_key')
def check(client_key: str):
    """Check for MCP server updates."""
    # 实现版本检查逻辑
    click.echo(f"Checking updates for {client_key}...")

@mcp_version.command()
@click.argument('client_key')
def rollback(client_key: str):
    """Rollback MCP client to previous version."""
    # 实现回滚逻辑
    click.echo(f"Rolling back {client_key}...")
```

### 方案 4: SKILL.md 增强

```markdown
---
name: "My Skill"
description: "What this skill does"
version: "1.2.0"           # ← 新增：语义化版本
source: "github"           # ← 新增：来源类型
source_url: "https://github.com/owner/repo/tree/main/skills/my-skill"
commit_hash: "abc123"      # ← 新增：安装时的 commit
changelog:                 # ← 新增：变更日志
  - version: "1.2.0"
    date: "2025-03-12"
    changes:
      - "Added new feature X"
      - "Fixed bug in Y"
  - version: "1.1.0"
    date: "2025-03-01"
    changes:
      - "Improved performance"
---

# My Skill

Skill content...
```

---

## 配置建议

### 环境变量

```bash
# Skills 版本控制
COPAW_SKILLS_AUTO_CHECK_UPDATES=true      # 启动时检查更新
COPAW_SKILLS_CHECK_INTERVAL=24h           # 检查间隔
COPAW_SKILLS_LOCK_ENABLED=true            # 启用锁定文件

# MCP 版本控制
COPAW_MCP_HEALTH_CHECK_INTERVAL=5m        # 健康检查间隔
COPAW_MCP_VERSION_TRACKING=true           # 启用版本追踪
COPAW_MCP_AUTO_ROLLBACK=false             # 失败自动回滚
```

### config.json 扩展

```json
{
  "skills": {
    "version_control": {
      "enabled": true,
      "auto_check": true,
      "lock_file": "skills.lock"
    }
  },
  "mcp": {
    "version_tracking": {
      "enabled": true,
      "health_check": true,
      "compatibility_check": true
    }
  }
}
```

---

## 使用示例

### Skills 版本管理

```bash
# 生成锁定文件
copaw skills version lock

# 检查过期技能
copaw skills version status

# 更新单个技能
copaw skills version update my-skill

# 更新所有技能
copaw skills version upgrade-all

# 查看技能历史
copaw skills history my-skill
```

### MCP 版本管理

```bash
# 查看版本和健康状态
copaw mcp version status

# 检查更新
copaw mcp version check tavily_search

# 兼容性检查
copaw mcp version check-compatibility

# 回滚
copaw mcp version rollback tavily_search --to 1.0.0
```

---

## 总结

### 当前状态

| 功能 | Skills | MCP |
|-----|--------|-----|
| **版本字段** | ⚠️ 存在但未使用 | ❌ 缺失 |
| **版本锁定** | ❌ 未实现 | ❌ 未实现 |
| **更新检测** | ❌ 未实现 | ❌ 未实现 |
| **热更新** | ❌ 不支持 | ✅ 已实现 |
| **健康检查** | ❌ 未实现 | ❌ 未实现 |
| **回滚机制** | ❌ 未实现 | ❌ 未实现 |
| **Changelog** | ❌ 未实现 | ❌ 未实现 |

### 优先级建议

1. **高优先级**: Skills 版本锁定（可重现安装）
2. **高优先级**: MCP 版本追踪（协议兼容性）
3. **中优先级**: 更新检测（主动通知）
4. **低优先级**: 回滚机制、Changelog

### 下一步行动

1. 实现 `SkillsLockManager` 类
2. 实现 `MCPVersionTracker` 类
3. 扩展 CLI 命令
4. 增强 SKILL.md Front Matter 规范
