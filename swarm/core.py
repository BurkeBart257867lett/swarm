"""Core Swarm client and agent orchestration logic."""

from __future__ import annotations

import copy
import json
from typing import Any, Callable, Optional, Union

from openai import OpenAI
from openai.types.chat import ChatCompletionMessage

from .types import Agent, AgentFunction, ChatCompletionMessageToolCall, Response, Result
from .util import function_to_json, debug_print

# Default model used when none is specified on the agent
DEFAULT_MODEL = "gpt-4o-mini"  # switched to mini for lower cost during personal experiments

# Maximum number of turns before we force-stop the loop
# Reduced from 100 to 25 to avoid runaway loops eating API credits
MAX_TURNS = 25


class Swarm:
    """Main Swarm client that manages agent execution and tool calls."""

    def __init__(self, client: Optional[OpenAI] = None):
        """Initialize the Swarm client.

        Args:
            client: An optional pre-configured OpenAI client. If not provided,
                    a default client will be instantiated from environment variables.
        """
        self.client = client or OpenAI()

    def get_chat_completion(
        self,
        agent: Agent,
        history: list[dict],
        context_variables: dict,
        model_override: Optional[str],
        stream: bool,
        debug: bool,
    ) -> ChatCompletionMessage:
        """Build and send a chat completion request for the given agent."""
        context_variables = copy.deepcopy(context_variables)

        # Render the system prompt, injecting context variables if callable
        instructions = (
            agent.instructions(context_variables)
            if callable(agent.instructions)
            else agent.instructions
        )

        messages = [{"role": "system", "content": instructions}] + history
        debug_print(debug, "Getting chat completion for:", messages)

        tools = [function_to_json(f) for f in agent.functions]

        # Inject context_variables parameter into tool schemas when needed
        for tool in tools:
            params = tool["function"]["parameters"]["properties"]
            if "context_variables" in params:
                del params["context_variables"]
                required = tool["function"]["parameters"].get("required", [])
                if "context_variables" in required:
                    required.remove("context_variables")

        create_params: dict[str, Any] = {
            "model": model_override or agent.model or DEFAULT_MODEL,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            create_params["tools"] = tools
            create_params["tool_choice"] = agent.tool_choice

        return self.client.chat.completions.create(**create_params)

    def handle_tool_calls(
        self,
        tool_calls: list[ChatCompletionMessageToolCall],
        functions: list[AgentFunction],
        context_variables: dict,
        debug: bool,
    ) -> Response:
        """Execute tool calls returned by the model and collect results."""
        function_map = {f.__n