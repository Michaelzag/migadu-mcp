"""Configuration for the Migadu MCP server."""

import os


class MigaduConfigError(ValueError):
    """Raised when required Migadu configuration is missing."""


class MigaduConfig:
    """Loads Migadu credentials and the optional default domain from env vars."""

    def __init__(self) -> None:
        self.email = os.getenv("MIGADU_EMAIL")
        self.api_key = os.getenv("MIGADU_API_KEY")
        self.default_domain = os.getenv("MIGADU_DOMAIN")
        if not self.email or not self.api_key:
            raise MigaduConfigError(
                "Set MIGADU_EMAIL and MIGADU_API_KEY environment variables"
            )


_config: MigaduConfig | None = None


def get_config() -> MigaduConfig:
    global _config
    if _config is None:
        _config = MigaduConfig()
    return _config
