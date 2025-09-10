import json
import os

import typer

app = typer.Typer(add_completion=False, help="OpenEncroachment Agent CLI")


@app.command("run")
def run(
    prompt: str = typer.Argument(..., help="User prompt for the agent"),
    model: str = typer.Option(
        os.environ.get("OPENAI_AGENT_MODEL", "gpt-4o-mini"), "--model", "-m", help="OpenAI model"
    ),
    system: str = typer.Option(
        "You are the OpenEncroachment operator assistant.", "--system", help="System prompt"
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output"),
) -> None:
    try:
        # Lazy import to allow --help without optional dependencies
        from .agent import run_agent  # type: ignore

        result = run_agent(prompt=prompt, model=model, system=system)
    except Exception as e:
        typer.echo(f"Agent error: {e}", err=True)
        raise typer.Exit(code=1) from e

    if json_output:
        typer.echo(json.dumps(result, indent=2))
    else:
        if result.get("ok"):
            typer.echo(result.get("output", ""))
        else:
            typer.echo(f"Agent failed: {result}", err=True)
            raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
