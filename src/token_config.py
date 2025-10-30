"""Backward-compatible export for legacy imports.

Older scripts import configuration constants from ``src.token_config`` while
newer modules live under ``src.config.token_config``. Re-export everything here
so both paths stay valid without duplicating logic.
"""

from .config.token_config import *  # noqa: F401,F403


