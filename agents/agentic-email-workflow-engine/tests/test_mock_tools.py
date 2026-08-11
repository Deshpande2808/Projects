"""
Tests for mock tool implementations.

Verifies that mocked tools:
1. Implement the Tool protocol correctly
2. Return expected fixture data
3. Handle edge cases (missing data, invalid operations)
4. Can be registered and retrieved via ToolRegistry
"""

import pytest
from src.tools import (
    create_tool_registry,
    MockDatabaseTool,
    MockDocumentStoreTool,
    MockCRMTool,
    MockEmailSenderTool,
)


# ============================================================================
# MOCK DATABASE TOOL TESTS
# ============================================================================

class TestMockDatabaseTool:
    """Tests for MockDatabaseTool."""

    @pytest.fixture
    def tool(self):
        return MockDatabaseTool()

    @pytest.mark.asyncio
    async def test_lookup_customer(self, tool):
        """Test looking up a customer by ID."""
        result = await tool.call({
            "operation": "lookup",
            "resource": "customer",
            "id": 123,
        })

        assert result["success"] is True
        assert result["data"]["id"] == 123
        assert result["data"]["name"] == "Alice Johnson"

    @pytest.mark.asyncio
    async def test_lookup_missing_customer(self, tool):
        """Test looking up a nonexistent customer."""
        result = await tool.call({
            "operation": "lookup",
            "resource": "customer",
            "id": 999,
        })

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_list_customers(self, tool):
        """Test listing all customers."""
        result = await tool.call({
            "operation": "list",
            "resource": "customer",
        })

        assert result["success"] is True
        assert len(result["data"]) == 3

    @pytest.mark.asyncio
    async def test_query_customers_by_filter(self, tool):
        """Test querying customers with filters."""
        result = await tool.call({
            "operation": "query",
            "resource": "customer",
            "filters": {"status": "active"},
        })

        assert result["success"] is True
        assert len(result["data"]) == 2  # Alice and Bob

    @pytest.mark.asyncio
    async def test_lookup_invoice(self, tool):
        """Test looking up an invoice."""
        result = await tool.call({
            "operation": "lookup",
            "resource": "invoice",
            "id": "INV-001",
        })

        assert result["success"] is True
        assert result["data"]["amount"] == 99.99

    def test_tool_metadata(self, tool):
        """Test tool has correct metadata."""
        assert tool.name == "database"
        assert "database_query" in tool.capability_tags
        assert "customer_lookup" in tool.capability_tags


# ============================================================================
# MOCK DOCUMENT STORE TOOL TESTS
# ============================================================================

class TestMockDocumentStoreTool:
    """Tests for MockDocumentStoreTool."""

    @pytest.fixture
    def tool(self):
        return MockDocumentStoreTool()

    @pytest.mark.asyncio
    async def test_search_documents(self, tool):
        """Test searching for documents."""
        result = await tool.call({
            "operation": "search",
            "query": "password",
        })

        assert result["success"] is True
        assert result["count"] > 0
        assert any("Password" in doc["title"] for doc in result["data"])

    @pytest.mark.asyncio
    async def test_search_with_category_filter(self, tool):
        """Test searching with category filter."""
        result = await tool.call({
            "operation": "search",
            "query": "account",
            "category": "account",
        })

        assert result["success"] is True
        assert all(doc["category"] == "account" for doc in result["data"])

    @pytest.mark.asyncio
    async def test_retrieve_document(self, tool):
        """Test retrieving a specific document."""
        result = await tool.call({
            "operation": "retrieve",
            "doc_id": "KB-001",
        })

        assert result["success"] is True
        assert result["data"]["title"] == "Password Reset Guide"

    @pytest.mark.asyncio
    async def test_retrieve_missing_document(self, tool):
        """Test retrieving a nonexistent document."""
        result = await tool.call({
            "operation": "retrieve",
            "doc_id": "FAKE-999",
        })

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_list_documents_by_category(self, tool):
        """Test listing documents by category."""
        result = await tool.call({
            "operation": "list",
            "category": "billing",
        })

        assert result["success"] is True
        assert all(doc["category"] == "billing" for doc in result["data"])

    def test_tool_metadata(self, tool):
        """Test tool has correct metadata."""
        assert tool.name == "document_store"
        assert "document_search" in tool.capability_tags


# ============================================================================
# MOCK CRM TOOL TESTS
# ============================================================================

