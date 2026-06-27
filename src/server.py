"""
Chatwoot MCP Server — core module.

Exposes 20+ MCP tools over stdio transport, powered by the official
chatwoot-sdk (MIT, maintained by Chatwoot engineering).

Tools are organized by resource: profile, conversations, messages,
contacts, inboxes, teams, agents.
"""

from __future__ import annotations

import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from chatwoot import ChatwootClient
from chatwoot.exceptions import ChatwootError

# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP("chatwoot")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ACCOUNT_ID: str | None = None


def _get_client() -> tuple[ChatwootClient, int]:
    """Build a ChatwootClient from env vars.

    Required:
        CHATWOOT_BASE_URL         — e.g. https://app.chatwoot.com
        CHATWOOT_USER_TOKEN       — API access token from Profile > Access Token
        CHATWOOT_DEFAULT_ACCOUNT_ID — numeric account id from the URL

    Returns (client, account_id).
    """
    base_url = os.environ.get("CHATWOOT_BASE_URL", "").rstrip("/")
    token = os.environ.get("CHATWOOT_USER_TOKEN", "")
    raw_aid = os.environ.get("CHATWOOT_DEFAULT_ACCOUNT_ID", "")

    errors = []
    if not base_url:
        errors.append("CHATWOOT_BASE_URL is required")
    if not token:
        errors.append("CHATWOOT_USER_TOKEN is required")
    if not raw_aid:
        errors.append("CHATWOOT_DEFAULT_ACCOUNT_ID is required")

    if errors:
        raise ChatwootError(f"Missing env vars: {', '.join(errors)}")

    try:
        account_id = int(raw_aid)
    except ValueError:
        raise ChatwootError(f"CHATWOOT_DEFAULT_ACCOUNT_ID must be an integer, got {raw_aid!r}")

    return ChatwootClient(base_url=base_url, api_token=token), account_id


def _safe_call(fn):
    """Wrap an SDK call so MCP gets a clean error message."""
    try:
        return fn()
    except ChatwootError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ═══════════════════════════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════════════════════════


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@mcp.tool()
def chatwoot_get_profile() -> dict:
    """Get the authenticated user's profile."""
    def _call():
        client, _ = _get_client()
        p = client.profile.get()
        return p.model_dump() if hasattr(p, "model_dump") else {"name": str(p)}
    return _safe_call(_call)


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

@mcp.tool()
def chatwoot_list_conversations(
    assignee_type: str = "all",
    page: int = 1,
    inbox_id: int | None = None,
    team_id: int | None = None,
    labels: str | None = None,
    q: str | None = None,
) -> list | dict:
    """List open conversations with optional filters.

    Solo muestra conversaciones abiertas por defecto.
    Para histórico o retrospectiva pídelo explícitamente.

    Args:
        assignee_type: 'all', 'me', or 'unassigned'
        page: page number for pagination
        inbox_id: filter by inbox ID
        team_id: filter by team ID
        labels: comma-separated label names
        q: search query (full-text search across conversation content)
    """
    def _call():
        client, aid = _get_client()
        label_list = labels.split(",") if labels else None
        convs = client.conversations.list(
            account_id=aid,
            status="open",
            assignee_type=assignee_type,
            page=page,
            inbox_id=inbox_id,
            team_id=team_id,
            labels=label_list,
            q=q,
        )
        return [c.model_dump() if hasattr(c, "model_dump") else str(c) for c in convs]
    return _safe_call(_call)


@mcp.tool()
def chatwoot_get_conversation(conversation_id: int) -> dict:
    """Get a single conversation's full details.

    Args:
        conversation_id: the numeric conversation ID
    """
    def _call():
        client, aid = _get_client()
        c = client.conversations.get(account_id=aid, conversation_id=conversation_id)
        return c.model_dump() if hasattr(c, "model_dump") else {"id": conversation_id}
    return _safe_call(_call)


@mcp.tool()
def chatwoot_update_conversation(
    conversation_id: int,
    status: str | None = None,
    assignee_id: int | None = None,
    team_id: int | None = None,
) -> dict:
    """Update a conversation's status, assignee, or team.

    Args:
        conversation_id: the conversation ID
        status: new status ('open', 'resolved', 'pending', 'snoozed')
        assignee_id: agent ID to assign
        team_id: team ID to assign
    """
    def _call():
        client, aid = _get_client()
        c = client.conversations.update(
            account_id=aid,
            conversation_id=conversation_id,
            status=status,
            assignee_id=assignee_id,
            team_id=team_id,
        )
        return c.model_dump() if hasattr(c, "model_dump") else {"id": conversation_id}
    return _safe_call(_call)


