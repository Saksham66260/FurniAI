import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.agent.graph import graph

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


class AgentChatRequest(BaseModel):
    message: str = ""
    thread_id: str | None = None
    user_id: int = 1
    resume_approval: bool | None = None


class AgentChatResponse(BaseModel):
    thread_id: str
    status: str  # "COMPLETED", "APPROVAL_REQUIRED", "ERROR"
    reply: str
    tool_calls: list[dict] = []
    approval_required: bool = False
    approval_prompt: str | None = None
    checkout_result: dict | None = None


@router.post("/chat", response_model=AgentChatResponse)
def chat_with_agent(payload: AgentChatRequest):
    thread_id = payload.thread_id or f"session-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    try:
        if payload.resume_approval is not None:
            # Resuming an existing interrupt (human approval / rejection)
            result = graph.invoke(
                Command(resume=payload.resume_approval),
                config=config,
            )
        else:
            if not payload.message.strip():
                raise HTTPException(status_code=400, detail="Message cannot be empty.")

            result = graph.invoke(
                {
                    "messages": [HumanMessage(content=payload.message)],
                    "user_query": payload.message,
                    "user_id": payload.user_id,
                    "agent_steps": 0,
                    "human_approved": False,
                },
                config=config,
            )

        # Check for human approval interrupt
        if "__interrupt__" in result:
            interrupt_data = result["__interrupt__"][0]
            approval_msg = (
                interrupt_data.value.get("message", "Approval required to proceed.")
                if isinstance(interrupt_data.value, dict)
                else str(interrupt_data.value)
            )
            return AgentChatResponse(
                thread_id=thread_id,
                status="APPROVAL_REQUIRED",
                reply=approval_msg,
                approval_required=True,
                approval_prompt=approval_msg,
                tool_calls=[],
                checkout_result=None,
            )

        # Extract last assistant message & tool calls
        messages = result.get("messages", [])
        last_reply = ""
        tool_calls: list[dict] = []

        for msg in reversed(messages):
            if msg.type == "ai":
                if not last_reply and msg.content:
                    last_reply = str(msg.content)
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_calls.append({
                            "name": tc.get("name"),
                            "args": tc.get("args"),
                        })

        if not last_reply and messages:
            last_reply = str(messages[-1].content)

        checkout_result = result.get("checkout_result")

        return AgentChatResponse(
            thread_id=thread_id,
            status="COMPLETED",
            reply=last_reply or "Here is what I found for you.",
            tool_calls=tool_calls,
            approval_required=False,
            approval_prompt=None,
            checkout_result=checkout_result,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution error: {str(exc)}",
        )
