from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    environment: str = "development"
    greeting_prefix: str = "Hello"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


def load_config() -> AppConfig:
    return AppConfig(
        environment=os.environ.get("APP_ENV", AppConfig.environment),
        greeting_prefix=os.environ.get("GREETING_PREFIX", AppConfig.greeting_prefix),
    )
