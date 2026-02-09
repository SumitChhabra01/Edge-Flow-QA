"""CALL_FLOW command."""

from __future__ import annotations

from core.commands.base_command import BaseCommand


class CallFlowCommand(BaseCommand):
    """Call a flow by name with optional parameters."""

    name = "CALL_FLOW"

    def execute(self, target: str | None, data: str | None, context):
        flow_executor = context.get("flow_executor")
        if not flow_executor:
            raise ValueError("Flow executor not configured.")
        flow_name = target or data or ""
        params = _parse_params(data)
        flow_executor(flow_name, params)
        return flow_name


def _parse_params(data: str | None) -> dict:
    if not data:
        return {}
    params = {}
    parts = [item for item in data.split(";") if "=" in item]
    for part in parts:
        key, value = part.split("=", 1)
        params[key.strip()] = value.strip()
    return params
