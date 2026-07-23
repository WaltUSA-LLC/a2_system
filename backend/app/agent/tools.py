import json

import pandas as pd
from langchain_core.tools import tool

from app.services.shift_view import handle_shift_mach_detail, \
    handle_shift_view

from app.services.sku_view import handle_sku_mach_detail,\
    handle_sku_view


@tool(
    "shift_summary",
    parse_docstring=True,
    description=(
        "Get overall production shift summary information only. "
        "Use this for questions about total MES_prs, NAU_prs, discard, efficiency, "
        "machine count, defects, or PQC counts for a shift or date range."
    ),
)
def get_shift_summary(start_time: str, end_time: str, shift: int) -> str:
    """Get shift summary as JSON.

    Args:
        start_time: Start date for the shift summary range, for example "2026-07-06".
        end_time: End date for the shift summary range, for example "2026-07-06".
        shift: Shift number. Use 0 to show day and night shifts separately,
            1 to show the day shift, or 2 to show the night shift.
    """
    print("Agent is using shift summary tool.")
    shift_summary = handle_shift_view(start_time, end_time, shift)
    return json.dumps(
        {"shift_summary": shift_summary.to_dict(orient="records")},
        default=str,
    )


@tool(
    "shift_machine_details",
    parse_docstring=True,
    description=(
        "Get machine-level production details for a shift. "
        "Use this only when the user asks about individual machines, lines, "
        "machine efficiency, style codes, or machine-level output."
    ),
)
def get_shift_machine_details(start_time: str, shift: int) -> str:
    """Get machine-level shift detail as JSON.

    Args:
        start_time: Start date for the machine detail, for example "2026-07-06".
        shift: Shift number. Use 0 to show day and night shifts separately,
            1 to show the day shift, or 2 to show the night shift.
    """
    print("Agent is using shift machine details tool")
    if shift == 0:
        machine_details = pd.concat(
            [
                handle_shift_mach_detail(start_time, 1),
                handle_shift_mach_detail(start_time, 2),
            ],
            ignore_index=True,
        )
    else:
        machine_details = handle_shift_mach_detail(start_time, shift)

    return json.dumps(
        {"machine_details": machine_details.to_dict(orient="records")},
        default=str,
    )



@tool(
    "style_summary",
    parse_docstring=True,
    description=(
        "Retrieve production metrics by style and shift for a specified date range. "
        "Use this tool to answer questions about a style's total MES_prs, NAU_prs, "
        "discard, efficiency, machine count, defects, or PQC count, with results "
        "broken down by shift."
    ),
)
def get_style_summary(start_time: str, end_time: str, shift: int) -> str:
    """Return style-level production metrics grouped by shift as JSON.

    Args:
        start_time: First date in the reporting range, formatted as YYYY-MM-DD.
        end_time: Last date in the reporting range, formatted as YYYY-MM-DD.
        shift: Shift filter. Use 0 for separate day- and night-shift results,
            1 for the day shift only, or 2 for the night shift only.

    Returns:
        A JSON string containing style summary records under the
        ``style_summary`` key.
    """
    print("Agent is using style summary tool.")
    style_summary = handle_sku_view(start_time, end_time, shift)
    return json.dumps(
        {"style_summary": style_summary.to_dict(orient="records")},
        default=str,
    )
