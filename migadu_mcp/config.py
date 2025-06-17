#!/usr/bin/env python3
"""
Configuration management for Migadu MCP Server
"""

import os
from typing import Optional


class MigaduConfig:
    """Configuration settings for Migadu API"""

    def __init__(self):
        self.email = os.getenv("MIGADU_EMAIL")
        self.api_key = os.getenv("MIGADU_API_KEY")
        self.default_domain = os.getenv("MIGADU_DOMAIN")
        self._validate()

    def _validate(self):
        """Validate required configuration"""
        if not self.email or not self.api_key:
            raise Exception(
                "Please set MIGADU_EMAIL and MIGADU_API_KEY environment variables"
            )

    def get_default_domain(self) -> str:
        """Get the default domain from environment variables"""
        if not self.default_domain:
            raise Exception("Please set MIGADU_DOMAIN environment variable")
        return self.default_domain


# Global config instance
_config: Optional[MigaduConfig] = None


def get_config() -> MigaduConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = MigaduConfig()
    return _config
