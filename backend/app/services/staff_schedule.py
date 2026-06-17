import tempfile
from pathlib import Path

from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from ingestors.staff_time_table import (
    MONTH,
    write_staff_schedule_to_db,
)


ALLOWED_EXCEL_EXTENSIONS = {".xlsx", ".xls"}


async def upload_staff_schedule(
    file: UploadFile,
    year: int,
    month: int,
) -> dict:
    """
    Service layer for uploading and importing one monthly knit schedule.

    Responsibilities:
    - validate year/month/file
    - save uploaded Excel file to a temporary file
    - call ingestor layer
    - return clean response data to API layer
    """

    if year < 2000 or year > 2100:
        raise ValueError("year must be between 2000 and 2100")

    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")

    if month not in MONTH:
        raise ValueError(f"Unsupported month: {month}")

    if not file.filename:
        raise ValueError("Uploaded file must have a filename")

    suffix = Path(file.filename).suffix.lower()

    if suffix not in ALLOWED_EXCEL_EXTENSIONS:
        raise ValueError("Only .xlsx or .xls Excel files are allowed")

    temp_file_path: Path | None = None

    try:
        # Save uploaded file to a temporary file.
        # Your ingestor expects excel_path: str | Path, so this is convenient.
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            contents = await file.read()

            if not contents:
                raise ValueError("Uploaded Excel file is empty")

            temp_file.write(contents)
            temp_file_path = Path(temp_file.name)

        # Your ingestor is synchronous and uses pandas + SQLAlchemy.
        # In FastAPI async endpoint, run it in threadpool to avoid blocking event loop.
        inserted_count = await run_in_threadpool(
            write_staff_schedule_to_db,
            year,
            month,
            temp_file_path,
        )

        return {
            "message": "Staff schedule uploaded successfully",
            "filename": file.filename,
            "year": year,
            "month": month,
            "sheet_name": MONTH[month],
            "inserted_count": inserted_count,
        }

    finally:
        # Clean temporary file
        if temp_file_path is not None and temp_file_path.exists():
            temp_file_path.unlink()