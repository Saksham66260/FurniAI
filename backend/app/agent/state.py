from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class ShoppingState(TypedDict, total=False):
    messages: Annotated[list[Any], add_messages]

    user_query: str

    # Trusted application-level identity.
    # The LLM must never provide this.
    user_id: int

    selected_product_ids: list[int]

    search_results: list[dict]

    checkout_ready: bool

    human_approved: bool

    checkout_result: dict

    agent_steps: int