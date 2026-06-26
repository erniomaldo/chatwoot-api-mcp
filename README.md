# Chatwoot MCP Server

MCP (Model Context Protocol) server that connects any MCP client (Claude, Hermes Agent, etc.) to a **Chatwoot** instance via the official [chatwoot-sdk](https://pypi.org/project/chatwoot-sdk/) (MIT, maintained by Chatwoot engineering).

**20+ tools** covering conversations, messages, contacts, inboxes, agents, teams, and profile — all over **stdio transport** (no HTTP, no SSE).

---

## Requirements

- Python >= 3.11
- A running Chatwoot instance (self-hosted or cloud)
- [Chatwoot API Access Token](https://www.chatwoot.com/hc/user-guide/articles/1677238266-lesson-4-complete-your-customer-engagement-suite)

## Quick Start

```bash
git clone <your-repo-url> chatwoot-mcp
cd chatwoot-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CHATWOOT_BASE_URL` | ✅ | Your Chatwoot instance URL | `https://chatwoot.tudominio.com` |
| `CHATWOOT_USER_TOKEN` | ✅ | API token from Profile → Access Token | `tX7k9mP2...` |
| `CHATWOOT_DEFAULT_ACCOUNT_ID` | ✅ | Numeric account ID from URL | `2` |

Get your token at: Chatwoot UI → click avatar → **Profile Settings** → **Access Token**.

## Run

### Direct (stdio)

```bash
python run_server.py
```

The server starts in stdio mode — it reads JSON-RPC messages on stdin and writes responses on stdout. Use it with any MCP client.

### With Hermes Agent

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  chatwoot:
    command: "/home/ernesto-personal/chatwoot-mcp/.venv/bin/python"
    args: ["/home/ernesto-personal/chatwoot-mcp/run_server.py"]
    env:
      CHATWOOT_BASE_URL: "https://chatwoot.tudominio.com"
      CHATWOOT_USER_TOKEN: "tu-token-aqui"
      CHATWOOT_DEFAULT_ACCOUNT_ID: "2"
```

Restart Hermes Agent. Tools appear as `mcp_chatwoot_*`.

## Tools

### Profile

| Tool | Description |
|------|-------------|
| `chatwoot_get_profile` | Get authenticated user's profile |

### Conversations

| Tool | Description |
|------|-------------|
| `chatwoot_list_conversations` | List conversations with filters (status, inbox, team, labels, search query `q`) |
| `chatwoot_get_conversation` | Get a single conversation's full details |
| `chatwoot_update_conversation` | Update status, assignee, or team |
| `chatwoot_get_conversation_counts` | Get conversation counts by status |

### Messages

| Tool | Description |
|------|-------------|
| `chatwoot_get_conversation_messages` | List all messages in a conversation |
| `chatwoot_send_message` | Send a message (outgoing, incoming, or private note) |

### Contacts

| Tool | Description |
|------|-------------|
| `chatwoot_list_contacts` | List all contacts |
| `chatwoot_get_contact` | Get a single contact's details |
| `chatwoot_search_contacts` | Search contacts by name, email, or phone |
| `chatwoot_get_contact_conversations` | List all conversations for a contact |

### Inboxes

| Tool | Description |
|------|-------------|
| `chatwoot_list_inboxes` | List all inboxes (WhatsApp, email, web widget, API, etc.) |
| `chatwoot_get_inbox` | Get a single inbox's details |

### Agents & Teams

| Tool | Description |
|------|-------------|
| `chatwoot_list_agents` | List all agents in the account |
| `chatwoot_list_teams` | List all teams |

## Examples

**"List my open WhatsApp conversations"**
→ tool: `chatwoot_list_conversations` with `status=open`, `inbox_id=<tu-inbox-id>`

**"Read all messages from conversation 42"**
→ tool: `chatwoot_get_conversation_messages` with `conversation_id=42`

**"Find Juan's contact and his conversations"**
→ tool: `chatwoot_search_contacts` with `q=Juan`
→ then: `chatwoot_get_contact_conversations` with `contact_id=<id>`

**"Close conversation 42"**
→ tool: `chatwoot_update_conversation` with `conversation_id=42`, `status=resolved`

## Architecture

```
WhatsApp → Evolution API → Chatwoot → PostgreSQL
                                        ↓
                                 chatwoot-sdk (API)
                                        ↓
                              chatwoot-mcp-server (stdio)
                                        ↓
                                 Hermes Agent (MCP client)
```

The MCP server uses **chatwoot-sdk** (official Python SDK, MIT) to talk to the Chatwoot REST API. All 20+ tools are thin wrappers over the SDK's typed methods — no raw HTTP calls, no manual JSON parsing.

## Testing

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

Tests use mocked HTTP via `unittest.mock.patch` — no real Chatwoot instance needed.

## Project Structure

```
chatwoot-mcp/
├── run_server.py        # Entry point (stdio transport)
├── src/
│   └── server.py        # Core module: 20+ MCP tools
├── tests/
│   ├── conftest.py      # Path setup
│   └── test_server.py   # 14 mocked tests
├── requirements.txt
├── .gitignore
└── README.md
```

## License

MIT — Built on [chatwoot-sdk](https://pypi.org/project/chatwoot-sdk/) (MIT, by Chatwoot Inc.)

---

*Powered by [FastMCP](https://github.com/jlowin/fastmcp) · chatwoot-sdk v0.2.0*