class TestMockCRMTool:
    """Tests for MockCRMTool."""

    @pytest.fixture
    def tool(self):
        return MockCRMTool()

    @pytest.mark.asyncio
    async def test_lookup_account(self, tool):
        """Test looking up a CRM account."""
        result = await tool.call({
            "operation": "lookup_account",
            "id": 123,
        })

        assert result["success"] is True
        assert result["data"]["name"] == "Alice Johnson"
        assert result["data"]["account_value"] == 50000

    @pytest.mark.asyncio
    async def test_lookup_missing_account(self, tool):
        """Test looking up a nonexistent account."""
        result = await tool.call({
            "operation": "lookup_account",
            "id": 999,
        })

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_update_account(self, tool):
        """Test updating a CRM account."""
        result = await tool.call({
            "operation": "update",
            "id": 123,
            "update_data": {"notes": "VIP customer - high priority"},
        })

        assert result["success"] is True
        assert "updated successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_lookup_opportunity(self, tool):
        """Test looking up a sales opportunity."""
        result = await tool.call({
            "operation": "lookup_opportunity",
            "id": "OPP-001",
        })

        assert result["success"] is True
        assert result["data"]["title"] == "Upgrade to Enterprise"

    @pytest.mark.asyncio
    async def test_list_opportunities_by_account(self, tool):
        """Test listing opportunities for an account."""
        result = await tool.call({
            "operation": "list_opportunities",
            "account_id": 123,
        })

        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["account_id"] == 123

    def test_tool_metadata(self, tool):
        """Test tool has correct metadata."""
        assert tool.name == "crm"
        assert "crm_lookup" in tool.capability_tags


# ============================================================================
# MOCK EMAIL SENDER TOOL TESTS
# ============================================================================

class TestMockEmailSenderTool:
    """Tests for MockEmailSenderTool."""

    @pytest.fixture
    def tool(self):
        return MockEmailSenderTool()

    @pytest.mark.asyncio
    async def test_send_email(self, tool):
        """Test sending an email."""
        result = await tool.call({
            "to": "user@example.com",
            "subject": "Test Email",
            "body": "This is a test email.",
        })

        assert result["success"] is True
        assert "MOCK-EMAIL" in result["email_id"]
        assert "sent_at" in result

    @pytest.mark.asyncio
    async def test_send_email_with_html(self, tool):
        """Test sending an email with HTML body."""
        result = await tool.call({
            "to": "user@example.com",
            "subject": "HTML Email",
            "body": "Text version",
            "html": "<h1>HTML Version</h1>",
            "cc": ["cc@example.com"],
            "bcc": ["bcc@example.com"],
        })

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_send_email_missing_to(self, tool):
        """Test sending an email without 'to' field."""
        result = await tool.call({
            "subject": "Test Email",
            "body": "Missing recipient",
        })

        assert result["success"] is False
        assert "Missing required fields" in result["error"]

    @pytest.mark.asyncio
    async def test_get_sent_emails(self, tool):
        """Test retrieving sent emails log."""
        # Send an email
        await tool.call({
            "to": "user1@example.com",
            "subject": "Email 1",
            "body": "Test",
        })

        await tool.call({
            "to": "user2@example.com",
            "subject": "Email 2",
            "body": "Test",
        })

        # Get all sent emails
        sent = await tool.get_sent_emails()
        assert len(sent) == 2
        assert sent[0]["to"] == "user1@example.com"
        assert sent[1]["to"] == "user2@example.com"

    def test_tool_metadata(self, tool):
        """Test tool has correct metadata."""
        assert tool.name == "email_sender"
        assert "email_sending" in tool.capability_tags


# ============================================================================
# TOOL REGISTRY INTEGRATION TESTS
# ============================================================================

class TestToolRegistryWithMockTools:
    """Integration tests with ToolRegistry and mock tools."""

    def test_create_tool_registry(self):
        """Test creating a registry with all mocked tools."""
        registry = create_tool_registry()

        # Verify all tools are registered
        assert registry.get("database").name == "database"
        assert registry.get("document_store").name == "document_store"
        assert registry.get("crm").name == "crm"
        assert registry.get("email_sender").name == "email_sender"

    def test_list_tools_by_capability(self):
        """Test listing tools by capability tag."""
        registry = create_tool_registry()

        # Find all tools that can do database queries
        db_tools = registry.list_by_tag("database_query")
        assert len(db_tools) >= 1
        assert any(tool.name == "database" for tool in db_tools)

    def test_list_all_tools(self):
        """Test listing all tools."""
        registry = create_tool_registry()

        all_tools = registry.list_all()
        assert len(all_tools) == 4  # database, document_store, crm, email_sender

        tool_names = {tool.name for tool in all_tools}
        expected = {"database", "document_store", "crm", "email_sender"}
        assert tool_names == expected
