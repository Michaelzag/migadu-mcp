# Migadu MCP Server

[![PyPI version](https://img.shields.io/pypi/v/migadu-mcp?style=for-the-badge)](https://pypi.org/project/migadu-mcp/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Michaelzag/migadu-mcp/workflows/CI/badge.svg?style=for-the-badge)](https://github.com/Michaelzag/migadu-mcp/actions/workflows/ci.yml)

Control your Migadu email hosting through AI assistants using the Model Context Protocol (MCP).

## What is Migadu?

[Migadu](https://migadu.com/) is a Swiss email hosting service that offers unlimited email addresses with pricing based on actual usage rather than mailbox count. They focus on standard email protocols (SMTP/IMAP/POP3) without vendor lock-in, making them popular with developers and privacy-conscious users.

## What This Does

This MCP server lets AI assistants manage your Migadu email accounts. Instead of clicking through web interfaces, you can ask your AI to:

- Create and delete mailboxes
- Set up email aliases and forwarding rules
- Configure autoresponders
- Manage multiple email identities
- Handle bulk operations efficiently

## Setup

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "migadu": {
      "command": "uvx",
      "args": ["migadu-mcp"],
      "env": {
        "MIGADU_EMAIL": "admin@yourdomain.com",
        "MIGADU_API_KEY": "your-api-key",
        "MIGADU_DOMAIN": "yourdomain.com"
      }
    }
  }
}
```

Get your API key from [Migadu Admin > My Account > API Keys](https://admin.migadu.com/account/api/keys).

## Example Usage

Once configured, you can ask your AI assistant things like:

- "Create a new mailbox for john@mydomain.com with the name John Smith"
- "List all mailboxes on my domain"
- "Set up an email alias support@mydomain.com that forwards to team@mydomain.com"
- "Delete the mailboxes for employees who left: alice@mydomain.com, bob@mydomain.com"
- "Create an autoresponder for vacation@mydomain.com"

## Available Tools

### Mailbox Management
- `list_mailboxes` / `list_my_mailboxes` - View all mailboxes
- `get_mailbox` / `get_my_mailbox` - Get mailbox details
- `create_mailbox` / `create_my_mailbox` - Create new mailboxes
- `update_mailbox` - Change mailbox settings
- `delete_mailbox` - Remove mailboxes
- `bulk_delete_mailboxes` - Delete multiple mailboxes at once
- `reset_mailbox_password` - Change passwords
- `set_autoresponder` - Configure out-of-office messages

### Email Routing
- `list_aliases` / `list_my_aliases` - View email aliases
- `create_alias` - Set up email forwarding without creating a mailbox
- `update_alias` - Change alias destinations
- `delete_alias` - Remove aliases

### Identity Management
- `list_identities` - View send-as addresses
- `create_identity` - Add additional sending addresses
- `update_identity` - Modify identity permissions
- `delete_identity` - Remove identities

### Advanced Routing
- `list_rewrites` - View pattern-based routing rules
- `create_rewrite` - Set up wildcard email routing
- `update_rewrite` - Modify routing patterns
- `delete_rewrite` - Remove routing rules

### External Forwarding
- `list_forwardings` - View external forwarding rules
- `create_forwarding` - Forward emails to external addresses
- `update_forwarding` - Change forwarding settings
- `delete_forwarding` - Remove forwarding rules

## MCP Resources

Access structured data through these resource URIs:

- `mailboxes://domain.com` - All mailboxes for a domain
- `mailbox://domain.com/username` - Specific mailbox details
- `aliases://domain.com` - All aliases for a domain
- `identities://domain.com/mailbox` - Identities for a mailbox
- `forwardings://domain.com/mailbox` - Forwarding rules for a mailbox
- `rewrites://domain.com` - Rewrite rules for a domain

## Technical Notes

- The server handles Migadu's API quirks automatically (like 500 status codes on successful deletions)
- All operations include proper error handling and progress reporting
- Built with FastMCP for reliable MCP integration
- Supports bulk operations with intelligent batching

## Development

```bash
# Clone the repository
git clone https://github.com/Michaelzag/migadu-mcp.git
cd migadu-mcp

# Install dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run quality checks
uv run ruff format --check .
uv run ruff check .
uv run mypy migadu_mcp/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.