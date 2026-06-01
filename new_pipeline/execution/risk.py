from dataclasses import dataclass


@dataclass
class RiskManager:
    max_risk_per_trade: float
    atr_multiplier: float

    def compute_position_size(self, account_balance: float, entry_price: float, atr: float) -> float:
        if atr <= 0 or entry_price <= 0:
            return 0.0

        stop = entry_price - (self.atr_multiplier * atr)
        risk_per_share = entry_price - stop
        if risk_per_share <= 0:
            return 0.0

        capital_at_risk = account_balance * self.max_risk_per_trade
        position_size = capital_at_risk / risk_per_share
        return max(0.0, position_size)
