"""Swarm - A multi-agent orchestration framework.

This package provides the core functionality for creating and managing
swarms of AI agents that can collaborate to solve complex tasks.
"""

__version__ = "0.1.0"
__author__ = "swarm contributors"

from swarm.core import Swarm
from swarm.agent import Agent
from swarm.types import AgentFunction, Result, Response

__all__ = [
    "Swarm",
    "Agent",
    "AgentFunction",
    "Result",
    "Response",
]
