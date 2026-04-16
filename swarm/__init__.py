"""Swarm - A multi-agent orchestration framework.

This package provides the core functionality for creating and managing
swarms of AI agents that can collaborate to solve complex tasks.

Personal fork: added AgentFunction, Result, and Response to top-level
imports for easier access without digging into submodules.

Note: Also aliased Response as SwarmResponse to avoid potential naming
conflicts when importing alongside other libraries (e.g. requests, httpx).
"""

__version__ = "0.1.0"
__author__ = "swarm contributors"

from swarm.core import Swarm
from swarm.agent import Agent
from swarm.types import AgentFunction, Result, Response

# Convenience aliases
AgentFn = AgentFunction
SwarmResponse = Response  # avoids collision with requests.Response / httpx.Response

__all__ = [
    "Swarm",
    "Agent",
    "AgentFunction",
    "AgentFn",
    "Result",
    "Response",
    "SwarmResponse",
]
