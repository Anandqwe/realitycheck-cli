from __future__ import annotations

import typer

from realitycheck_cli.cli.commands.analyze import analyze_contract_command
from realitycheck_cli.cli.commands.compare import compare_contract_command

app = typer.Typer(
    help=(
        "RealityCheck CLI: transform legal contracts into structured risk intelligence, "
        "negotiation drafts, and comparison insights."
    ),
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

app.command("analyze")(analyze_contract_command)
app.command("compare")(compare_contract_command)

