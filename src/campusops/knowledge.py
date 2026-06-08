from __future__ import annotations

import yaml
from pathlib import Path
from typing import List, Dict


class KnowledgeBase:
    def __init__(self, path: str = "data/campus_kb.yaml"):
        self.path = Path(path)
        self.items = self._load()

    def _load(self) -> List[Dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("items", [])

    def search(self, query: str, limit: int = 3) -> List[Dict]:
        q = query.lower()

        category_to_kb_id = [
            ("kb-phishing", ["phishing", "suspicious email", "clicked link", "qr code", "validate gmail", "wixsite"]),
            ("kb-pridenet-portal", ["pridenet", "portal", "student self-service", "soar", "math placement", "housing", "no profile", "incoming student", "adirondack"]),
            ("kb-google-apps", ["gmail works", "google drive", "google docs", "drive disabled", "docs disabled", "google apps"]),
            ("kb-classroom-tech", ["projector", "classroom", "audio", "zoom", "hdmi", "class starting", "exam", "loaner laptop", "presentation"]),
            ("kb-password-reset", ["password", "reset", "login", "account", "mfa", "locked", "sign in", "challenge questions"]),
            ("kb-printer-access", ["printer", "print", "printing", "papercut", "access denied", "secure server connection", "paper jam"]),
            ("kb-wifi", ["wifi", "wi-fi", "network", "device connection", "internet connection", "eduroam"]),
            ("kb-facilities-urgent", ["heater", "heat", "ac", "air conditioning", "leak", "flood", "maintenance", "room", "lockout", "freezing", "facilities"]),
        ]

        wanted_id = None
        for kb_id, words in category_to_kb_id:
            if any(word in q for word in words):
                wanted_id = kb_id
                break

        if not wanted_id:
            return []

        for item in self.items:
            if item.get("id") == wanted_id:
                return [item]

        return []
