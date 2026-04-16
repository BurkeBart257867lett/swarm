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
DEFAULT_MODEL = "gpt-4o"

# Maximum number of turns before we force-stop the loop
MAX_TURNS = 100


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
        function_map = {f.__name__: f for f in functions}
        partial_response = Response(messages=[], agent=None, context_variables={})

        for tool_call in tool_calls:
            name = tool_call.function.name
            if name not in function_map:
                debug_print(debug, f"Tool {name} not found in function map.")
                partial_response.messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": f"Error: tool '{name}' not found."}
                )
                continue

            args = json.loads(tool_call.function.arguments)
            debug_print(debug, f"Processing tool call: {name} with args", args)

            func = function_map[name]
            # Inject context_variables if the function expects them
            import inspect
            if "context_variables" in inspect.signature(func).parameters:
                args["context_variables"] = context_variables

            raw_result = func(**args)
            result: Result = self._handle_function_result(raw_result, debug)

            partial_response.messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": result.value}
            )
            context_variables.update(result.context_variables)
            if result.agent:
                partial_response.agent = result.agent

        partial_response.context_variables = context_variables
        return partial_response

    def _handle_function_result(self, result: Any, debug: bool) -> Result:
        """Normalize a function return value into a Result object."""
        if isinstance(result, Result):
            return result
        if isinstance(result, Agent):
            return Result(value=json.dumps({"assistant": result.name}), agent=result)
        try:
            return Result(value=str(result))
        except Exception as e:
            error_msg = f"Failed to cast response to string: {e}"
            debug_print(debug, error_msg)
            raise TypeError(error_msg) from e

    def run(
        self,
        agent: Agent,
        messages: list[dict],
        context_variables: Optional[dict] = None,
        model_override: Optional[str] = None,
        stream: bool = False,
        debug: bool = False,
        max_turns: int = MAX_TURNS,
        execute_tools: bool = True,
    ) -> Response:
        """Run the agent loop until completion or max_turns is reached."""
        context_variables = context_variables or {}
        history = copy.deepcopy(messages)
        init_len = len(messages)
        active_agent = agent

        while len(history) - init_len < max_turns:
            completion = self.get_chat_completion(
                agent=active_agent,
                history=history,
                context_variables=context_variables,
                model_override=model_override,
                stream=stream,
                debug=debug,
            )

            message = completion.choices[0].message
            debug_print(debug, "Received completion:", message)
            message_dict = json.loads(message.model_dump_json())
            message_dict["sender"] = active_agent.name
            history.append(message_dict)

            if not message.tool_calls or not execute_tools:
                debug_print(debug, "Ending turn — no tool calls or execute_tools=False.")
                break

            partial_response = self.handle_tool_calls(
                message.tool_calls, active_agent.functions, context_variables, debug
            )
            history.extend(partial_response.messages)
            context_variables.update(partial_response.context_variables)
            if partial_response.agent:
                active_agent = partial_response.agent

        return Response(
            messages=history[init_len:],
            agent=active_agent,
            context_variables=context_variables,
        )
