import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    data_dir: Path = Path("data")
    resend_api_key: Optional[str] = None
    email_from: Optional[str] = None
    email_to: Optional[str] = None

    @classmethod
    def load(cls, config_path: str = "config.yaml") -> "Config":
        if os.path.exists(config_path):
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}
            return cls(**data)
        return cls()


def get_config() -> Config:
    config = Config.load()
    config.resend_api_key = config.resend_api_key or os.environ.get("RESEND_API_KEY")
    config.email_from = config.email_from or os.environ.get("EMAIL_FROM")
    config.email_to = config.email_to or os.environ.get("EMAIL_TO")
    return config
