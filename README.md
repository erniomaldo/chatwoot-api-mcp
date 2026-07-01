<h1 align="center">Chatwoot API MCP Server</h1>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-≥3.11-blue?logo=python" alt="Python ≥3.11"></a>
  <a href="https://pypi.org/project/chatwoot-sdk/"><img src="https://img.shields.io/badge/chatwoot--sdk-0.2.0-blue?logo=python" alt="chatwoot-sdk 0.2.0"></a>
  <a href="https://www.chatwoot.com/"><img src="https://img.shields.io/badge/Chatwoot-API-FF6C37?logo=chatwoot" alt="Chatwoot API"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"></a>
</p>

<p align="center">
  A <a href="https://modelcontextprotocol.io/">Model Context Protocol (MCP)</a> server that exposes the <strong>Chatwoot Application API</strong> through <strong>15 tools</strong> over <strong>stdio transport</strong>. Built on the official <code>chatwoot-sdk</code> (MIT, maintained by Chatwoot engineering).
</p>

<p align="center">
  Compatible with any MCP client — Claude Code, Continue.dev, Cursor, custom AI agents, and more.
</p>

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Tools Reference](#tools-reference)
  - [Profile](#profile)
  - [Conversations](#conversations)
  - [Messages](#messages)
  - [Contacts](#contacts)
  - [Inboxes & Agents & Teams](#inboxes--agents--teams)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- **15 MCP tools** covering the most common Chatwoot API operations
- **Stdio transport** — zero HTTP overhead, native MCP protocol
- **Official SDK** — no raw API calls, no manual JSON parsing, no reinvention
- **Clean error handling** — every tool returns structured errors when the API fails
- **Zero dependencies beyond** `chatwoot-sdk`, `mcp`, `httpx`, and `pydantic`

## Requirements

- Python ≥ 3.11
- A running [Chatwoot](https://www.chatwoot.com/) instance (self-hosted or Chatwoot Cloud)
- [Chatwoot API Access Token](https://www.chatwoot.com/hc/user-guide/articles/1677238266-lesson-4-complete-your-customer-engagement-suite) — Profile → Access Token

## Quick Start

```bash
git clone https://github.com/erniomaldo/chatwoot-api-mcp.git
cd chatwoot-api-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set your Chatwoot credentials
export CHATWOOT_BASE_URL="https://chatwoot.tudominio.com"
export CHATWOOT_USER_TOKEN="tX7k9mP2..."
export CHATWOOT_DEFAULT_ACCOUNT_ID="2"

# Start the MCP server
python run_server.py
```

The server reads JSON-RPC requests from **stdin** and writes responses to **stdout** — the standard MCP stdio pattern.

## Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CHATWOOT_BASE_URL` | ✅ | Your Chatwoot instance URL | `https://chatwoot.tudominio.com` |
| `CHATWOOT_USER_TOKEN` | ✅ | API access token from Profile → Access Token | `tX7k9mP2...` |
| `CHATWOOT_DEFAULT_ACCOUNT_ID` | ✅ | Numeric account ID (from browser URL) | `2` |

Get your token at: **Chatwoot UI → avatar → Profile Settings → Access Token**.

### With Any MCP Client

Add this server to your MCP client configuration. For example, with a generic `claude_desktop_config.json` or equivalent:

```json
{
  "mcpServers": {
    "chatwoot": {
      "command": "/path/to/chatwoot-api-mcp/.venv/bin/python",
      "args": ["/path/to/chatwoot-api-mcp/run_server.py"],
      "env": {
        "CHATWOOT_BASE_URL": "https://chatwoot.tudominio.com",
        "CHATWOOT_USER_TOKEN": "tu-token-aqui",
        "CHATWOOT_DEFAULT_ACCOUNT_ID": "2"
      }
    }
  }
}
```

---

## Tools Reference

### Profile

| Tool | Description |
|------|-------------|
| `chatwoot_get_profile` | Get the authenticated user's profile |

### Conversations

| Tool | Description |
|------|-------------|
| `chatwoot_list_conversations` | List open conversations (filters: assignee, inbox, team, labels, search query) |
| `chatwoot_get_conversation` | Get full details of a single conversation |
| `chatwoot_update_conversation` | Update status, assignee, or team on a conversation |
| `chatwoot_get_conversation_counts` | Count conversations by status (open, resolved, pending, snoozed) |

### Messages

| Tool | Description |
|------|-------------|
| `chatwoot_get_conversation_messages` | List all messages in a conversation |
| `chatwoot_send_message` | Send a message (outgoing, incoming, or private internal note) |

### Contacts

| Tool | Description |
|------|-------------|
| `chatwoot_list_contacts` | List all contacts (paginated) |
| `chatwoot_get_contact` | Get a single contact's details |
| `chatwoot_search_contacts` | Search contacts by name, email, or phone |
| `chatwoot_get_contact_conversations` | List all conversations for a specific contact |

### Inboxes, Agents & Teams

| Tool | Description |
|------|-------------|
| `chatwoot_list_inboxes` | List all inboxes (WhatsApp, email, web widget, API, etc.) |
| `chatwoot_get_inbox` | Get a single inbox's details |
| `chatwoot_list_agents` | List all agents in the account |
| `chatwoot_list_teams` | List all teams |

---

## Usage Examples

**"List my open WhatsApp conversations"**
→ `chatwoot_list_conversations` with `inbox_id=<your-whatsapp-inbox-id>`

**"Read all messages from conversation 42"**
→ `chatwoot_get_conversation_messages` with `conversation_id=42`

**"Find Juan's contact and his conversations"**
→ `chatwoot_search_contacts` with `q=Juan`
→ then `chatwoot_get_contact_conversations` with `contact_id=<result-id>`

**"Close conversation 42"**
→ `chatwoot_update_conversation` with `conversation_id=42`, `status=resolved`

**"Send a private note to conversation 7"**
→ `chatwoot_send_message` with `conversation_id=7`, `content="Revisando...", `private=true`

---

## Architecture

```
WhatsApp / Telegram / Email → Evolution API → Chatwoot → PostgreSQL
                                                        ↓
                                                 chatwoot-sdk (Python)
                                                        ↓
                                              chatwoot-api-mcp (stdio)
                                                        ↓
                                                 MCP Client (Claude, etc.)
```

The server sits as a lightweight translation layer: **Chatwoot REST API → typed Python SDK → MCP tools**. Every tool is a thin wrapper over the official `chatwoot-sdk` methods — no raw HTTP, no manual serialization.

---

## Testing

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

Tests use mocked HTTP via `unittest.mock.patch` — no live Chatwoot instance required.

---

## Project Structure

```
chatwoot-api-mcp/
├── run_server.py          # MCP server entry point (stdio transport)
├── src/
│   └── server.py          # Core module: 15 MCP tools
├── tests/
│   ├── conftest.py        # Test path setup
│   └── test_server.py     # 14 mocked tests covering all tools and error cases
├── docs/                  # Additional documentation (if any)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## License

**MIT License** — built on top of the official [chatwoot-sdk](https://pypi.org/project/chatwoot-sdk/) (MIT, by Chatwoot Inc.).

This project is **not affiliated with, funded by, or endorsed by** Chatwoot Inc. It uses the publicly available Chatwoot Application API and the open-source `chatwoot-sdk`.

---

<p align="center">
  <a href="https://www.chatwoot.com/"><img src="https://img.shields.io/badge/Built%20for-Chatwoot-FF6C37?logo=chatwoot" alt="Built for Chatwoot"></a>
</p>
