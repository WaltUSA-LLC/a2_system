from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    database_url: str
    weights_path: Path
    output_dir: Path

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv()

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL is missing. Set it in .env")

        return cls(
            database_url=database_url,
            weights_path=Path(os.getenv("WEIGHTS_PATH", "./nautilus_mes_base/data/weights.json")),
            output_dir=Path(os.getenv("BASE_OUTPUT", "./base_outputs")),
        )
