from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .knowledge import KnowledgeBase
from .tickets import TicketStore
from .rts import RealTimeSearchClient
from .safety import sanitize_user_text, contains_sensitive_data_warning
from .ai_triage import ai_refine_triage

@dataclass
class TriageResult:
    category: str
    priority: str
    summary: str
    checklist: List[str]
    escalation: str


class CampusOpsAgent:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.tickets = TicketStore()
        self.rts = RealTimeSearchClient()

    def respond(
        self,
        text: str,
        user_id: str,
        channel_id: str,
        action_token: Optional[str] = None,
    ) -> Dict:
        clean = sanitize_user_text(text)

        if self._is_handoff_request(clean):
            return self._handoff(user_id=user_id, channel_id=channel_id)

        triage = self._triage(clean)
        triage = ai_refine_triage(clean, triage)
        kb_matches = self.kb.search(clean, limit=3)

        live_sources = []
        if action_token and self.rts.is_configured():
            live_sources = self.rts.search(query=clean, action_token=action_token, limit=3)

        ticket_id = self.tickets.create(
            category=triage.category,
            priority=triage.priority,
            summary=triage.summary,
            requester=user_id,
            channel_id=channel_id,
            source_text=clean,
            checklist=triage.checklist,
        )

        ticket_record = self.tickets.get(ticket_id) or {}

        warning = ""
        if contains_sensitive_data_warning(clean):
            warning = "\n\n⚠️ Privacy note: avoid posting passwords, SSNs, medical details, or full student IDs in Slack. Use approved secure systems for sensitive data."

        sources_text = ""
        if kb_matches:
            sources_text += "\n\nRelevant campus knowledge:\n"
            for item in kb_matches:
                sources_text += f"• {item['title']}: {item['answer']}\n"

        if live_sources:
            sources_text += "\nLive Slack context:\n"
            for source in live_sources:
                title = source.get("title") or "Slack result"
                permalink = source.get("permalink") or ""
                sources_text += f"• {title} {permalink}\n"

        checklist = "\n".join([f"{i+1}. {step}" for i, step in enumerate(triage.checklist)])

        text_response = f"""Ticket `{ticket_id}` created.

*Category:* {triage.category}
*Priority:* {triage.priority}

*What I think is happening:* {triage.summary}

*Do this next:*
{checklist}

*Escalate when:* {triage.escalation}{sources_text}{warning}
"""

        return {
            "ticket_id": ticket_id,
            "category": triage.category,
            "priority": triage.priority,
            "summary": triage.summary,
            "checklist": triage.checklist,
            "escalation": triage.escalation,
            "status": ticket_record.get("status", "open"),
            "owner": ticket_record.get("owner", "unassigned"),
            "waiting_on": ticket_record.get("waiting_on", "user"),
            "privacy_warning": True,
            "sources": kb_matches + live_sources,
            "text": text_response.strip(),
        }

    def _is_handoff_request(self, text: str) -> bool:
        lowered = text.lower()
        return any(term in lowered for term in ["handoff", "shift summary", "end of shift", "unresolved"])

    def _handoff(self, user_id: str, channel_id: str) -> Dict:
        open_tickets = self.tickets.open_tickets(channel_id=channel_id)
        resolved = self.tickets.resolved_today(channel_id=channel_id)

        if not open_tickets and not resolved:
            text = "No unresolved CampusOps tickets in this channel. Handoff is clean ✅"
            return {
                "ticket_id": None,
                "category": "handoff",
                "priority": "normal",
                "summary": "No open tickets",
                "checklist": [],
                "escalation": "",
                "sources": [],
                "text": text,
            }

        high = [t for t in open_tickets if t.get("priority") in {"urgent", "high"}]
        waiting_user = [
            t for t in open_tickets
            if "user" in str(t.get("waiting_on", "")).lower()
            and t not in high
        ]
        waiting_team = [
            t for t in open_tickets
            if any(word in str(t.get("waiting_on", "")).lower() for word in ["team", "admin", "facilities", "security", "review"])
            and t not in high
        ]
        normal = [
            t for t in open_tickets
            if t not in high and t not in waiting_user and t not in waiting_team
        ]

        def fmt_ticket(t):
            owner = t.get("owner", "unassigned")
            waiting = t.get("waiting_on", "unknown")
            return f"• `{t['id']}` — {t.get('category')} — {t.get('priority')}\n  {t.get('summary')}\n  Owner: {owner} · Waiting on: {waiting}"

        def section(title, items, limit=3):
            if not items:
                return []
            lines = [f"*{title}*"]
            for item in items[:limit]:
                lines.append(fmt_ticket(item))
            if len(items) > limit:
                lines.append(f"+ {len(items) - limit} more. Use `@CampusOps handoff` after filtering/clearing resolved items.")
            lines.append("")
            return lines

        lines = []
        lines.append(f"Open tickets: {len(open_tickets)} · High: {len(high)} · Resolved this shift: {len(resolved)}")
        lines.append("")

        lines += section("🔥 High priority / time-sensitive", high)
        lines += section("🕓 Waiting on user", waiting_user)
        lines += section("🏢 Waiting on campus team", waiting_team)
        lines += section("🟡 Normal queue", normal)
        lines += section("✅ Resolved this shift", resolved, limit=2)

        lines.append("*Next shift checklist:*")
        lines.append("1. Handle urgent safety/security/deadline issues first.")
        lines.append("2. Confirm every high-priority ticket has an owner.")
        lines.append("3. Follow up on user screenshots or confirmations.")
        lines.append("4. Escalate repeated service failures or unclear ownership.")

        return {
            "ticket_id": None,
            "category": "handoff",
            "priority": "normal",
            "summary": "Shift handoff generated",
            "checklist": [],
            "escalation": "",
            "sources": [],
            "text": "\n".join(lines),
        }

    def _triage(self, text: str) -> TriageResult:
        t = text.lower()

        if any(k in t for k in ["phishing", "suspicious email", "clicked link", "qr code", "validate gmail", "wixsite"]):
            urgent = any(k in t for k in ["entered password", "entered credentials", "gave password", "submitted password"])
            return TriageResult(
                category="Security · phishing / suspicious email",
                priority="urgent" if urgent else "high",
                summary="This appears to be a suspicious email or phishing-report workflow.",
                checklist=[
                    "Tell the user not to click the link again or enter credentials.",
                    "Ask whether they only clicked, or whether they entered username/password.",
                    "Collect a screenshot or forwarded copy without exposing private data.",
                    "Escalate immediately if credentials were entered or many users received it.",
                ],
                escalation="credentials were entered, the sender appears internal, multiple users received it, or the message asks for password/QR validation.",
            )

        if any(k in t for k in ["pridenet", "portal", "housing", "no profile", "incoming student", "soar", "math placement", "adirondack"]):
            high = any(k in t for k in ["deadline", "today", "soon", "urgent", "due"])
            return TriageResult(
                category="IT · PrideNET / portal / incoming student access",
                priority="high" if high else "normal",
                summary="This appears to be an incoming-student portal or PrideNET access issue.",
                checklist=[
                    "Confirm user status: incoming student, current student, alumni, staff, or faculty.",
                    "Ask which exact portal/link they used and what error appears.",
                    "Use the official TechHelp/direct-link path when available instead of guessing.",
                    "If housing/profile is missing, route to the proper admin or Residence Life owner.",
                ],
                escalation="a direct official link still fails, the profile appears missing, or a deadline is today/soon.",
            )

        if any(k in t for k in ["google drive", "google docs", "drive disabled", "docs disabled", "gmail works", "google apps"]):
            return TriageResult(
                category="IT · Google apps / Drive / Docs",
                priority="high" if any(k in t for k in ["assignment", "class", "blocked", "deadline"]) else "normal",
                summary="This appears to be a Google app provisioning issue where email may work but Drive/Docs access does not.",
                checklist=[
                    "Confirm whether Gmail works and whether only Drive/Docs are blocked.",
                    "Ask for a redacted screenshot of the Google app error.",
                    "Confirm active user status without asking for passwords or OTP codes.",
                    "Escalate for Google service/access review if the account should be active.",
                ],
                escalation="active user services appear disabled, coursework/work is blocked, or multiple Google apps are inaccessible.",
            )

        if any(k in t for k in ["projector", "classroom", "audio", "zoom", "hdmi", "class starting", "exam", "loaner laptop", "presentation"]):
            urgent = any(k in t for k in ["class", "exam", "starting", "now", "today", "monday"])
            return TriageResult(
                category="IT · classroom technology / loaner device",
                priority="high" if urgent else "normal",
                summary="This appears to be a classroom technology, AV, or loaner-device request.",
                checklist=[
                    "Collect building, room, class/event time, and affected equipment.",
                    "Confirm whether the class, exam, or event is already blocked.",
                    "Record constraints such as no internet, specific software, or pickup time.",
                    "Escalate to technician/AV support if the event is soon or currently blocked.",
                ],
                escalation="class is active, exam/event is soon, AV hardware failed, or loaner constraints are time-sensitive.",
            )

        if any(k in t for k in ["password", "login", "sign in", "locked out", "reset", "mfa", "challenge questions"]):
            return TriageResult(
                category="IT · account access",
                priority="high" if any(k in t for k in ["locked", "cannot", "class", "today", "faculty", "staff"]) else "normal",
                summary="The request appears to be an account access or password/login issue.",
                checklist=[
                    "Confirm the requester is the account owner using approved identity-verification procedure.",
                    "Ask what system is affected: email, portal, Wi-Fi, printer, or another campus app.",
                    "Have them try the official password reset/help page, not a random link.",
                    "If reset succeeds, ask them to sign out/in on phone, laptop, and saved Wi-Fi credentials.",
                    "If still blocked, collect non-sensitive context: error text, system name, time, and device type.",
                ],
                escalation="identity cannot be verified, the account is locked, MFA is broken, or the issue affects payroll/academic access.",
            )

        if any(k in t for k in ["printer", "printing", "print", "pridnet", "papercut", "paper jam", "secure server connection", "access denied"]):
            high = any(k in t for k in ["all", "multiple", "staff need", "secure server connection", "outage"])
            return TriageResult(
                category="IT · printing / PaperCut",
                priority="high" if high else "normal",
                summary="The request appears to be a campus printing or PaperCut issue.",
                checklist=[
                    "Ask for printer location, printer name/area, and exact error message.",
                    "Confirm whether this affects one user, one printer, multiple printers, or multiple users.",
                    "Check whether the user is on the required campus network or print path.",
                    "For access denied, verify whether access should already be provisioned.",
                    "For hardware or widespread issues, route to the printer support queue.",
                ],
                escalation="multiple users/printers are affected, secure server connection error appears, or there is hardware failure.",
            )

        if any(k in t for k in ["wifi", "wi-fi", "network", "internet", "connection", "eduroam"]):
            return TriageResult(
                category="IT · Wi-Fi / device connection",
                priority="high" if any(k in t for k in ["class", "event", "multiple", "building"]) else "normal",
                summary="This appears to be a Wi-Fi or device connection issue.",
                checklist=[
                    "Collect building/room, device type, network name, and exact error.",
                    "Ask whether one user, several users, or a whole area is affected.",
                    "Have the user test another approved network/device path if available.",
                    "Escalate if multiple users or a class/event/work function is blocked.",
                ],
                escalation="multiple users are affected, a classroom/event/work function is blocked, or a building-wide issue is suspected.",
            )

        if any(k in t for k in ["heater", "heat", "ac", "air conditioning", "leak", "maintenance", "room", "door", "lock", "freezing", "flood"]):
            urgent = any(k in t for k in ["flood", "leak", "freezing", "no heat", "locked out", "unsafe"])
            return TriageResult(
                category="Residence Life · facilities",
                priority="urgent" if urgent else "normal",
                summary="The request appears to be a residence hall facilities or room-maintenance issue.",
                checklist=[
                    "Identify building, room, issue type, and whether it is currently unsafe.",
                    "For safety/lockout/no-heat/flooding, contact the on-call/residence-life escalation path immediately.",
                    "For routine maintenance, submit a facilities request with location and clear description.",
                    "Tell the resident what temporary workaround is allowed and what is not allowed.",
                    "Log the issue for shift handoff until an owner confirms receipt.",
                ],
                escalation="safety risk, lockout, flooding, no heat in cold weather, electrical issue, or repeated unresolved request.",
            )

        if any(k in t for k in ["event", "schedule", "where is", "when is", "meeting", "orientation"]):
            return TriageResult(
                category="Campus Ops · event Q&A",
                priority="normal",
                summary="The request appears to be about schedule, location, or event information.",
                checklist=[
                    "Search the approved schedule/source of truth first.",
                    "Reply with time, place, eligibility, and who to contact.",
                    "If information conflicts, state the uncertainty and link the official source.",
                    "If the user needs accommodation or access support, route to the appropriate office.",
                ],
                escalation="the event is happening today, the posted information conflicts, or accessibility support is requested.",
            )

        return TriageResult(
            category="Campus Ops · general triage",
            priority="normal",
            summary="This looks like a general campus operations request that needs routing.",
            checklist=[
                "Restate the request in one sentence.",
                "Identify owner: IT, Residence Life, Facilities, Student Affairs, Dining, or Events.",
                "Collect minimum useful context without sensitive data.",
                "Give the requester the next action and expected follow-up path.",
            ],
            escalation="there is safety risk, repeated failure, sensitive information, or no clear owner.",
        )

