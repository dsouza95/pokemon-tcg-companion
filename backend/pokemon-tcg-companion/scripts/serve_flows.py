#!/usr/bin/env python3
"""
Serve all Prefect flows.

Registers every flow in the FLOWS registry as a deployment under the
configured deployment name and starts serving them. Must stay running
to accept flow runs dispatched via run_deployment().
"""

from typing import cast

from prefect import serve
from prefect.deployments.runner import RunnerDeployment

from core.settings import settings
from flows import FLOWS


def serve_flows() -> None:
    deployments = [
        cast(RunnerDeployment, flow_fn.to_deployment(name=settings.prefect_deployment))
        for flow_fn in FLOWS.values()
    ]
    serve(*deployments)


if __name__ == "__main__":
    serve_flows()
