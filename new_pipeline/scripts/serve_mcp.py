"""Offline stand-in entrypoint for the MCP tool server (Phase 7 container image).

Prints the deterministic quant-tool registry as JSON-RPC tool schemas. The live
FastMCP stdio server is wired here at the live cutover; until then this is a
runnable inventory entrypoint for the MCP image.
"""

import json

from new_pipeline.execution.mcp_tools import build_default_registry


def main() -> None:
    registry = build_default_registry()
    print(json.dumps({"tools": registry.schemas()}, indent=2))


if __name__ == "__main__":
    main()
