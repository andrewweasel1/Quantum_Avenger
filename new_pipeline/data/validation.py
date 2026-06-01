from pathlib import Path

import pandas as pd

from new_pipeline.config import get_config
from new_pipeline.core.exceptions import DataValidationError


class DataValidator:
    def __init__(self) -> None:
        self.config = get_config()

    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        missing = df.isna().sum().sum()
        if missing > 0 and self.config.data.validation_mode == "strict":
            raise DataValidationError("Data contains missing values")
        return missing == 0

    def validate_file(self, path: Path) -> bool:
        if not path.exists():
            raise DataValidationError(f"Data file missing: {path}")
        return True
