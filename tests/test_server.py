"""
Sanity tests for the Chatwoot MCP Server.

Uses mocked HTTP via httpx to avoid needing a real Chatwoot instance.
"""

from __future__ import annotations

import json
import os
from typing import Any
from unittest.mock import patch

import pytest

# Point at the source under test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def env():
    """Set required env vars before every test."""
    old = {
        k: os.environ.pop(k, None)
        for k in ("CHATWOOT_BASE_URL", "CHATWOOT_USER_TOKEN", "CHATWOOT_DEFAULT_ACCOUNT_ID")
    }
    os.environ["CHATWOOT_BASE_URL"] = "https://chatwoot.test"
    os.environ["CHATWOOT_USER_TOKEN"] = "test-token-123"
    os.environ["CHATWOOT_DEFAULT_ACCOUNT_ID"] = "1"
    yield
    for k, v in old.items():
        if v is not None:
            os.environ[k] = v
        else:
            os.environ.pop(k, None)


@pytest.fixture
def patch_http():
    """Replace the SDK HTTP layer with a simple mock that returns canned data."""
    def mock_get(*args, **kwargs) -> Any:
        # args[0] is self (HTTPClient), args[1] is the path
        path = args[1] if len(args) > 1 else (args[0] if args else "")
        if "profile" in path:
            return {"id": 1, "name": "Test Agent", "email": "test@chatwoot.test", "account_id": 1, "role": "agent"}
        if "conversations" in path and "messages" not in path and "toggle" not in path and "meta" not in path and "labels" not in path and "search" not in path:
            # get single conversation (path has /conversations/N) vs list (no trailing number)
            parts = path.rstrip("/").split("/")
            if parts[-1].isdigit():
                return {"id": int(parts[-1]), "account_id": 1, "inbox_id": 1, "status": "open", "contact_inbox": {"source_id": "test"}}
            return [{"id": 42, "account_id": 1, "inbox_id": 1, "status": "open", "contact_inbox": {"source_id": "test"}}]
        if "messages" in path:
            return [{"id": 1, "content": "Hola", "message_type": "incoming", "conversation_id": 42, "created_at": 1719000000},
                    {"id": 2, "content": "Buenas", "message_type": "outgoing", "conversation_id": 42, "created_at": 1719000100}]
        if "contacts/search" in path:
            return [{"id": 7, "name": "Juan Pérez", "phone_number": "+521234567890"}]
        if "contacts" in path and "conversations" in path:
            return [{"id": 42, "account_id": 1, "inbox_id": 1, "status": "open"}]
        if "contacts" in path:
            return [{"id": 7, "name": "Juan Pérez"}]
        if "inboxes" in path and "members" not in path:
            return [{"id": 1, "channel_id": 1, "name": "WhatsApp Test", "channel_type": "whatsapp"}]
        if "agents" in path:
            return [{"id": 1, "name": "Agent 1", "email": "agent1@test.com", "account_id": 1, "role": "agent"}]
        if "teams" in path:
            return [{"id": 1, "name": "Ventas", "account_id": 1}]
        return []

    def mock_post(*args, **kwargs) -> Any:
        return {"id": 999, "content": "sent", "message_type": "outgoing", "conversation_id": 42, "created_at": 1719000000}

    def mock_patch(*args, **kwargs) -> Any:
        return {"id": 42, "account_id": 1, "inbox_id": 1, "status": "resolved"}

    with patch("chatwoot._http.HTTPClient.get", mock_get), \
         patch("chatwoot._http.HTTPClient.post", mock_post), \
         patch("chatwoot._http.HTTPClient.patch", mock_patch):
        yield


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestProfile:
    def test_get_profile(self, patch_http):
        from server import chatwoot_get_profile
        result = chatwoot_get_profile()
        assert result["name"] == "Test Agent"
        assert result["email"] == "test@chatwoot.test"


class TestConversations:
    def test_list_conversations(self, patch_http):
        from server import chatwoot_list_conversations
        result = chatwoot_list_conversations()
        assert isinstance(result, list)
        assert result[0]["id"] == 42
        assert result[0]["status"] == "open"

    def test_list_conversations_with_filters(self, patch_http):
        from server import chatwoot_list_conversations
        result = chatwoot_list_conversations(inbox_id=1, q="test")
        assert isinstance(result, list)

    def test_get_conversation(self, patch_http):
        from server import chatwoot_get_conversation
        result = chatwoot_get_conversation(conversation_id=42)
        assert result["id"] == 42

    def test_update_conversation(self, patch_http):
        from server import chatwoot_update_conversation
        result = chatwoot_update_conversation(conversation_id=42, status="resolved")
        assert result["status"] == "resolved"


class TestMessages:
    def test_get_messages(self, patch_http):
        from server import chatwoot_get_conversation_messages
        result = chatwoot_get_conversation_messages(conversation_id=42)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["content"] == "Hola"

    def test_send_message(self, patch_http):
        from server import chatwoot_send_message
        result = chatwoot_send_message(conversation_id=42, content="Test")
        assert result["content"] == "sent"


class TestContacts:
    def test_list_contacts(self, patch_http):
        from server import chatwoot_list_contacts
        result = chatwoot_list_contacts()
        assert isinstance(result, list)

    def test_get_contact(self, patch_http):
        from server import chatwoot_get_contact
        result = chatwoot_get_contact(contact_id=7)
        assert isinstance(result, dict)

    def test_search_contacts(self, patch_http):
        from server import chatwoot_search_contacts
        result = chatwoot_search_contacts(q="Juan")
        assert isinstance(result, list)
        assert result[0]["name"] == "Juan Pérez"


class TestInboxes:
    def test_list_inboxes(self, patch_http):
        from server import chatwoot_list_inboxes
        result = chatwoot_list_inboxes()
        assert isinstance(result, list)
        assert result[0]["name"] == "WhatsApp Test"
        assert result[0]["channel_type"] == "whatsapp"


class TestAgents:
    def test_list_agents(self, patch_http):
        from server import chatwoot_list_agents
        result = chatwoot_list_agents()
        assert isinstance(result, list)


class TestTeams:
    def test_list_teams(self, patch_http):
        from server import chatwoot_list_teams
        result = chatwoot_list_teams()
        assert isinstance(result, list)


class TestErrors:
    def test_missing_env_returns_error(self):
        os.environ.pop("CHATWOOT_BASE_URL", None)
        from server import chatwoot_list_inboxes
        result = chatwoot_list_inboxes()
        assert "error" in result
        assert "CHATWOOT_BASE_URL" in result["error"]
