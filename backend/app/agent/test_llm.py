from app.agent.llm import llm
from app.agent.tools import search_products


llm_with_tools = llm.bind_tools([
    search_products
])


messages = [
    ("user", "Find me an oak desk under 15000")
]


# 1. LLM decides which tool to use
response = llm_with_tools.invoke(messages)

print("LLM TOOL CALL:")
print(response.tool_calls)


# 2. Execute the requested tool
tool_call = response.tool_calls[0]

tool_result = search_products.invoke(tool_call["args"])

print("\nTOOL RESULT:")
print(tool_result[:2])


# 3. Give the tool result back to the LLM
messages.append(response)

messages.append({
    "role": "tool",
    "tool_call_id": tool_call["id"],
    "content": str(tool_result),
})


# 4. LLM generates final answer
final_response = llm_with_tools.invoke(messages)

print("\nFINAL LLM RESPONSE:")
print(final_response.content)