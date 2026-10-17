from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.agent.graph import graph


THREAD_ID = "furniai-demo-user-1"
USER_ID = 1


def run_agent(user_query: str):

    config = {
        "configurable": {
            "thread_id": THREAD_ID
        }
    }

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_query)
            ],
            "user_query": user_query,
            "user_id": USER_ID,
            "agent_steps": 0,
            "human_approved": False,
        },
        config=config,
    )

    return result, config


def print_messages(result):

    print("\nMESSAGES:\n")

    for message in result.get("messages", []):

        print(f"{message.type}:")
        print(message.content)

        if getattr(message, "tool_calls", None):

            print(
                "TOOL CALLS:",
                message.tool_calls
            )

        print("-" * 60)


if __name__ == "__main__":

    result, config = run_agent(
        "I want to checkout my cart."
    )

    # ========================================================
    # CHECK FOR HUMAN APPROVAL INTERRUPT
    # ========================================================

    if "__interrupt__" in result:

        interrupt_data = result["__interrupt__"][0]

        print("\n" + "=" * 60)
        print("HUMAN APPROVAL REQUIRED")
        print("=" * 60)

        print(interrupt_data.value["message"])

        answer = input("\nApprove checkout? (yes/no): ").strip().lower()

        if answer in {"yes", "y"}:

            print("\nApproval received. Executing checkout...\n")

            result = graph.invoke(
                Command(resume=True),
                config=config,
            )

        else:

            print("\nCheckout cancelled.")

            result = graph.invoke(
                Command(resume=False),
                config=config,
            )

    print_messages(result)

    print("\nGRAPH RESULT:")
    print(result)