from __future__ import annotations

from pathlib import Path

import typer

from realitycheck_cli.config.settings import Settings
from realitycheck_cli.output.json_writer import write_json_output
from realitycheck_cli.output.rich_renderer import render_comparison
from realitycheck_cli.pipeline import compare_contract_files


def compare_contract_command(
    baseline_pdf: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to baseline/original contract PDF.",
    ),
    revised_pdf: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to revised contract PDF.",
    ),
    json_output: Path | None = typer.Option(
        None,
        "--json-output",
        "-j",
        help="Path to write structured comparison JSON output.",
    ),
    use_llm: bool = typer.Option(
        False,
        "--use-llm/--no-llm",
        help="Enable LLM-assisted classification during comparison.",
    ),
) -> None:
    settings = Settings.from_env()
    if use_llm and not settings.gemini_api_key:
        raise typer.BadParameter(
            "GEMINI_API_KEY must be set when --use-llm is enabled."
        )

    baseline_result, revised_result, comparison = compare_contract_files(
        baseline_path=baseline_pdf,
        revised_path=revised_pdf,
        settings=settings,
        use_llm=use_llm,
    )

    output_path = (
        json_output
        or Path("artifacts")
        / f"{baseline_pdf.stem}_vs_{revised_pdf.stem}.comparison.json"
    )
    output_path = write_json_output(
        {
            "baseline": baseline_result,
            "revised": revised_result,
            "comparison": comparison,
        },
        output_path,
    )
    render_comparison(
        comparison=comparison,
        baseline_name=baseline_pdf.name,
        revised_name=revised_pdf.name,
        json_output_path=output_path,
    )

