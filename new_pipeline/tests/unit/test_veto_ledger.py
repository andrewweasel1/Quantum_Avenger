from new_pipeline.execution.veto_ledger import LEDGER_SCHEMA, VetoLedger, VetoRecord


def _record(reason="executed", gate="none", size=10, exec_id="x1"):
    return VetoRecord("AAPL", "BUY", 100.0, reason, gate, 0.96, size, exec_id)


def test_append_and_read(tmp_path):
    ledger = VetoLedger(tmp_path / "veto.parquet")
    ledger.append(_record())
    table = ledger.read()
    assert table.num_rows == 1
    assert table.schema.names == LEDGER_SCHEMA.names
    assert table.column("symbol").to_pylist() == ["AAPL"]


def test_append_only_accumulates(tmp_path):
    ledger = VetoLedger(tmp_path / "veto.parquet")
    ledger.append(_record(exec_id="a"))
    ledger.append(_record(reason="risk veto", gate="shield", size=0, exec_id=""))
    assert len(ledger) == 2
    assert ledger.read().column("veto_gate").to_pylist() == ["none", "shield"]


def test_read_empty_ledger(tmp_path):
    assert VetoLedger(tmp_path / "missing.parquet").read().num_rows == 0
