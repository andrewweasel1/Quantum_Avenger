from enum import Enum


class RunMode(str, Enum):
    BACKTEST = "backtest"
    EVALUATE = "evaluate"
    LIVE = "live"


class ValidationMode(str, Enum):
    STRICT = "strict"
    WARN = "warn"
    SKIP = "skip"
