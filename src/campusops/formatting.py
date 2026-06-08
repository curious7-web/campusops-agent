from __future__ import annotations

from typing import Dict, List


def _priority_label(priority: str) -> str:
    p = (priority or "normal").lower()
    if p == "urgent":
        return "🔴 URGENT"
    if p == "high":
        return "🟠 HIGH"
    if p == "low":
        return "⚪ LOW"
    return "🟡 NORMAL"


def _status_label(status: str) -> str:
    s = (status or "open").lower()
    if s == "resolved":
        return "✅ Resolved"
    if s == "escalated":
        return "🚨 Escalated"
    if s == "waiting_on_user":
        return "Waiting on user"
    if s == "waiting_on_team":
        return "Waiting on campus team"
    return "Open"


def slack_blocks_for_response(result: Dict):
    category = result.get("category", "CampusOps")

    if category == "handoff":
        handoff_text = result.get("text", "No handoff available.")
        handoff_text = handoff_text.replace("*CampusOps shift handoff*\n\n", "")
        return [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "CampusOps · Shift Handoff", "emoji": True},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": handoff_text[:3000]},
            },
        ]

    ticket_id = result.get("ticket_id") or "N/A"
    priority = result.get("priority", "normal")
    status = result.get("status", "open")
    owner = result.get("owner", "unassigned")
    waiting_on = result.get("waiting_on", "user")
    checklist = result.get("checklist", [])[:3]

    blocks: List[Dict] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"CampusOps · {category}", "emoji": True},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Priority:*\n{_priority_label(priority)}"},
                {"type": "mrkdwn", "text": f"*Ticket:*\n`{ticket_id}`"},
                {"type": "mrkdwn", "text": f"*Status:*\n{_status_label(status)}"},
                {"type": "mrkdwn", "text": f"*Waiting on:*\n{waiting_on}"},
                {"type": "mrkdwn", "text": f"*Owner:*\n{owner}"},
            ],
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Summary:*\n{result.get('summary', '')}"},
        },
    ]

    if checklist:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Top next steps:*\n" + "\n".join([f"{i+1}. {x}" for i, x in enumerate(checklist)]),
            },
        })

    if result.get("privacy_warning"):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Do not collect:*\nPasswords, OTP/MFA codes, full IDs, SSNs, payment details, or sensitive screenshots in Slack.",
            },
        })

    if result.get("escalation"):
        blocks.append({
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"*Escalate when:* {result['escalation']}"}],
        })

    if ticket_id != "N/A":
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✅ Resolve", "emoji": True},
                    "style": "primary",
                    "action_id": "campusops_resolve",
                    "value": ticket_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🚨 Escalate", "emoji": True},
                    "style": "danger",
                    "action_id": "campusops_escalate",
                    "value": ticket_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "👤 Assign me", "emoji": True},
                    "action_id": "campusops_assign",
                    "value": ticket_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📝 Add note", "emoji": True},
                    "action_id": "campusops_add_note",
                    "value": ticket_id,
                },
            ],
        })

    return blocks


def ticket_update_blocks(ticket: Dict, message: str):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{message}*\n"
                    f"*Ticket:* `{ticket.get('id')}`\n"
                    f"*Status:* {_status_label(ticket.get('status', 'open'))}\n"
                    f"*Owner:* {ticket.get('owner', 'unassigned')}\n"
                    f"*Waiting on:* {ticket.get('waiting_on', 'user')}"
                ),
            },
        }
    ]
