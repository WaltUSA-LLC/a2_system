from __future__ import annotations

from pathlib import Path
from datetime import datetime

import pandas as pd

from nautilus_mes_base.utils import (
    format_header_bold,
    format_header_fill,
    auto_fit_columns,
    apply_table_borders,
)


class ExcelWriter:
    def __init__(self, output_dir: Path, sheet_name: str, file_name: str) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sheet_name = sheet_name
        self.file_name = file_name

    def to_excel(self, df: pd.DataFrame, start_dt: datetime, end_dt: datetime) -> str:
        output_name = f"{self.file_name}_{start_dt.date().isoformat()}_{end_dt.date().isoformat()}.xlsx"
        output_path = self.output_dir / output_name

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=self.sheet_name, index=False)
            ws = writer.sheets[self.sheet_name]
            ws.freeze_panes = "A2"

            format_header_bold(ws, "13")
            format_header_fill(ws, "FFA500")
            auto_fit_columns(ws)
            apply_table_borders(ws)

        return str(output_path)
