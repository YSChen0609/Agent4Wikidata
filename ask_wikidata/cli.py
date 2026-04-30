import json

import typer

from ask_wikidata import __version__
from ask_wikidata.sparql_query_graph import run_nl_query

app = typer.Typer(no_args_is_help=True, help="ASK-WIKIDATA: NL -> Wikidata SPARQL.")


@app.command()
def version() -> None:
    """Show package version."""
    typer.echo(__version__)


@app.command()
def nl_query(
    query: str = typer.Argument(..., help="Natural language question."),
    provider: str | None = typer.Option(
        None,
        "--provider",
        help="LLM provider override: openai, gemini, ollama.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        help="LLM model override (provider-specific).",
    ),
) -> None:
    """Convert NL to Wikidata SPARQL, execute it, and print results."""
    state = run_nl_query(query_nl=query, provider=provider, model=model)

    sparql = state.get("query_sparql", "") or ""
    results = state.get("query_results", {})

    if sparql:
        typer.echo("\nSPARQL:\n" + sparql)
    typer.echo("\nRESULTS:\n" + json.dumps(results, indent=2))


def main() -> None:
    app()


if __name__ == "__main__":
    main()

