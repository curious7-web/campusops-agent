# 3-minute demo script

## 0:00–0:20 — Problem

"Campus student workers and RAs answer the same operational questions every day: password issues, printing, room maintenance, event schedules, and shift handoffs. The problem is not one hard ticket. The problem is dozens of messy small requests with missing context."

## 0:20–0:45 — Introduce CampusOps

"CampusOps is a Slack-native agent for campus operations teams. It triages requests, gives next steps, routes issues, and creates shift handoffs without leaving Slack."

## 0:45–1:20 — IT/helpdesk triage demo

Prompt:

```text
@CampusOps student cannot log in after password reset and needs help before class
```

Show:
- Category: IT account access
- Priority: high
- Identity verification reminder
- Approved reset/help page reminder
- Escalation conditions

Say:

"Notice it does not ask for a password. It gives a safe checklist and tells the worker when to escalate."

## 1:20–1:55 — RA/facilities demo

Prompt:

```text
@CampusOps resident says heater is not working and the room is freezing
```

Show:
- Category: Residence Life facilities
- Priority: urgent
- Building/room/safety checklist
- On-call escalation

Say:

"This is where the agent becomes operations-specific, not just a generic chatbot."

## 1:55–2:25 — Live context / RTS story

Prompt:

```text
@CampusOps what did we say last week about printer access?
```

Say:

"When configured with Slack Real-Time Search, CampusOps can retrieve relevant Slack context at request time, while respecting Slack permissions and avoiding a separate database of raw Slack messages."

## 2:25–2:50 — Shift handoff

Prompt:

```text
@CampusOps handoff
```

Show:
- High-priority open tickets
- Normal queue
- Next shift checklist

Say:

"This is the payoff: the end of the shift is no longer a memory game."

## 2:50–3:00 — Close

"CampusOps can start on a college campus, but the pattern works for nonprofits, coworking spaces, clinics, small companies, and volunteer teams—any organization where frontline staff need fast, safe routing."
