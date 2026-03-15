# CoPaw 用户认证实现总结

## 概述

为 CoPaw 添加了完整的用户认证系统，包括登录、注册、登出功能，以及前后端的认证保护。

## 实现的功能

### 后端 (Python/FastAPI)

1. **配置系统** (`src/copaw/config/`)
   - `auth.py`: 认证设置（JWT、环境变量）
   - `config.py`: 添加 `AuthConfig` 类到主配置
   - 环境变量支持：`AUTH_ENABLED`, `AUTH_ALLOW_REGISTRATION`, `AUTH_JWT_SECRET_KEY`

2. **数据库** (`src/copaw/db/`)
   - `migrations/002_users.sql`: 用户表迁移脚本
   - `database.py`: 更新以支持多表迁移

3. **认证服务** (`src/copaw/services/auth.py`)
   - 用户注册和认证
   - JWT Token 生成和验证
   - 密码哈希（PBKDF2-HMAC-SHA256）

4. **API 路由** (`src/copaw/app/routers/auth.py`)
   - `POST /api/auth/login` - 登录
   - `POST /api/auth/register` - 注册
   - `POST /api/auth/logout` - 登出
   - `GET /api/auth/me` - 获取当前用户
   - `GET /api/auth/status` - 认证状态

5. **中间件** (`src/copaw/app/_app.py`)
   - HTTP 请求认证检查
   - Token 验证
   - 白名单路径（登录页、API 文档等）

6. **依赖** (`pyproject.toml`)
   - 添加 `PyJWT>=2.8.0`
   - 添加 `pydantic-settings>=2.0.0`

### 前端 (React/TypeScript)

1. **API 客户端** (`console/src/api/`)
   - `modules/auth.ts`: 认证 API 封装
   - `config.ts`: Token 管理（localStorage）
   - `request.ts`: 401 自动跳转登录
   - `index.ts`: 导出 authApi

2. **认证上下文** (`console/src/contexts/AuthContext.tsx`)
   - 全局认证状态管理
   - 用户信息
   - 登录/注册/登出方法

3. **认证页面** (`console/src/pages/Auth/`)
   - `LoginPage.tsx`: 登录页面
   - `RegisterPage.tsx`: 注册页面
   - `Auth.css`: 样式（支持深色模式）

4. **路由保护** (`console/src/layouts/MainLayout/`)
   - 未认证用户重定向到登录页
   - 认证启用时显示登录/注册页面

5. **用户菜单** (`console/src/layouts/Header.tsx`)
   - 显示当前用户
   - 登出功能

6. **国际化** (`console/src/locales/`)
   - `en.json`: 英文翻译
   - `zh.json`: 中文翻译

## 文件清单

### 新增文件

```
src/copaw/config/auth.py
src/copaw/services/auth.py
src/copaw/db/migrations/002_users.sql
src/copaw/app/routers/auth.py
console/src/api/modules/auth.ts
console/src/contexts/AuthContext.tsx
console/src/pages/Auth/LoginPage.tsx
console/src/pages/Auth/RegisterPage.tsx
console/src/pages/Auth/Auth.css
AUTH_GUIDE.md
AUTH_IMPLEMENTATION.md (本文件)
```

### 修改文件

```
src/copaw/config/config.py          - 添加 AuthConfig
src/copaw/config/__init__.py        - 导出认证相关
src/copaw/db/database.py            - 支持多表迁移
src/copaw/app/_app.py               - 添加认证中间件
src/copaw/app/routers/__init__.py   - 注册 auth 路由
pyproject.toml                      - 添加 PyJWT 依赖
.env.example                        - 添加认证环境变量
console/src/api/index.ts            - 导出 authApi
console/src/api/config.ts           - Token 管理
console/src/api/request.ts          - 401 处理
console/src/App.tsx                 - 添加 AuthProvider
console/src/layouts/MainLayout/     - 路由保护
console/src/layouts/Header.tsx      - 用户菜单
console/src/layouts/index.module.less - 用户名样式
console/src/locales/en.json         - 英文翻译
console/src/locales/zh.json         - 中文翻译
```

## 使用方法

### 1. 启用认证

编辑 `.env` 文件：
```bash
AUTH_ENABLED=true
AUTH_ALLOW_REGISTRATION=true
```

### 2. 重启 CoPaw

```bash
copaw restart
```

### 3. 访问 Console

1. 打开浏览器访问 `http://localhost:8088`
2. 首次使用点击 "Sign up" 创建账号
3. 使用创建的账号登录

## 技术细节

### 密码安全

- 使用 PBKDF2-HMAC-SHA256 算法
- 100,000 次迭代
- 随机盐值（16 字节）

### JWT Token

- 算法：HS256
- 默认过期时间：24 小时（1440 分钟）
- 载荷：用户 ID、用户名、过期时间

### 数据库表

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMPTZ
);
```

## 安全建议

1. **生产环境**：设置强 `AUTH_JWT_SECRET_KEY`
2. **HTTPS**：使用 HTTPS 保护传输
3. **密码策略**：建议最小长度 8 位
4. **定期更新**：定期更换 JWT 密钥

## 未来计划

1. **OAuth 集成**：支持 GitHub、Google 等第三方登录
2. **双因素认证**：TOTP 支持
3. **密码重置**：邮件找回密码
4. **用户管理**：管理员界面
5. **审计日志**：记录登录历史

## 测试

### 后端测试

```bash
# 测试配置导入
python -c "from copaw.config import AuthConfig; print('OK')"

# 测试服务导入
python -c "from copaw.services.auth import user_service; print('OK')"
```

### 前端测试

```bash
cd console
npm run build
```

## 已知限制

1. 首次启用认证后，需要创建第一个账号才能使用
2. 如果忘记密码，需要手动从数据库删除用户或重置密码
3. 暂不支持 OAuth 第三方登录

## 故障排除

### 问题：无法登录

**检查项**：
1. 数据库连接是否正常
2. `users` 表是否创建成功
3. 查看 `copaw.log` 日志

### 问题：前端 401 循环

**检查项**：
1. 清除浏览器缓存
2. 检查 `AUTH_ENABLED` 设置
3. 确认 Token 格式正确

## 贡献

欢迎提交 Issue 和 Pull Request 改进认证功能！

## 许可证

Apache 2.0
