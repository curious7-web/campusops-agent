# CampusOps Agent

**CampusOps Agent** is a Slack-native triage and handoff assistant for campus support teams.

It turns messy campus support messages into prioritized ticket cards, escalation checklists, safe next steps, and shift handoffs directly inside Slack.

## One-line pitch

CampusOps is the Slack-native shift lead for campus operations teams: it turns messy messages into safe ticket notes, owners, waiting-on states, escalation decisions, and handoffs before anything gets lost.

## Problem

Campus support teams handle chaotic requests across Slack, walk-ins, email, residence halls, events, and helpdesk queues. A single student-worker or RA shift might include:

* student portal access issues
* password/login problems
* phishing reports
* Google Workspace or Microsoft 365 access issues
* campus printing outages
* Wi-Fi/device problems
* classroom technology issues
* Residence Life/facilities concerns
* event questions
* shift handoffs

The hard part is not just answering the user. The hard part is knowing what information to collect, what not to ask for, when to escalate, who owns the issue, and how to hand off unresolved work to the next shift.

## Solution

CampusOps lives inside Slack. When a user mentions `@CampusOps` with a messy support issue, the agent:

* classifies the issue into a campus operations category
* assigns priority
* creates a ticket-style ID
* summarizes the problem
* suggests safe next steps
* shows what not to collect in Slack
* identifies escalation conditions
* tracks status, owner, and waiting-on state
* provides action buttons for resolving, escalating, assigning, or adding notes
* generates shift handoffs with `@CampusOps handoff`

## Current demo features

* Slack app built with Python and Slack Bolt
* Socket Mode support
* Slack thread replies
* Block Kit ticket cards
* ticket IDs such as `CO-0608201105`
* priority labels
* status tracking
* owner tracking
* waiting-on tracking
* privacy/safety warnings
* action buttons:

  * ✅ Resolve
  * 🚨 Escalate
  * 👤 Assign me
  * 📝 Add note
* shift handoff summaries grouped by queue state

## Supported demo categories

* IT · portal / student system / incoming student access
* Security · phishing / suspicious email
* IT · email / Google Workspace / Microsoft 365
* IT · printing / PaperCut / campus printing
* IT · account access / password reset
* Residence Life · facilities
* IT · classroom technology / loaner device
* IT · Wi-Fi / device connection
* Campus Ops · event Q&A
* Campus Ops · general triage

## Example prompts

```text
@CampusOps housing thing says no profile but email works and housing deadline is soon
```

```text
@CampusOps clicked sketchy email qr thing from wixsite but did not enter password
```

```text
@CampusOps Student says Gmail works but Google Drive and Docs say they don’t have access. They need files for class assignments.
```

```text
@CampusOps All campus printers on the first floor say unable to make a secure server connection. Staff need to print documents now.
```

```text
@CampusOps resident says heater not working and room freezing
```

```text
@CampusOps handoff
```

## Why Slack

Campus operations already happens in chat. Student workers, RAs, front desks, IT support, facilities coordinators, and event teams often coordinate informally before anything becomes a formal ticket.

CampusOps meets workers where they already are: Slack.

Instead of forcing every messy message into a form first, CampusOps converts the message into a structured, safe operational card.

## Why it matters

CampusOps helps:

* student workers respond consistently
* new staff avoid missing escalation rules
* RAs route urgent facilities issues safely
* IT teams reduce repeated triage mistakes
* security reports get escalated correctly
* shift handoffs become clearer
* messy English and typo-filled messages still get routed

The goal is not to replace official ticket systems. The goal is to make the messy first mile of support safer, faster, and easier to hand off.

## Privacy and safety

CampusOps is designed to avoid unsafe support behavior. It reminds workers not to collect:

* passwords
* OTP/MFA codes
* full student IDs
* Social Security numbers
* payment details
* private medical details
* sensitive screenshots
* full ID documents

For account access, identity verification, security incidents, and administrative changes, CampusOps prepares the case and routes it for human review instead of making risky changes automatically.

## Universal and configurable

CampusOps is not tied to one school. The demo uses small-college style workflows, but the architecture is meant to be configurable for any campus or student-services organization.

A real school could configure:

* portal names
* password reset links
* printing systems
* escalation teams
* residence-life workflows
* facilities routing
* ticket categories
* knowledge base links
* Slack channels
* ticket-system connectors

## Architecture

Current hackathon architecture:

```text
Slack workspace
   ↓
CampusOps Slack app
   ↓
Slack Bolt / Python app
   ↓
Rule-based triage engine
   ↓
YAML campus knowledge base
   ↓
Local JSONL ticket store
   ↓
Slack Block Kit ticket cards + handoff summaries
```

Future production architecture:

```text
Slack
   ↓
CampusOps Agent
   ↓
Campus config layer
   ↓
Ticket system connector
   ↓
Knowledge base connector
   ↓
Residence Life / Facilities connector
   ↓
Audit log + role-based access + admin settings
```

## Future integrations

Possible integrations include:

* TeamDynamix
* ServiceNow
* Jira Service Management
* Freshservice
* Zendesk
* ManageEngine ServiceDesk Plus
* Canvas, Moodle, Blackboard, Brightspace
* Google Workspace admin review workflows
* Microsoft 365 admin review workflows
* facilities work order systems
* housing/residence-life systems
* Slack Real-Time Search API
* MCP connectors
* Slack App Home dashboard

## Limitations

This is a hackathon demo. It currently uses:

* local JSONL storage
* fake ticket IDs
* configurable YAML knowledge
* local Socket Mode development

It does not directly reset passwords, modify accounts, change Google/Microsoft settings, or create official work orders. Those actions should remain human-approved in a real deployment.

CampusOps is a triage and handoff assistant, not an autonomous administrator.

## Running locally

Create a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run local demo:

```bash
python local_demo.py
```

Run Slack app:

```bash
python app.py
```

Required environment variables:

```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...
CAMPUSOPS_DEMO_MODE=true
```

Do not commit `.env`.

## Hackathon positioning

CampusOps is a new Slack agent for campus support teams. It is designed for the Slack Agent Builder Challenge as a practical organization workflow tool.

Best prize targets:

* New Slack Agent
* Best UX
* Slack Agent for Organizations

The strongest demo angle:

> CampusOps is not a chatbot that answers support questions. It is a Slack-native shift console that turns messy campus messages into safe ticket notes, owners, waiting-on states, escalation decisions, and handoffs before anything gets lost.
