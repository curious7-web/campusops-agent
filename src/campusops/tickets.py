from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional


class TicketStore:
    def __init__(self, path: str = "data/tickets.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        category: str,
        priority: str,
        summary: str,
        requester: str,
        channel_id: str,
        source_text: str,
        checklist: List[str],
        waiting_on: Optional[str] = None,
        owner: Optional[str] = None,
    ) -> str:
        ticket_id = f"CO-{datetime.now(timezone.utc).strftime('%m%d%H%M%S')}"

        if waiting_on is None:
            waiting_on = self._default_waiting_on(category, priority)

        record = {
            "id": ticket_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None,
            "status": "open",
            "owner": owner or "unassigned",
            "waiting_on": waiting_on,
            "escalated": False,
            "notes": [],
            "category": category,
            "priority": priority,
            "summary": summary,
            "requester": requester,
            "channel_id": channel_id,
            "source_text": source_text,
            "checklist": checklist,
        }

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        return ticket_id

    def _default_waiting_on(self, category: str, priority: str) -> str:
        c = category.lower()

        if "phishing" in c or "security" in c:
            return "user confirmation / security review"
        if "facilities" in c or "residence life" in c:
            return "location + campus team"
        if "portal" in c or "student system" in c or "incoming" in c:
            return "user direct-link test / admin review"
        if "google" in c or "microsoft" in c or "drive" in c:
            return "redacted screenshot / service review"
        if "printing" in c or "papercut" in c:
            return "location + scope confirmation"
        if "account" in c or "password" in c:
            return "identity-safe user confirmation"
        if priority in {"urgent", "high"}:
            return "campus team"
        return "user"

    def all(self) -> List[Dict]:
        if not self.path.exists():
            return []

        records = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def _write_all(self, records: List[Dict]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")

    def get(self, ticket_id: str) -> Optional[Dict]:
        for record in self.all():
            if record.get("id") == ticket_id:
                return record
        return None

    def update(self, ticket_id: str, **updates) -> Optional[Dict]:
        records = self.all()
        updated_record = None

        for record in records:
            if record.get("id") == ticket_id:
                record.update(updates)
                record["updated_at"] = datetime.now(timezone.utc).isoformat()
                updated_record = record
                break

        if updated_record:
            self._write_all(records)

        return updated_record

    def mark_resolved(self, ticket_id: str, user_id: str) -> Optional[Dict]:
        note = {
            "at": datetime.now(timezone.utc).isoformat(),
            "by": user_id,
            "text": "Marked resolved from Slack action.",
        }
        record = self.get(ticket_id)
        if not record:
            return None
        notes = record.get("notes", [])
        notes.append(note)
        return self.update(
            ticket_id,
            status="resolved",
            waiting_on="none",
            resolved_at=datetime.now(timezone.utc).isoformat(),
            notes=notes,
        )

    def escalate(self, ticket_id: str, user_id: str) -> Optional[Dict]:
        record = self.get(ticket_id)
        if not record:
            return None
        notes = record.get("notes", [])
        notes.append({
            "at": datetime.now(timezone.utc).isoformat(),
            "by": user_id,
            "text": "Escalated from Slack action.",
        })
        return self.update(
            ticket_id,
            status="escalated",
            escalated=True,
            waiting_on="campus team",
            notes=notes,
        )

    def assign_to(self, ticket_id: str, user_id: str) -> Optional[Dict]:
        record = self.get(ticket_id)
        if not record:
            return None
        notes = record.get("notes", [])
        notes.append({
            "at": datetime.now(timezone.utc).isoformat(),
            "by": user_id,
            "text": f"Assigned to <@{user_id}> from Slack action.",
        })
        return self.update(ticket_id, owner=f"<@{user_id}>", notes=notes)

    def add_demo_note(self, ticket_id: str, user_id: str) -> Optional[Dict]:
        record = self.get(ticket_id)
        if not record:
            return None
        notes = record.get("notes", [])
        notes.append({
            "at": datetime.now(timezone.utc).isoformat(),
            "by": user_id,
            "text": "Demo note added: follow up during next shift if still open.",
        })
        return self.update(ticket_id, notes=notes)

    def open_tickets(self, channel_id: str | None = None) -> List[Dict]:
        records = [r for r in self.all() if r.get("status") != "resolved"]
        if channel_id:
            records = [r for r in records if r.get("channel_id") == channel_id]
        return records

    def resolved_today(self, channel_id: str | None = None) -> List[Dict]:
        records = [r for r in self.all() if r.get("status") == "resolved"]
        if channel_id:
            records = [r for r in records if r.get("channel_id") == channel_id]
        return records
