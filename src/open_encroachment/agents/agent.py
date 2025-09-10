import json
import os
from typing import Any

from openai import OpenAI

from .tools import call_tool, tool_schemas

DEFAULT_MODEL = os.environ.get("OPENAI_AGENT_MODEL", "gpt-4o-mini")


def run_agent(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system: str = "You are the OpenEncroachment operator assistant.",
) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment.")

    client = OpenAI(api_key=api_key)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    tools = tool_schemas()

    # Loop handling for tool calls
    for _ in range(8):
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                arguments = tool_call.function.arguments or "{}"
                tool_result = call_tool(name, arguments)
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": json.dumps(tool_result),
                }
                messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call]})
                messages.append(tool_msg)
            continue
        # No tool calls; final assistant message
        messages.append({"role": "assistant", "content": msg.content})
        return {
            "ok": True,
            "messages": messages,
            "output": msg.content,
            "model": model,
        }
    return {"ok": False, "error": "Tool loop exceeded limit"}
