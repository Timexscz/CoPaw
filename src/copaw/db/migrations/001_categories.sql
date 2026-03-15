-- 分类表
CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(10) NOT NULL,
    color VARCHAR(20) NOT NULL,
    keywords JSONB NOT NULL DEFAULT '[]',
    priority INTEGER NOT NULL DEFAULT 0,
    is_custom BOOLEAN NOT NULL DEFAULT FALSE,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    category_type VARCHAR(20) NOT NULL CHECK (category_type IN ('skill', 'mcp')),
    matcher_type VARCHAR(20) CHECK (matcher_type IN ('keyword', 'transport')),
    matcher_config JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 技能分类映射表
CREATE TABLE IF NOT EXISTS skill_category_map (
    skill_name VARCHAR(255) PRIMARY KEY,
    category_id VARCHAR(50) NOT NULL REFERENCES categories(id),
    ai_confidence INTEGER,
    is_manual BOOLEAN NOT NULL DEFAULT FALSE,
    matched_keywords JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- MCP 分类映射表
CREATE TABLE IF NOT EXISTS mcp_category_map (
    client_key VARCHAR(255) PRIMARY KEY,
    category_id VARCHAR(50) NOT NULL REFERENCES categories(id),
    ai_confidence INTEGER,
    is_manual BOOLEAN NOT NULL DEFAULT FALSE,
    matched_keywords JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 索引（如果不存在则创建）
CREATE INDEX IF NOT EXISTS idx_categories_type_priority ON categories(category_type, priority DESC);
CREATE INDEX IF NOT EXISTS idx_categories_enabled ON categories(category_type, is_enabled) WHERE is_enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_skill_category ON skill_category_map(category_id);
CREATE INDEX IF NOT EXISTS idx_mcp_category ON mcp_category_map(category_id);
CREATE INDEX IF NOT EXISTS idx_categories_keywords ON categories USING GIN(keywords);
CREATE INDEX IF NOT EXISTS idx_skill_matched_keywords ON skill_category_map USING GIN(matched_keywords);

-- 触发器：自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skill_category_map_updated_at BEFORE UPDATE ON skill_category_map
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_category_map_updated_at BEFORE UPDATE ON mcp_category_map
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初始化默认技能分类（如果不存在则插入）
INSERT INTO categories (id, name, icon, color, keywords, priority, is_custom, is_enabled, category_type) VALUES
    ('document', '文档处理', '📄', '#1890ff', '["docx","word","document","pdf","pptx","xlsx","excel","文档"]', 10, FALSE, TRUE, 'skill'),
    ('communication', '通讯工具', '📧', '#52c41a', '["email","imap","smtp","mail","dingtalk","discord","telegram","slack","邮件","通讯"]', 9, FALSE, TRUE, 'skill'),
    ('automation', '自动化', '⚙️', '#fa8c16', '["cron","schedule","定时","automation","automated","定时任务","计划任务","自动化"]', 9, FALSE, TRUE, 'skill'),
    ('browser', '浏览器', '🌐', '#722ed1', '["browser","web","http","url","navigate","click","snapshot","浏览器","网页"]', 9, FALSE, TRUE, 'skill'),
    ('media', '媒体处理', '🎵', '#eb2f96', '["audio","video","music","himalaya","podcast","image","photo","media","音频","视频","音乐","媒体"]', 8, FALSE, TRUE, 'skill'),
    ('news', '新闻资讯', '📰', '#faad14', '["news","article","rss","feed","headline","新闻","资讯","文章","订阅"]', 7, FALSE, TRUE, 'skill'),
    ('lifestyle', '生活服务', '🌟', '#13c2c2', '["weather","forecast","calendar","event","reminder","shopping","food","restaurant","travel","天气","日历","提醒","生活"]', 6, FALSE, TRUE, 'skill'),
    ('productivity', '效率工具', '📊', '#2f54eb', '["note","todo","task","project","manage","search","find","organize","笔记","待办","任务","管理","搜索","效率"]', 6, FALSE, TRUE, 'skill'),
    ('development', '开发工具', '💻', '#52c41a', '["code","git","github","api","database","sql","debug","test","deploy","代码","开发","数据库","API","测试"]', 5, FALSE, TRUE, 'skill'),
    ('ai', 'AI 工具', '🤖', '#722ed1', '["llm","model","ai","chatbot","generate","embedding","vector","ml","人工智能","模型","生成","机器学习"]', 5, FALSE, TRUE, 'skill'),
    ('other', '其他', '📦', '#d9d9d9', '[]', 0, FALSE, TRUE, 'skill')
ON CONFLICT (id) DO NOTHING;

-- 初始化默认 MCP 分类（如果不存在则插入）
INSERT INTO categories (id, name, icon, color, keywords, priority, is_custom, is_enabled, category_type, matcher_type) VALUES
    ('database', '数据库', '🗄️', '#722ed1', '["postgres","mysql","sqlite","mongo","redis","database","sql"]', 10, FALSE, TRUE, 'mcp', 'keyword'),
    ('filesystem', '文件系统', '📁', '#faad14', '["file","filesystem","storage","disk"]', 9, FALSE, TRUE, 'mcp', 'keyword'),
    ('api', 'API 集成', '🔌', '#13c2c2', '["api","rest","graphql","webhook"]', 8, FALSE, TRUE, 'mcp', 'keyword'),
    ('ai', 'AI 服务', '🤖', '#eb2f96', '["llm","model","ai","embedding","chat","openai","anthropic"]', 7, FALSE, TRUE, 'mcp', 'keyword'),
    ('productivity', '效率工具', '📊', '#2f54eb', '["calendar","todo","task","note","notion","slack"]', 6, FALSE, TRUE, 'mcp', 'keyword'),
    ('local', '本地服务', '💻', '#1890ff', '[]', 5, FALSE, TRUE, 'mcp', 'transport'),
    ('remote_http', '远程 HTTP', '🌐', '#52c41a', '[]', 4, FALSE, TRUE, 'mcp', 'transport'),
    ('remote_sse', '远程 SSE', '📡', '#fa8c16', '[]', 3, FALSE, TRUE, 'mcp', 'transport'),
    ('other', '其他', '📦', '#d9d9d9', '[]', 0, FALSE, TRUE, 'mcp', 'keyword')
ON CONFLICT (id) DO NOTHING;
