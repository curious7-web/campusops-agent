"""
CampusOps Agent Slack entrypoint.

This is a straightforward Bolt for Python app. For the official hackathon route,
you can also scaffold with `slack create agent` and move the CampusOpsAgent logic
into the generated agent template.
"""

import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from src.campusops.agent import CampusOpsAgent
from src.campusops.formatting import slack_blocks_for_response, ticket_update_blocks

load_dotenv()

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

agent = CampusOpsAgent()


@app.event("app_mention")
def handle_app_mention(event, say, client, logger):
    text = event.get("text", "")
    user_id = event.get("user", "unknown")
    channel_id = event.get("channel", "unknown")
    thread_ts = event.get("thread_ts") or event.get("ts")

    # Slack RTS API bot-token searches require action_token when available.
    action_token = event.get("action_token")

    result = agent.respond(
        text,
        user_id=user_id,
        channel_id=channel_id,
        action_token=action_token,
    )

    say(
        text=result["text"],
        blocks=slack_blocks_for_response(result),
        thread_ts=thread_ts,
    )


@app.message("")
def handle_dm(message, say, logger):
    # In real deployment, limit this to DMs or agent container events.
    channel_type = message.get("channel_type")
    if channel_type not in {"im", "mpim"}:
        return

    result = agent.respond(
        message.get("text", ""),
        user_id=message.get("user", "unknown"),
        channel_id=message.get("channel", "unknown"),
        action_token=message.get("action_token"),
    )

    say(text=result["text"], blocks=slack_blocks_for_response(result))


@app.command("/campusops")
def handle_slash_command(ack, body, respond):
    ack()
    text = body.get("text", "")
    result = agent.respond(
        text,
        user_id=body.get("user_id", "unknown"),
        channel_id=body.get("channel_id", "unknown"),
    )
    respond(blocks=slack_blocks_for_response(result), text=result["text"])




@app.action("campusops_resolve")
def handle_resolve(ack, body, respond, logger):
    ack()
    ticket_id = body["actions"][0]["value"]
    user_id = body.get("user", {}).get("id", "unknown")
    ticket = agent.tickets.mark_resolved(ticket_id, user_id)
    if not ticket:
        respond(text=f"Could not find ticket `{ticket_id}`.")
        return
    respond(
        text=f"Ticket {ticket_id} marked resolved.",
        blocks=ticket_update_blocks(ticket, "✅ Ticket marked resolved"),
        replace_original=False,
    )


@app.action("campusops_escalate")
def handle_escalate(ack, body, respond, logger):
    ack()
    ticket_id = body["actions"][0]["value"]
    user_id = body.get("user", {}).get("id", "unknown")
    ticket = agent.tickets.escalate(ticket_id, user_id)
    if not ticket:
        respond(text=f"Could not find ticket `{ticket_id}`.")
        return
    respond(
        text=f"Ticket {ticket_id} escalated.",
        blocks=ticket_update_blocks(ticket, "🚨 Ticket escalated"),
        replace_original=False,
    )


@app.action("campusops_assign")
def handle_assign(ack, body, respond, logger):
    ack()
    ticket_id = body["actions"][0]["value"]
    user_id = body.get("user", {}).get("id", "unknown")
    ticket = agent.tickets.assign_to(ticket_id, user_id)
    if not ticket:
        respond(text=f"Could not find ticket `{ticket_id}`.")
        return
    respond(
        text=f"Ticket {ticket_id} assigned.",
        blocks=ticket_update_blocks(ticket, f"👤 Ticket assigned to <@{user_id}>"),
        replace_original=False,
    )


@app.action("campusops_add_note")
def handle_add_note(ack, body, respond, logger):
    ack()
    ticket_id = body["actions"][0]["value"]
    user_id = body.get("user", {}).get("id", "unknown")
    ticket = agent.tickets.add_demo_note(ticket_id, user_id)
    if not ticket:
        respond(text=f"Could not find ticket `{ticket_id}`.")
        return
    respond(
        text=f"Note added to {ticket_id}.",
        blocks=ticket_update_blocks(ticket, "📝 Demo note added: follow up during next shift if still open"),
        replace_original=False,
    )


if __name__ == "__main__":
    token = os.environ.get("SLACK_APP_TOKEN")
    if not token:
        raise RuntimeError("Missing SLACK_APP_TOKEN. Copy .env.example to .env and fill credentials.")
    SocketModeHandler(app, token).start()
