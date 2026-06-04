from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class ModelMetadata(BaseModel):
    model_name: str
    version: str
    created_at: datetime
    feature_set: list[str]
    path: Path

    class Config:
        arbitrary_types_allowed = True
