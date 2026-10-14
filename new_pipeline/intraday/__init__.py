"""Intraday (minute-bar) trading stack: small/mid-cap, flat-by-close.

Sibling to the daily tournament — shares adapters, evaluation, and config
machinery, touches none of the frozen daily champion's surfaces. First
strategy: long-only opening range breakout (see docs in the plan/README).
"""
