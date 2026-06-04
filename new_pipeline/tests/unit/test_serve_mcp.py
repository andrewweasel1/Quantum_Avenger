import json

from new_pipeline.scripts import serve_mcp


def test_serve_mcp_prints_tool_schemas(capsys):
    serve_mcp.main()
    payload = json.loads(capsys.readouterr().out)
    assert "tools" in payload
    assert len(payload["tools"]) >= 8
    assert all("inputSchema" in tool for tool in payload["tools"])
