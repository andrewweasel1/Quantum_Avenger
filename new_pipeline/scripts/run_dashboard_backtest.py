"""Run the dashboard's S&P 500 backtest page headlessly (streamlit AppTest).

Drives ``monitoring/dashboard/pages/07_backtest.py`` exactly as a user would —
set the date range, flip the family toggles, submit the form — and prints the
resulting KPIs + snapshot path. Useful on hosts without a browser and in CI.

  PYTHONPATH=. python -m new_pipeline.scripts.run_dashboard_backtest \
      --start 2024-07-15 --end 2026-07-10

Requires the dashboard extra (``pip install -r requirements-dashboard.txt``).
"""

import argparse
from datetime import date, timedelta
from pathlib import Path

PAGE = (
    Path(__file__).resolve().parents[1]
    / "monitoring" / "dashboard" / "pages" / "07_backtest.py"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Headless dashboard S&P 500 backtest")
    parser.add_argument("--start", type=date.fromisoformat, default=date.today() - timedelta(days=730))
    parser.add_argument("--end", type=date.fromisoformat, default=date.today() - timedelta(days=3))
    parser.add_argument("--max-symbols", type=int, default=0, help="0 = full S&P 500")
    parser.add_argument("--no-news", action="store_true")
    parser.add_argument("--no-expanded", action="store_true")
    parser.add_argument("--no-fundamentals", action="store_true")
    parser.add_argument("--no-snapshot", action="store_true")
    parser.add_argument("--timeout", type=float, default=3600.0)
    args = parser.parse_args()

    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(PAGE), default_timeout=args.timeout)
    at.run()
    at.date_input[0].set_value(args.start)
    at.date_input[1].set_value(args.end)
    at.toggle[0].set_value(not args.no_news)
    at.toggle[1].set_value(not args.no_expanded)
    at.toggle[2].set_value(not args.no_fundamentals)
    at.toggle[3].set_value(not args.no_snapshot)
    at.number_input[0].set_value(args.max_symbols)
    at.button[0].click()
    at.run()

    if at.exception:
        for exc in at.exception:
            print("PAGE EXCEPTION:", exc.value)
        raise SystemExit(1)
    report = at.session_state["sp500_report"]
    print("metrics rendered:", [(metric.label, metric.value) for metric in at.metric])
    print("kpis:", report.kpis())
    for note in report.degradations:
        print("degradation:", note)
    if report.snapshot_path:
        print("snapshot:", report.snapshot_path)


if __name__ == "__main__":
    main()
