"""
run_breaking_pipeline.py

Runs every query in tests/breaking.py through the ASK-WIKIDATA pipeline
(NL -> SPARQL -> Wikidata execution) and writes a structured JSON report.

Usage (from the ASK_WIKIDATA project root):
    python run_breaking_pipeline.py
    python run_breaking_pipeline.py --provider gemini --model gemini-2.0-flash
    python run_breaking_pipeline.py --provider openai  --model gpt-4o-mini
    python run_breaking_pipeline.py --provider ollama  --model qwen2.5-coder:7b
    python run_breaking_pipeline.py --out results/my_run.json

Output file (default): results/breaking_results_<ISO-timestamp>.json
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Make sure the package root is importable when run directly.
sys.path.insert(0, str(Path(__file__).parent))

from ask_wikidata.sparql_query_graph import run_nl_query
from tests.breaking import BREAKING_QUERIES


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run breaking queries through the ASK-WIKIDATA pipeline."
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="LLM provider override: openai | gemini | ollama. "
             "Falls back to LLM_PROVIDER env var.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="LLM model override (provider-specific). "
             "Falls back to LLM_MODEL env var.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSON file path. "
             "Defaults to results/breaking_results_<timestamp>.json",
    )
    parser.add_argument(
        "--category",
        default=None,
        choices=["AMBIGUOUS", "CONFLICTING", "TYPO", "NON_ENGLISH"],
        help="Run only queries belonging to this category.",
    )
    return parser.parse_args()


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_single_query(
    query: str,
    provider: str | None,
    model: str | None,
) -> dict:
    """Run one NL query and return a result dict."""
    start = time.perf_counter()
    error: str | None = None
    sparql: str = ""
    results: dict = {}
    state: dict = {}

    try:
        state = dict(run_nl_query(query_nl=query, provider=provider, model=model))
        sparql = state.get("query_sparql", "") or ""
        results = state.get("query_results", {}) or {}
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"

    elapsed_ms = round((time.perf_counter() - start) * 1000)

    messages = state.get("messages", []) or []
    if messages:
        last = messages[-1]
        results = {"last_message": getattr(last, "content", str(last))}

    return {
        "sparql": sparql,
        "results": results,
        "error": error,
        "elapsed_ms": elapsed_ms,
    }


def run_pipeline(
    provider: str | None,
    model: str | None,
    category_filter: str | None,
) -> list[dict]:
    """Run all (or filtered) breaking queries and collect structured records."""
    queries = BREAKING_QUERIES
    if category_filter:
        queries = [q for q in queries if q.category == category_filter]

    total = len(queries)
    records: list[dict] = []

    print(f"\n{'='*60}")
    print(f"ASK-WIKIDATA  Breaking Query Pipeline")
    print(f"Provider : {provider or 'env default'}")
    print(f"Model    : {model or 'env default'}")
    print(f"Queries  : {total}")
    print(f"{'='*60}\n")

    for idx, bq in enumerate(queries, start=1):
        print(f"[{idx:02d}/{total}] ({bq.category}) {bq.query[:70]}")
        outcome = run_single_query(bq.query, provider, model)

        record = {
            "index": idx,
            "category": bq.category,
            "query": bq.query,
            "note": bq.note,
            **outcome,
        }
        records.append(record)

        status = "ERROR" if outcome["error"] else ("OK" if outcome["sparql"] else "NO_SPARQL")
        print(f"         → {status}  ({outcome['elapsed_ms']} ms)")
        if outcome["error"]:
            print(f"         ! {outcome['error']}")

    return records


# ── Output ────────────────────────────────────────────────────────────────────

def save_results(records: list[dict], out_path: Path, provider: str | None, model: str | None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    summary = {
        "total": len(records),
        "ok": sum(1 for r in records if not r["error"] and r["sparql"]),
        "no_sparql": sum(1 for r in records if not r["error"] and not r["sparql"]),
        "errors": sum(1 for r in records if r["error"]),
    }

    payload = {
        "meta": {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "provider": provider or "env default",
            "model": model or "env default",
            "summary": summary,
        },
        "results": records,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"  Total      : {summary['total']}")
    print(f"  OK (SPARQL): {summary['ok']}")
    print(f"  No SPARQL  : {summary['no_sparql']}")
    print(f"  Errors     : {summary['errors']}")
    print(f"{'='*60}")
    print(f"Results saved → {out_path}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    out_path = Path(args.out) if args.out else Path(f"results/breaking_results_{timestamp}.json")

    records = run_pipeline(
        provider=args.provider,
        model=args.model,
        category_filter=args.category,
    )
    save_results(records, out_path, provider=args.provider, model=args.model)


if __name__ == "__main__":
    main()
