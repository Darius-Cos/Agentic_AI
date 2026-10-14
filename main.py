"""CLI entry point for the Autonomous Research Agent."""

import argparse
import asyncio

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from agent import ResearchAgentRunner
from rag.indexer import build_index
from utils.config import FAISS_INDEX_PATH, MAX_ITERATIONS

console = Console()


async def run_query(query: str, max_iterations: int) -> None:
    runner = ResearchAgentRunner()
    with console.status("[bold green]Researching...[/bold green]", spinner="dots"):
        answer = await runner.run(query, max_iterations=max_iterations)
    console.print(Panel(Markdown(answer), title="Research Answer", border_style="blue"))


def build_corpus_index() -> None:
    console.print("[yellow]Building FAISS index from corpus...[/yellow]")
    build_index()
    console.print(f"[green]Index built and saved to {FAISS_INDEX_PATH}/[/green]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous Research Agent")
    parser.add_argument("query", nargs="*", help="Research question")
    parser.add_argument("--build-index", action="store_true", help="Build FAISS index from corpus")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=MAX_ITERATIONS,
        metavar="N",
        help=f"Max refinement loop iterations (default: {MAX_ITERATIONS})",
    )
    args = parser.parse_args()

    if args.build_index:
        build_corpus_index()
        return

    if not args.query:
        parser.print_help()
        return

    query = " ".join(args.query)
    asyncio.run(run_query(query, max_iterations=args.max_iterations))


if __name__ == "__main__":
    main()
