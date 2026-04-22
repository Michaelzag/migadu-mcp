# Migadu MCP Server

[![PyPI version](https://img.shields.io/pypi/v/migadu-mcp?style=for-the-badge)](https://pypi.org/project/migadu-mcp/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Control your Migadu email hosting from AI assistants via the Model Context Protocol.

## What is Migadu?

[Migadu](https://migadu.com/) is a Swiss email host that prices on actual usage instead of mailbox count, with standard SMTP/IMAP/POP3 and no lock-in.

## What this does

Covers the full Migadu API surface as MCP tools:

- Domains — create, update, activate, DNS records, diagnostics, usage
- Mailboxes — CRUD, autoresponders, password resets
- Aliases — forwarding rules without a mailbox behind them
- Identities — send-as addresses on a mailbox
- Forwardings — external delivery copies with confirmation flow
- Rewrites — pattern-based routing rules

## Setup

Get an API key at [Migadu Admin → My Account → API Keys](https://admin.migadu.com/account/api/keys).

Add to your MCP client config (e.g. Claude Desktop, `~/.claude.json`, etc.):

```json
{
  "mcpServers": {
    "migadu": {
      "command": "uvx",
      "args": ["migadu-mcp"],
      "env": {
        "MIGADU_EMAIL": "you@example.com",
        "MIGADU_API_KEY": "your-api-key",
        "MIGADU_DOMAIN": "example.com"
      }
    }
  }
}
```

Or via the Claude Code CLI:

```bash
claude mcp add migadu \
  --env MIGADU_EMAIL=you@example.com \
  --env MIGADU_API_KEY=your-api-key \
  --env MIGADU_DOMAIN=example.com \
  -- uvx migadu-mcp
```

`MIGADU_DOMAIN` is optional. It's the default domain used by tools like `list_mailboxes` when you don't pass one explicitly. Skip it if you manage multiple domains and prefer to pass `domain` on every call.

## Example usage

Once configured, ask your AI assistant things like:

- "Onboard a new domain `acme.example` — walk me through DNS setup and activation"
- "Create mailboxes for alice@acme.example and bob@acme.example"
- "Set up `support@acme.example` as an alias to both Alice and Bob"
- "Configure an autoresponder on `vacation@acme.example` until January 15th"
- "Delete the mailboxes for everyone who left: list of addresses..."

Three built-in prompts are registered to scaffold common workflows: `mailbox_creation_wizard`, `bulk_operation_planner`, `domain_onboarding`.

## Tools

### Domain

`list_domains`, `get_domain`, `create_domain`, `update_domain`, `get_domain_records`, `get_domain_diagnostics`, `activate_domain`, `get_domain_usage`

### Mailbox

`list_mailboxes`, `get_mailbox`, `create_mailbox`, `update_mailbox`, `delete_mailbox`, `reset_mailbox_password`, `set_autoresponder`

### Alias

`list_aliases`, `get_alias`, `create_alias`, `update_alias`, `delete_alias`

### Identity

`list_identities`, `get_identity`, `create_identity`, `update_identity`, `delete_identity`

### Forwarding

`list_forwardings`, `get_forwarding`, `create_forwarding`, `update_forwarding`, `delete_forwarding`

### Rewrite

`list_rewrites`, `get_rewrite`, `create_rewrite`, `update_rewrite`, `delete_rewrite`

All mutation tools (`create_*`, `update_*`, `delete_*`, `activate_*`, `set_autoresponder`, `reset_mailbox_password`) accept a `list[dict]` of items and return a bulk-result envelope with per-item success/failure. A single-item list works too.

## Resources

Read-only views addressable by URI:

- `domains://` — all domains on the account
- `domain://{name}` — one domain's full config
- `domain-records://{name}` — required DNS records for setup
- `domain-usage://{name}` — message + storage metrics
- `mailboxes://{domain}` — mailboxes for a domain
- `mailbox://{domain}/{local_part}` — one mailbox
- `identities://{domain}/{mailbox}` — identities on a mailbox
- `forwardings://{domain}/{mailbox}` — forwardings on a mailbox
- `aliases://{domain}` — aliases for a domain
- `rewrites://{domain}` — rewrite rules for a domain

## Notes

- Migadu's API returns HTTP 500 on successful DELETE (known quirk). The client treats 200/204/404/500 as success on DELETE; other codes raise.
- One long-lived `httpx.AsyncClient` per server process, closed on shutdown via FastMCP lifespan hook.
- `list_*` tools pass responses through a static summarizer when they exceed ~2000 tokens, returning a count plus a sample instead of flooding context.

## Development

```bash
git clone https://github.com/Michaelzag/migadu-mcp.git
cd migadu-mcp
uv sync --group dev

# Quality gates (same as CI)
uv run ruff format --check .
uv run ruff check migadu_mcp/ tests/
uv run ty check migadu_mcp/
uv run pytest
uv run bandit -r migadu_mcp/
```

Tests use `respx` to mock the Migadu API — no credentials needed. Integration tests (behind `@pytest.mark.integration`) hit the real API and are skipped by default.

## License

MIT — see [LICENSE](LICENSE).
