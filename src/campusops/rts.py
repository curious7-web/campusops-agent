from __future__ import annotations

import os
from typing import List, Dict, Optional

from slack_sdk import WebClient


class RealTimeSearchClient:
    """
    Thin wrapper around Slack's assistant.search.context method.

    This is optional in local demo mode. In the hackathon demo, it is your
    strong technical differentiator: CampusOps can retrieve current Slack
    context without storing raw Slack workspace data.
    """

    def __init__(self):
        token = os.environ.get("SLACK_BOT_TOKEN")
        self.client = WebClient(token=token) if token else None

    def is_configured(self) -> bool:
        return self.client is not None

    def search(self, query: str, action_token: Optional[str], limit: int = 3) -> List[Dict]:
        if not self.client or not action_token:
            return []

        try:
            response = self.client.api_call(
                "assistant.search.context",
                json={
                    "query": query,
                    "channel_types": ["public_channel"],
                    "limit": min(limit, 20),
                    "action_token": action_token,
                },
            )
        except Exception:
            return []

        results = []
        for item in response.get("results", [])[:limit]:
            results.append({
                "title": item.get("channel_name") or "Slack context",
                "answer": item.get("text", "")[:300],
                "permalink": item.get("permalink", ""),
                "source": "Slack Real-Time Search",
            })
        return results
