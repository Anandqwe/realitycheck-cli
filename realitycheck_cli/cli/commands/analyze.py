from __future__ import annotations

from pathlib import Path

import typer
from google.api_core.exceptions import GoogleAPICallError

from realitycheck_cli.config.settings import Settings
from realitycheck_cli.output.json_writer import write_json_output
from realitycheck_cli.output.rich_renderer import render_analysis
from realitycheck_cli.pipeline import analyze_contract_file


def analyze_contract_command(
    pdf_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to a contract PDF file.",
    ),
    json_output: Path | None = typer.Option(
        None,
        "--json-output",
        "-j",
        help="Path to write structured JSON output.",
    ),
    use_llm: bool = typer.Option(
        False,
        "--use-llm/--no-llm",
        help="Enable LLM-assisted classification.",
    ),
) -> None:
    settings = Settings.from_env()
    if use_llm and not settings.gemini_api_key:
        raise typer.BadParameter(
            "GEMINI_API_KEY must be set when --use-llm is enabled."
        )
    if use_llm:
        typer.echo(
            f"LLM mode enabled ({settings.gemini_model}); "
            f"timeout {settings.llm_timeout_seconds}s per clause."
        )

    try:
        result = analyze_contract_file(
            pdf_path=pdf_path,
            settings=settings,
            use_llm=use_llm,
        )
    except GoogleAPICallError as exc:
        raise typer.BadParameter(f"LLM request failed: {exc}") from exc
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    output_path = json_output or Path("artifacts") / f"{pdf_path.stem}.analysis.json"
    output_path = write_json_output(result, output_path)
    render_analysis(result, output_path)

