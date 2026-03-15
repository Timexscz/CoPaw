# CoPaw 用户认证配置指南

## 概述

CoPaw 现在支持用户认证功能，可以为您的 CoPaw 实例添加登录/注册保护。启用后，用户需要登录才能访问 Web Console。

## 快速开始

### 1. 启用认证

在 `.env` 文件中添加以下配置：

```bash
# 启用认证
AUTH_ENABLED=true

# 允许新用户注册（可选，默认 true）
AUTH_ALLOW_REGISTRATION=true

# JWT 密钥（可选，不设置会自动生成）
AUTH_JWT_SECRET_KEY=your-secret-key-here

# Token 过期时间（分钟，默认 1440 分钟=24 小时）
AUTH_JWT_EXPIRATION_MINUTES=1440
```

### 2. 重启 CoPaw

```bash
copaw start
# 或者
copaw restart
```

### 3. 访问 Console

打开浏览器访问 `http://localhost:8088`，您将被重定向到登录页面。

- 如果是第一次启用认证，点击 "Sign up" 创建第一个账号
- 创建账号后，可以使用该账号登录

## 配置选项

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `AUTH_ENABLED` | 是否启用认证 | `false` |
| `AUTH_ALLOW_REGISTRATION` | 是否允许新用户注册 | `true` |
| `AUTH_JWT_SECRET_KEY` | JWT 签名密钥 | 自动生成 |
| `AUTH_JWT_EXPIRATION_MINUTES` | Token 过期时间（分钟） | `1440` |

### config.json 配置

您也可以通过 `config.json` 配置认证：

```json
{
  "auth": {
    "enabled": true,
    "allow_registration": true
  }
}
```

## API 端点

认证功能提供以下 API 端点：

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息
- `GET /api/auth/status` - 获取认证状态

### 示例

#### 登录

```bash
curl -X POST http://localhost:8088/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "yourname", "password": "yourpassword"}'
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "yourname"
  }
}
```

#### 注册

```bash
curl -X POST http://localhost:8088/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "password123"}'
```

## 数据库

用户信息存储在 PostgreSQL 数据库的 `users` 表中：

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMPTZ
);
```

## 安全建议

1. **生产环境**：务必设置强 `AUTH_JWT_SECRET_KEY`
2. **HTTPS**：在生产环境中使用 HTTPS 保护传输
3. **密码策略**：建议密码至少 8 位，包含大小写字母和数字
4. **定期更新**：定期更新 JWT 密钥和用户密码

## 禁用认证

如果需要禁用认证，只需设置：

```bash
AUTH_ENABLED=false
```

然后重启 CoPaw。现有用户数据会保留，重新启用认证后仍可使用。

## 故障排除

### 问题：无法访问 Console

**症状**：启用认证后无法访问 Console

**解决方案**：
1. 检查 `AUTH_ENABLED` 设置
2. 查看日志文件 `copaw.log` 了解错误信息
3. 确保数据库连接正常

### 问题：注册失败

**症状**：注册时提示 "Registration is disabled"

**解决方案**：
1. 设置 `AUTH_ALLOW_REGISTRATION=true`
2. 或者通过 config.json 设置 `"allow_registration": true`

### 问题：Token 过期

**症状**：使用过程中提示需要重新登录

**解决方案**：
1. 增加 `AUTH_JWT_EXPIRATION_MINUTES` 值
2. 或者重新登录获取新 token

## OAuth 集成（计划中）

未来版本将支持 OAuth 提供商集成：
- GitHub OAuth
- Google OAuth
- 通用 OAuth2

配置示例（未来版本）：
```json
{
  "auth": {
    "enabled": true,
    "oauth": {
      "github": {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "redirect_uri": "http://localhost:8088/api/auth/github/callback"
      }
    }
  }
}
```

## 更多信息

- [CoPaw 文档](https://copaw.agentscope.io/)
- [GitHub 仓库](https://github.com/agentscope-ai/CoPaw)
- [问题反馈](https://github.com/agentscope-ai/CoPaw/issues)
