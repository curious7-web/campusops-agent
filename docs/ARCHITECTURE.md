# CampusOps Agent architecture

```mermaid
flowchart TD
    U[Student worker / RA / IT staff in Slack] --> S[CampusOps Slack Agent]

    S --> T[Triage Engine]
    T --> K[Campus Knowledge Base]
    T --> R[Slack Real-Time Search API optional]
    T --> Q[Ticket Metadata Store]
    T --> H[Handoff Generator]

    K --> A[Answer with policy/source hints]
    R --> A
    Q --> H
    H --> A

    A --> B[Slack message with blocks: category, priority, steps, escalation]
```

## Components

### Slack surface
CampusOps lives where student workers already coordinate: Slack DMs, app mentions, slash command, and eventually App Home.

### Triage engine
Classifies requests into:
- IT account access
- IT printing
- Residence Life/facilities
- Event Q&A
- General campus operations

### Knowledge layer
A small local YAML knowledge base powers deterministic responses in demo mode. This keeps the project stable for video recording.

### Real-Time Search layer
When available, the agent calls Slack `assistant.search.context` to retrieve relevant Slack messages/files at request time. This demonstrates secure live context without storing Slack workspace content.

### Ticket metadata store
Stores lightweight records:
- ticket ID
- category
- priority
- summary
- requester/channel metadata
- checklist

Production version should avoid raw Slack message storage unless the organization explicitly permits it.

### Handoff generator
Aggregates unresolved items into an end-of-shift handoff for the next worker.

## Privacy posture

CampusOps is designed for FERPA-aware / workplace-aware contexts:
- Never ask for passwords in Slack.
- Avoid storing raw Slack content.
- Warn users when sensitive data appears.
- Pull context just in time through Slack permissions.
