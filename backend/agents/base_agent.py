"""
Base Agent - shared base class for all HR agents
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseAgent:
    """Minimal base class providing common agent interface"""

    def __init__(self):
        self.agent_name = "base_agent"
        self.is_initialized = False

    async def initialize(self):
        self.is_initialized = True

    def is_ready(self) -> bool:
        return self.is_initialized
