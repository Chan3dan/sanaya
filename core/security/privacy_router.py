"""Privacy rules that force sensitive requests to local models."""

import re
from typing import Any

from core.config import config


class PrivacyRouter:
    """Evaluates whether a request must remain local."""

    sensitive_patterns = [
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        re.compile(r"\bpassword\b", re.IGNORECASE),
        re.compile(r"\b(bank|credit card|routing|account number)\b", re.IGNORECASE),
        re.compile(r"\b(health|diagnosis|prescription|medical)\b", re.IGNORECASE),
    ]

    def requires_local(self, context: dict[str, Any]) -> bool:
        """Return True when privacy rules require local processing."""
        memories = context.get("memories", [])
        if any(memory.get("is_private") for memory in memories if isinstance(memory, dict)):
            return True
        if config.privacy_mode:
            return True
        content = str(context.get("content", ""))
        if any(pattern.search(content) for pattern in self.sensitive_patterns):
            return True
        return context.get("task_type") == "embedding"
