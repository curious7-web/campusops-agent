# CampusOps Agent

CampusOps Agent is a Slack-native shift console for campus support teams.

It turns messy campus support messages into structured ticket cards with priority, owner, waiting-on state, safe next steps, escalation rules, privacy reminders, action buttons, and shift handoffs.

## Why

Campus support work is messy. A single shift can include:

* student portal issues
* phishing reports
* printer problems
* Wi-Fi issues
* residence hall facilities concerns
* classroom tech issues
* shift handoffs

CampusOps helps student workers, RAs, IT desks, and facilities teams turn those scattered Slack messages into clear operational actions.

## Required Slack technology

CampusOps includes an AI-assisted triage workflow inside Slack.

The project has an OpenAI-powered refinement path when `OPENAI_API_KEY` is configured and quota is available, plus a deterministic rule/safety fallback so the Slack demo stays reliable if the external AI API is unavailable.

## Features

* Slack app built with Python and Slack Bolt
* Socket Mode support
* Slack thread replies
* Slack Block Kit ticket cards
* AI-assisted triage path
* deterministic safety fallback
* YAML campus knowledge base
* local JSONL demo ticket store
* ticket status, owner, and waiting-on tracking
* action buttons:

  * Resolve
  * Escalate
  * Assign me
  * Add note
* shift handoff summaries with `@CampusOps handoff`

## Example prompts

```text
@CampusOps housing thing says no profile but email works and housing deadline is soon
```

```text
@CampusOps clicked sketchy email qr thing from wixsite but did not enter password
```

```text
@CampusOps resident says heater not working and room freezing
```

```text
@CampusOps handoff
```

## Architecture

```text
Slack workspace
   ↓
CampusOps Slack app
   ↓
Slack Bolt / Python
   ↓
AI-assisted triage layer
   ↓
OpenAI refinement path when available
   ↓
deterministic rule + safety fallback
   ↓
YAML campus knowledge base
   ↓
local JSONL ticket store
   ↓
Slack Block Kit cards + handoff summaries
```

## Privacy and safety

CampusOps reminds workers not to collect sensitive information in Slack, including:

* passwords
* OTP/MFA codes
* full student IDs
* SSNs
* payment details
* medical details
* sensitive screenshots

CampusOps does not reset passwords, modify accounts, or create official work orders. It prepares safe ticket notes and routes issues for human review.

## Running locally

Create a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:

```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...
OPENAI_API_KEY=optional_openai_key_here
CAMPUSOPS_DEMO_MODE=true
```

Run the Slack app:

```bash
python app.py
```

Run the local demo:

```bash
python local_demo.py
```

Do not commit `.env`.

## Built with

Python, Slack Bolt, Slack API, Slack Socket Mode, Slack Block Kit, OpenAI API integration path, YAML, JSONL.

## Hackathon

Built solo for the Slack Agent Builder Challenge.
