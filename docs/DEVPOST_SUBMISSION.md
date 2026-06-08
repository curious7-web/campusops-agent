# Devpost submission draft

## Project name

CampusOps Agent

## One-liner

A Slack-native AI agent that helps campus IT workers, RAs, and student operations teams triage requests, route issues, and generate shift handoffs.

## Inspiration

Student workers and RAs often become the first line of support for everything: password lockouts, printer access, room maintenance, event questions, and policy confusion. These requests arrive informally and often lack the details needed to solve them. CampusOps Agent was inspired by real campus operations work where the challenge is not just answering questions but turning messy requests into safe next actions.

## What it does

CampusOps Agent works inside Slack. A user can mention the agent or message it directly with a campus operations issue. The agent classifies the issue, assigns a priority, gives a step-by-step checklist, identifies when to escalate, and creates a lightweight ticket record. At the end of a shift, staff can ask for a handoff summary and receive a structured list of unresolved items.

The prototype handles:
- password/login helpdesk triage
- printer/access troubleshooting
- residence hall maintenance routing
- event schedule Q&A
- escalation checklists
- shift handoff summaries

## How we built it

The prototype uses Python and Slack Bolt. The agent has a deterministic triage layer for reliability during demos, a YAML knowledge base for campus policy/helpdesk answers, a ticket metadata store, and an optional Slack Real-Time Search integration through `assistant.search.context` for live Slack context. The architecture is designed to avoid storing raw Slack workspace content unless an organization explicitly permits it.

## Slack technology used

- New Slack agent/app surface
- Slack Bolt for Python
- Slack messages and Block Kit formatting
- Optional Slack Real-Time Search API for live workspace context
- Designed to be portable into the official `slack create agent` template

## Challenges

The biggest design challenge was balancing usefulness with safety. Campus operations often touches sensitive information, so the agent intentionally avoids collecting passwords, medical details, or unnecessary student data. Another challenge was making the demo reliable while still showing how live Slack context could make the agent more powerful.

## What we learned

We learned that the winning pattern is not "chatbot answers question." It is "agent turns messy operational work into a safe workflow." Slack is a strong surface for this because the handoff, escalation, and team context already live there.

## What is next

Next steps:
- Add official Slack Agent Builder template integration
- Add persistent ticket status buttons
- Add App Home dashboard
- Add organization-specific policy connectors
- Add role-based routing for IT, Residence Life, Facilities, and Events
- Prepare the app for Slack Marketplace submission
