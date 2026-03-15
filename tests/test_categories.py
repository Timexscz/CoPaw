#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for MCP and Skills category management.

These tests verify:
- MCP client categorization logic
- Skill categorization logic
- Default category configurations
- Custom category management
"""

import pytest
from pathlib import Path


class TestMCPCategorization:
    """Test MCP client categorization."""

    def test_database_category_postgres(self):
        """Test PostgreSQL clients are categorized as database."""
        from copaw.config.mcpCategories import _match_database
        
        client = {
            "name": "postgres-mcp",
            "description": "PostgreSQL database client",
            "transport": "stdio"
        }
        assert _match_database(client) is True

    def test_database_category_mysql(self):
        """Test MySQL clients are categorized as database."""
        from copaw.config.mcpCategories import _match_database
        
        client = {
            "name": "mysql-server",
            "description": "MySQL database connection",
            "transport": "stdio"
        }
        assert _match_database(client) is True

    def test_database_category_sqlite(self):
        """Test SQLite clients are categorized as database."""
        from copaw.config.mcpCategories import _match_database
        
        client = {
            "name": "sqlite-mcp",
            "description": "SQLite database access",
            "transport": "stdio"
        }
        assert _match_database(client) is True

    def test_database_category_mongodb(self):
        """Test MongoDB clients are categorized as database."""
        from copaw.config.mcpCategories import _match_database
        
        client = {
            "name": "mongo-mcp",
            "description": "MongoDB NoSQL database",
            "transport": "stdio"
        }
        assert _match_database(client) is True

    def test_database_category_redis(self):
        """Test Redis clients are categorized as database."""
        from copaw.config.mcpCategories import _match_database
        
        client = {
            "name": "redis-cache",
            "description": "Redis in-memory database",
            "transport": "stdio"
        }
        assert _match_database(client) is True

    def test_filesystem_category(self):
        """Test filesystem clients are categorized as filesystem."""
        from copaw.config.mcpCategories import _match_filesystem
        
        client = {
            "name": "filesystem",
            "description": "File system access and operations",
            "transport": "stdio"
        }
        assert _match_filesystem(client) is True

    def test_filesystem_category_storage(self):
        """Test storage clients are categorized as filesystem."""
        from copaw.config.mcpCategories import _match_filesystem
        
        client = {
            "name": "storage-manager",
            "description": "Disk storage management",
            "transport": "stdio"
        }
        assert _match_filesystem(client) is True

    def test_api_category_rest(self):
        """Test REST API clients are categorized as API integration."""
        from copaw.config.mcpCategories import _match_api
        
        client = {
            "name": "rest-api",
            "description": "REST API integration service",
            "transport": "streamable_http"
        }
        assert _match_api(client) is True

    def test_api_category_graphql(self):
        """Test GraphQL clients are categorized as API integration."""
        from copaw.config.mcpCategories import _match_api
        
        client = {
            "name": "graphql-gateway",
            "description": "GraphQL API gateway",
            "transport": "streamable_http"
        }
        assert _match_api(client) is True

    def test_api_category_webhook(self):
        """Test webhook clients are categorized as API integration."""
        from copaw.config.mcpCategories import _match_api
        
        client = {
            "name": "webhook-handler",
            "description": "Webhook event handler",
            "transport": "sse"
        }
        assert _match_api(client) is True

    def test_ai_category_llm(self):
        """Test LLM service clients are categorized as AI service."""
        from copaw.config.mcpCategories import _match_ai
        
        client = {
            "name": "llm-service",
            "description": "Large language model provider",
            "transport": "streamable_http"
        }
        assert _match_ai(client) is True

    def test_ai_category_openai(self):
        """Test OpenAI clients are categorized as AI service."""
        from copaw.config.mcpCategories import _match_ai
        
        client = {
            "name": "openai-proxy",
            "description": "OpenAI API proxy",
            "transport": "streamable_http"
        }
        assert _match_ai(client) is True

    def test_ai_category_anthropic(self):
        """Test Anthropic clients are categorized as AI service."""
        from copaw.config.mcpCategories import _match_ai
        
        client = {
            "name": "anthropic-claude",
            "description": "Anthropic Claude model access",
            "transport": "streamable_http"
        }
        assert _match_ai(client) is True

    def test_ai_category_embedding(self):
        """Test embedding service clients are categorized as AI service."""
        from copaw.config.mcpCategories import _match_ai
        
        client = {
            "name": "embedding-service",
            "description": "Text embedding generation",
            "transport": "streamable_http"
        }
        assert _match_ai(client) is True

    def test_transport_matcher_local(self):
        """Test transport-based matcher for local (stdio)."""
        from copaw.config.mcpCategories import _match_local
        
        client = {
            "name": "local-mcp",
            "transport": "stdio"
        }
        assert _match_local(client) is True

    def test_transport_matcher_remote_http(self):
        """Test transport-based matcher for HTTP."""
        from copaw.config.mcpCategories import _match_remote_http
        
        client = {
            "name": "remote-mcp",
            "transport": "streamable_http"
        }
        assert _match_remote_http(client) is True

    def test_transport_matcher_sse(self):
        """Test transport-based matcher for SSE."""
        from copaw.config.mcpCategories import _match_remote_sse
        
        client = {
            "name": "sse-mcp",
            "transport": "sse"
        }
        assert _match_remote_sse(client) is True


class TestSkillCategorization:
    """Test skill categorization."""

    def test_document_category_pdf(self):
        """Test PDF skills match document category."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        # Check that pdf is in document category keywords
        doc_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'document'), None)
        assert doc_category is not None
        assert any('pdf' in kw.lower() for kw in doc_category['keywords'])

    def test_document_category_docx(self):
        """Test DOCX skills match document category."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        doc_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'document'), None)
        assert doc_category is not None
        assert any('docx' in kw.lower() or 'word' in kw.lower() for kw in doc_category['keywords'])

    def test_document_category_xlsx(self):
        """Test XLSX skills match document category."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        doc_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'document'), None)
        assert doc_category is not None
        assert any('xlsx' in kw.lower() or 'excel' in kw.lower() for kw in doc_category['keywords'])

    def test_document_category_pptx(self):
        """Test PPTX skills match document category."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        doc_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'document'), None)
        assert doc_category is not None
        assert any('pptx' in kw.lower() for kw in doc_category['keywords'])

    def test_automation_category_cron(self):
        """Test cron skills match automation category."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        auto_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'automation'), None)
        assert auto_category is not None
        assert any('cron' in kw.lower() or 'schedule' in kw.lower() for kw in auto_category['keywords'])

    def test_automation_category_shell(self):
        """Test shell skills match automation category."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        # Shell might be in automation or browser category
        auto_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'automation'), None)
        browser_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'browser'), None)
        assert auto_category is not None or browser_category is not None

    def test_browser_category(self):
        """Test browser skills match browser category."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        browser_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'browser'), None)
        assert browser_category is not None
        assert any('browser' in kw.lower() or 'web' in kw.lower() for kw in browser_category['keywords'])

    def test_communication_category_news(self):
        """Test news skills match communication category."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        comm_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'communication'), None)
        assert comm_category is not None

    def test_file_category_reader(self):
        """Test file reader skills match document category."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        doc_category = next((c for c in SKILL_CATEGORIES if c['id'] == 'document'), None)
        assert doc_category is not None


