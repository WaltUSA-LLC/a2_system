from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    database_url: str
    weights_path: Path
    output_dir: Path
    log_data_output: bool

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv()

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL is missing. Set it in .env")

        log_data_output = os.getenv("LOG_DATA_OUTPUT", "false").strip().lower() == "true"

        return cls(
            database_url=database_url,
            weights_path=Path(os.getenv("WEIGHTS_PATH", "./extractors/data/weights.json")),
            output_dir=Path(os.getenv("DATA_OUTPUT", "./extractors/data_outputs")),
            log_data_output=log_data_output,
        )
