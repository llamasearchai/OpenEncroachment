import os
from typing import Any

from agents import Agent, Runner, function_tool

from .tools import package_notification, run_pipeline, severity_summary

DEFAULT_MODEL = os.environ.get("OPENAI_AGENT_MODEL", "gpt-4o-mini")


@function_tool
def run_pipeline_tool(config: str | None = None, sample_data: bool = False) -> dict[str, Any]:
    """Run the end-to-end pipeline and return a summary."""
    return run_pipeline(config, sample_data)


@function_tool
def severity_summary_tool(config: str | None = None, limit: int = 100) -> dict[str, Any]:
    """Summarize incident severities."""
    return severity_summary(config, limit)


@function_tool
def package_notification_tool(incident_id: str, config: str | None = None) -> dict[str, Any]:
    """Create and write an outbound notification for an incident to the outbox."""
    return package_notification(incident_id, config)


def create_encroachment_agent(model: str = DEFAULT_MODEL) -> Agent:
    """Create the OpenEncroachment agent with integrated tools."""
    return Agent(
        name="OpenEncroachment Assistant",
        instructions="""
        You are the OpenEncroachment operator assistant. You help users monitor and respond to environmental threats and infrastructure protection incidents.

        Your capabilities include:
        - Running the complete threat detection pipeline
        - Analyzing incident severity and risk levels
        - Managing case notifications and responses
        - Providing insights into geofence breaches and threat patterns

        Always provide clear, actionable information and use the available tools to gather data before making recommendations.
        """,
        model=model,
        tools=[run_pipeline_tool, severity_summary_tool, package_notification_tool],
    )


def run_agent(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system: str = "You are the OpenEncroachment operator assistant.",
) -> dict[str, Any]:
    """Run the OpenEncroachment agent with the given prompt."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required")

    # Set the API key for the agents SDK
    os.environ["OPENAI_API_KEY"] = api_key

    try:
        agent = create_encroachment_agent(model)
        result = Runner.run_sync(agent, prompt)

        return {
            "ok": True,
            "output": result.final_output,
            "model": model,
            "agent_name": agent.name,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "model": model,
        }
