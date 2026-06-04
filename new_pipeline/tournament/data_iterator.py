"""Zero-copy out-of-core feeding of Parquet row-groups to XGBoost.

Streams one Parquet row-group at a time into an ``xgb.QuantileDMatrix`` /
``xgb.ExtMemQuantileDMatrix`` so training never materializes the whole vault in
memory — the basis for the GPU out-of-core path (``cache_host_ratio``). Columns
are converted Arrow -> NumPy directly (no pandas materialization).
"""

import numpy as np
import pyarrow.parquet as pq
import xgboost as xgb


class ParquetDataIter(xgb.DataIter):
    def __init__(self, path, feature_columns, label_column):
        self._parquet = pq.ParquetFile(str(path))
        self._features = list(feature_columns)
        self._label = label_column
        self._row_group = 0
        super().__init__()

    def reset(self) -> None:
        self._row_group = 0

    def next(self, input_data) -> int:
        if self._row_group >= self._parquet.num_row_groups:
            return 0
        table = self._parquet.read_row_group(
            self._row_group, columns=[*self._features, self._label]
        )
        features = np.column_stack(
            [table.column(name).to_numpy(zero_copy_only=False) for name in self._features]
        ).astype(np.float64, copy=False)
        labels = table.column(self._label).to_numpy(zero_copy_only=False).astype(
            np.float64, copy=False
        )
        input_data(data=features, label=labels)
        self._row_group += 1
        return 1
