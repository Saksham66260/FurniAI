import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import SystemMessage, AIMessage

from app.agent.state import ShoppingState
from app.agent.llm import llm
from app.agent.tools import (
    search_products,
    compare_products,
    check_inventory_and_delivery,
    get_product_knowledge,
    checkout,
)

from app.db.database import SessionLocal
from app.services.order_service import OrderService


# ============================================================
# TOOLS
# ============================================================

tools = [
    search_products,
    compare_products,
    check_inventory_and_delivery,
    get_product_knowledge,
    checkout,
]

llm_with_tools = llm.bind_tools(tools)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are FurniAI, an AI shopping assistant.

Your job is to help users discover, evaluate, and purchase furniture.

IMPORTANT RULES:

1. The database and tool results are the source of truth.

2. Never invent product specifications, prices, inventory,
   delivery times, assembly instructions, materials, features,
   ratings, or policies.

3. If a fact is not present in the tool results, say that the
   information is not currently available.

4. Use search_products for product discovery.

5. Use compare_products when exact product specifications
   are needed.

6. Use check_inventory_and_delivery for current inventory.

7. Use get_product_knowledge for product documentation,
   assembly, care, manuals, or related product knowledge.

8. Use checkout ONLY when the user explicitly wants to
   place an order.

9. Checkout requires human approval.

10. Never claim checkout succeeded unless the application
    returns a successful checkout result.

11. Never invent an order ID.

12. Never invent a total price.

13. Never claim an order was placed before the application
    confirms successful order creation.

14. NEVER ask the user for a user_id.

15. NEVER ask the user for an idempotency key.

16. The authenticated user identity and idempotency key are
    controlled by the application layer.

17. Do not call checkout merely to calculate a price.

18. Do not call checkout for product discovery or comparison.

19. Do not call tools unnecessarily.

20. Never make unsupported factual claims.
"""


# ============================================================
# AGENT NODE
# ============================================================

MAX_AGENT_STEPS = 8


def agent_node(state: ShoppingState):

    current_steps = state.get("agent_steps", 0) + 1

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response],
        "agent_steps": current_steps,
    }


# ============================================================
# ROUTING
# ============================================================

def should_continue(state: ShoppingState):

    current_steps = state.get("agent_steps", 0)

    if current_steps >= MAX_AGENT_STEPS:
        return END

    last_message = state["messages"][-1]

    tool_calls = getattr(last_message, "tool_calls", None)

    if not tool_calls:
        return END

    # Checkout gets a special approval gate.
    for tool_call in tool_calls:
        if tool_call["name"] == "checkout":
            return "approval"

    return "tools"


# ============================================================
# HUMAN APPROVAL
# ============================================================

def approval_node(state: ShoppingState):

    approval_request = {
        "type": "checkout_confirmation",
        "message": (
            "Your cart is ready for checkout. "
            "Do you approve creating the order?"
        ),
    }

    approved = interrupt(approval_request)

    if approved is not True:
        return {
            "human_approved": False,
            "checkout_result": {
                "success": False,
                "status": "CANCELLED",
                "message": "Checkout was cancelled by the user.",
            },
            "messages": [
                AIMessage(
                    content="Checkout was cancelled. No order was created."
                )
            ],
        }

    # ========================================================
    # HUMAN APPROVED
    # ========================================================

    user_id = state.get("user_id")

    if user_id is None:
        raise ValueError(
            "Authenticated user_id is missing from application state."
        )

    # Application generates the idempotency key.
    idempotency_key = f"agent-checkout-{uuid.uuid4()}"

    db = SessionLocal()

    try:
        order = OrderService.create_order(
            db=db,
            user_id=user_id,
            idempotency_key=idempotency_key,
        )

        result = {
            "success": True,
            "status": order.status,
            "order_id": order.id,
            "user_id": order.user_id,
            "total_amount": float(order.total_amount),
        }

    except Exception as exc:

        result = {
            "success": False,
            "status": "FAILED",
            "message": str(exc),
        }

    finally:
        db.close()

    # ========================================================
    # RETURN RESULT TO AGENT STATE
    # ========================================================

    if result["success"]:

        message = (
            f"Order successfully created. "
            f"Order ID: {result['order_id']}. "
            f"Total: {result['total_amount']:.2f}. "
            f"Status: {result['status']}."
        )

    else:

        message = (
            f"Checkout failed. "
            f"Reason: {result.get('message', 'Unknown error')}."
        )

    return {
        "human_approved": True,
        "checkout_result": result,
        "messages": [
            AIMessage(content=message)
        ],
    }


# ============================================================
# TOOL NODE
# ============================================================

tool_node = ToolNode(tools)


# ============================================================
# GRAPH
# ============================================================

builder = StateGraph(ShoppingState)

builder.add_node("agent", agent_node)
builder.add_node("approval", approval_node)
builder.add_node("tools", tool_node)

builder.add_edge(
    START,
    "agent",
)

builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "approval": "approval",
        END: END,
    },
)

# IMPORTANT:
# Approval directly finishes checkout.
# It does NOT go back to ToolNode.
builder.add_edge(
    "approval",
    END,
)

builder.add_edge(
    "tools",
    "agent",
)


# ============================================================
# CHECKPOINTING
# ============================================================

checkpointer = MemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)