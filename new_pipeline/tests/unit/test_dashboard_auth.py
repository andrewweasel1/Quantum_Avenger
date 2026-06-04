from new_pipeline.monitoring.dashboard.auth import verify_credentials


def test_valid_credentials():
    assert verify_credentials("admin", "secret", expected_user="admin", expected_password="secret")


def test_invalid_password():
    assert not verify_credentials(
        "admin", "wrong", expected_user="admin", expected_password="secret"
    )


def test_fail_closed_when_unconfigured():
    assert not verify_credentials("admin", "secret", expected_user="", expected_password="")


def test_reads_from_env(monkeypatch):
    monkeypatch.setenv("DASHBOARD_USER", "quant")
    monkeypatch.setenv("DASHBOARD_PASS", "shield")
    assert verify_credentials("quant", "shield")
    assert not verify_credentials("quant", "nope")