@mcp.tool()
def chatwoot_get_conversation_counts(status: str = "open") -> dict:
    """Get conversation counts by status.

    Args:
        status: status to count ('open', 'resolved', 'pending', 'snoozed')
    """
    def _call():
        client, aid = _get_client()
        return client.conversations.get_counts(account_id=aid, status=status)
    return _safe_call(_call)


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

@mcp.tool()
def chatwoot_get_conversation_messages(conversation_id: int) -> list | dict:
    """List all messages in a conversation.

    Args:
        conversation_id: the conversation ID
    """
    def _call():
        client, aid = _get_client()
        msgs = client.messages.list(account_id=aid, conversation_id=conversation_id)
        return [m.model_dump() if hasattr(m, "model_dump") else str(m) for m in msgs]
    return _safe_call(_call)


@mcp.tool()
def chatwoot_send_message(
    conversation_id: int,
    content: str,
    message_type: str = "outgoing",
    private: bool = False,
) -> dict:
    """Send a message in a conversation.

    Args:
        conversation_id: the conversation ID
        content: message text
        message_type: 'outgoing' (visible to customer) or 'incoming'
        private: if True, message is an internal note (invisible to customer)
    """
    def _call():
        client, aid = _get_client()
        m = client.messages.create(
            account_id=aid,
            conversation_id=conversation_id,
            content=content,
            message_type=message_type,
            private=private,
        )
        return m.model_dump() if hasattr(m, "model_dump") else {"content": content}
    return _safe_call(_call)


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

@mcp.tool()
def chatwoot_list_contacts(page: int = 1) -> list | dict:
    """List all contacts.

    Args:
        page: page number for pagination
    """
    def _call():
        client, aid = _get_client()
        contacts = client.contacts.list(account_id=aid, page=page)
        return [c.model_dump() if hasattr(c, "model_dump") else str(c) for c in contacts]
    return _safe_call(_call)


@mcp.tool()
def chatwoot_get_contact(contact_id: int) -> dict:
    """Get a single contact's details.

    Args:
        contact_id: the numeric contact ID
    """
    def _call():
        client, aid = _get_client()
        c = client.contacts.get(account_id=aid, contact_id=contact_id)
        return c.model_dump() if hasattr(c, "model_dump") else {"id": contact_id}
    return _safe_call(_call)


@mcp.tool()
def chatwoot_search_contacts(q: str) -> list | dict:
    """Search contacts by name, email, or phone number.

    Args:
        q: search query string
    """
    def _call():
        client, aid = _get_client()
        contacts = client.contacts.search(account_id=aid, query=q)
        return [c.model_dump() if hasattr(c, "model_dump") else str(c) for c in contacts]
    return _safe_call(_call)


@mcp.tool()
def chatwoot_get_contact_conversations(contact_id: int) -> list | dict:
    """List all conversations for a specific contact.

    Args:
        contact_id: the numeric contact ID
    """
    def _call():
        client, aid = _get_client()
        convs = client.contacts.conversations(account_id=aid, contact_id=contact_id)
        return [c.model_dump() if hasattr(c, "model_dump") else str(c) for c in convs]
    return _safe_call(_call)


# ---------------------------------------------------------------------------
# Inboxes
# ---------------------------------------------------------------------------

@mcp.tool()
def chatwoot_list_inboxes() -> list | dict:
    """List all inboxes (WhatsApp, email, web widget, API, etc.)"""
    def _call():
        client, aid = _get_client()
        inboxes = client.inboxes.list(account_id=aid)
        return [i.model_dump() if hasattr(i, "model_dump") else str(i) for i in inboxes]
    return _safe_call(_call)


@mcp.tool()
def chatwoot_get_inbox(inbox_id: int) -> dict:
    """Get a single inbox's details.

    Args:
        inbox_id: the numeric inbox ID
    """
    def _call():
        client, aid = _get_client()
        i = client.inboxes.get(account_id=aid, inbox_id=inbox_id)
        return i.model_dump() if hasattr(i, "model_dump") else {"id": inbox_id}
    return _safe_call(_call)


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

@mcp.tool()
def chatwoot_list_agents() -> list | dict:
    """List all agents in the account."""
    def _call():
        client, aid = _get_client()
        agents = client.agents.list(account_id=aid)
        return [a.model_dump() if hasattr(a, "model_dump") else str(a) for a in agents]
    return _safe_call(_call)


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

@mcp.tool()
def chatwoot_list_teams() -> list | dict:
    """List all teams."""
    def _call():
        client, aid = _get_client()
        teams = client.teams.list(account_id=aid)
        return [t.model_dump() if hasattr(t, "model_dump") else str(t) for t in teams]
    return _safe_call(_call)
