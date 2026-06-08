from src.campusops.agent import CampusOpsAgent
from rich.console import Console
from rich.panel import Panel

console = Console()
agent = CampusOpsAgent()

console.print(Panel.fit("CampusOps Agent local demo\nType 'exit' to quit.", title="CampusOps"))

while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        break

    response = agent.respond(user_input, user_id="local-user", channel_id="local-demo")
    console.print(Panel(response["text"], title=f"CampusOps · {response['category']} · {response['priority']}"))