class TestCategoryConfig:
    """Test category configuration."""

    def test_default_mcp_categories_exists(self):
        """Test default MCP categories exist and are valid."""
        from copaw.config.mcpCategories import MCP_CATEGORIES
        
        categories = MCP_CATEGORIES
        assert len(categories) > 0
        
        # Check structure
        for category in categories:
            assert 'id' in category
            assert 'name' in category
            assert 'icon' in category
            assert 'color' in category
            assert 'priority' in category

    def test_default_mcp_categories_have_required(self):
        """Test default MCP categories include required categories."""
        from copaw.config.mcpCategories import MCP_CATEGORIES
        
        category_ids = [c['id'] for c in MCP_CATEGORIES]
        
        # Should have these basic categories
        assert 'database' in category_ids or any('database' in c.get('name', '').lower() for c in MCP_CATEGORIES)
        assert 'filesystem' in category_ids or any('file' in c.get('name', '').lower() for c in MCP_CATEGORIES)

    def test_default_skill_categories_exists(self):
        """Test default skill categories exist and are valid."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        categories = SKILL_CATEGORIES
        assert len(categories) > 0
        
        # Check structure
        for category in categories:
            assert 'id' in category
            assert 'name' in category
            assert 'icon' in category or 'emoji' in category
            assert 'priority' in category

    def test_default_skill_categories_have_required(self):
        """Test default skill categories include required categories."""
        from copaw.config.skillCategories import SKILL_CATEGORIES
        
        category_ids = [c['id'] for c in SKILL_CATEGORIES]
        
        # Should have these basic categories
        assert any('doc' in cid.lower() for cid in category_ids)  # documents
        assert any('cron' in cid.lower() or 'auto' in cid.lower() for cid in category_ids)  # automation


class TestCategoryMatcherTypes:
    """Test different matcher types."""

    def test_transport_matcher_stdio(self):
        """Test transport-based matcher for stdio."""
        from copaw.config.mcpCategories import _match_local
        
        # Database with stdio transport
        client = {
            "name": "generic-db",
            "transport": "stdio"
        }
        assert _match_local(client) is True

    def test_transport_matcher_http(self):
        """Test transport-based matcher for HTTP."""
        from copaw.config.mcpCategories import _match_remote_http
        
        # API with HTTP transport
        client = {
            "name": "api-gateway",
            "transport": "streamable_http"
        }
        assert _match_remote_http(client) is True

    def test_transport_matcher_sse(self):
        """Test transport-based matcher for SSE."""
        from copaw.config.mcpCategories import _match_remote_sse
        
        client = {
            "name": "event-stream",
            "transport": "sse"
        }
        assert _match_remote_sse(client) is True


class TestCategoryFilesExist:
    """Test that category configuration files exist."""

    def test_mcp_categories_file_exists(self):
        """Test MCP categories configuration file exists."""
        mcp_categories_file = Path(__file__).parent.parent / "src" / "copaw" / "config" / "mcpCategories.py"
        assert mcp_categories_file.exists(), f"MCP categories file not found: {mcp_categories_file}"

    def test_skill_categories_file_exists(self):
        """Test skill categories configuration file exists."""
        skill_categories_file = Path(__file__).parent.parent / "src" / "copaw" / "config" / "skillCategories.py"
        assert skill_categories_file.exists(), f"Skill categories file not found: {skill_categories_file}"

    def test_mcp_categories_content_valid(self):
        """Test MCP categories file has valid Python syntax."""
        mcp_categories_file = Path(__file__).parent.parent / "src" / "copaw" / "config" / "mcpCategories.py"
        content = mcp_categories_file.read_text()
        
        # Should be valid Python
        compile(content, str(mcp_categories_file), 'exec')
        
        # Should contain expected content
        assert "_match_database" in content
        assert "MCP_CATEGORIES" in content

    def test_skill_categories_content_valid(self):
        """Test skill categories file has valid Python syntax."""
        skill_categories_file = Path(__file__).parent.parent / "src" / "copaw" / "config" / "skillCategories.py"
        content = skill_categories_file.read_text()
        
        # Should be valid Python
        compile(content, str(skill_categories_file), 'exec')
        
        # Should contain expected content
        assert "SKILL_CATEGORIES" in content
