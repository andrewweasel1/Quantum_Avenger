from new_pipeline.monitoring.dashboard.alerts import Alert
from new_pipeline.monitoring.dashboard.notifications import (
    ConsoleChannel,
    RecordingChannel,
    WebhookChannel,
    dispatch,
)


def test_dispatch_to_multiple_channels():
    alerts = [Alert("critical", "drawdown"), Alert("warning", "veto rate")]
    recorder = RecordingChannel()
    posted = []
    webhook = WebhookChannel("http://hook", lambda url, payload: posted.append((url, payload)))

    deliveries = dispatch(alerts, [recorder, webhook])

    assert deliveries == 4  # 2 alerts x 2 channels
    assert len(recorder.sent) == 2
    assert posted[0] == ("http://hook", {"severity": "critical", "message": "drawdown"})


def test_console_channel_uses_sink():
    lines = []
    ConsoleChannel(sink=lines.append).send(Alert("warning", "hi"))
    assert lines == ["[WARNING] hi"]
