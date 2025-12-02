"""
Token Consumption Logging Utility for MBRAS AI Agents

This module provides centralized token consumption logging functionality
for all AI agents in the MBRAS system. It tracks input/output tokens
and provides detailed consumption metrics for monitoring and optimization.
"""

from typing import Any

from src.infrastructure.lib.logger import guide_logger


def log_token_consumption(
    agent_name: str, response: Any, input_message_count: int = 0
) -> None:
    """
    Log token consumption for LLM calls in agents.

    This function extracts token usage information from LLM response objects
    and logs comprehensive consumption metrics including input tokens, output tokens,
    total tokens, and context information.

    Args:
        agent_name: Name of the agent making the LLM call
        response: Response object from model.ainvoke() or similar LLM calls
        input_message_count: Number of input messages for context (optional)

    Example:
        >>> response = await model.ainvoke({"messages": messages})
        >>> log_token_consumption("Broker", response, len(messages))

    Token Usage Sources:
        - response.usage_metadata (newer LangChain versions)
        - response.response_metadata.usage (OpenAI format)
        - response.response_metadata.token_usage (alternative format)
    """
    try:
        # Extract token usage information from response
        usage_data = {}

        # Try to get usage from different possible locations in response
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            # Modern LangChain format
            usage_data = {
                "input_tokens": response.usage_metadata.get("input_tokens", 0),
                "output_tokens": response.usage_metadata.get("output_tokens", 0),
                "total_tokens": response.usage_metadata.get("total_tokens", 0),
            }
        elif hasattr(response, "response_metadata") and response.response_metadata:
            # Check for usage in response_metadata (OpenAI and other providers)
            metadata = response.response_metadata

            if "usage" in metadata:
                # Standard OpenAI format
                usage = metadata["usage"]
                usage_data = {
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
            elif "token_usage" in metadata:
                # Alternative token usage format
                usage = metadata["token_usage"]
                usage_data = {
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }

        # If we found usage data, log it with comprehensive information
        if usage_data and usage_data.get("total_tokens", 0) > 0:
            guide_logger.info(
                f"🤖 TOKEN CONSUMPTION | Agent: {agent_name} | "
                f"Input: {usage_data['input_tokens']} tokens | "
                f"Output: {usage_data['output_tokens']} tokens | "
                f"Total: {usage_data['total_tokens']} tokens | "
                f"Input Messages: {input_message_count}"
            )
        else:
            # Log that we couldn't extract token info for debugging
            guide_logger.debug(
                f"🤖 TOKEN CONSUMPTION | Agent: {agent_name} | "
                f"Unable to extract token usage (response type: {type(response).__name__}) | "
                f"Input Messages: {input_message_count}"
            )

    except Exception as e:
        # Log any errors that occur during token logging without disrupting agent flow
        guide_logger.error(f"Failed to log token consumption for {agent_name}: {e}")


def log_token_consumption_with_model_info(
    agent_name: str, response: Any, input_message_count: int = 0, model_name: str = None
) -> None:
    """
    Enhanced token consumption logging with model information.

    Args:
        agent_name: Name of the agent making the LLM call
        response: Response object from model.ainvoke()
        input_message_count: Number of input messages for context
        model_name: Name of the model used (if available)
    """
    try:
        # Extract token usage information from response
        usage_data = {}

        # Try to get usage from different possible locations in response
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage_data = {
                "input_tokens": response.usage_metadata.get("input_tokens", 0),
                "output_tokens": response.usage_metadata.get("output_tokens", 0),
                "total_tokens": response.usage_metadata.get("total_tokens", 0),
            }
        elif hasattr(response, "response_metadata") and response.response_metadata:
            metadata = response.response_metadata

            # Try to extract model name from metadata if not provided
            if not model_name:
                model_name = metadata.get(
                    "model", metadata.get("model_name", "unknown")
                )

            if "usage" in metadata:
                usage = metadata["usage"]
                usage_data = {
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
            elif "token_usage" in metadata:
                usage = metadata["token_usage"]
                usage_data = {
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }

        # Enhanced logging with model information
        if usage_data and usage_data.get("total_tokens", 0) > 0:
            model_info = f"Model: {model_name} | " if model_name else ""
            guide_logger.info(
                f"🤖 TOKEN CONSUMPTION | Agent: {agent_name} | "
                f"{model_info}"
                f"Input: {usage_data['input_tokens']} tokens | "
                f"Output: {usage_data['output_tokens']} tokens | "
                f"Total: {usage_data['total_tokens']} tokens | "
                f"Input Messages: {input_message_count}"
            )
        else:
            model_info = f"Model: {model_name} | " if model_name else ""
            guide_logger.debug(
                f"🤖 TOKEN CONSUMPTION | Agent: {agent_name} | "
                f"{model_info}"
                f"Unable to extract token usage (response type: {type(response).__name__}) | "
                f"Input Messages: {input_message_count}"
            )

    except Exception as e:
        guide_logger.error(
            f"Failed to log enhanced token consumption for {agent_name}: {e}"
        )


def calculate_token_cost(
    input_tokens: int,
    output_tokens: int,
    input_cost_per_1k: float = 0.0,
    output_cost_per_1k: float = 0.0,
) -> dict:
    """
    Calculate estimated cost for token usage.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        input_cost_per_1k: Cost per 1000 input tokens in USD
        output_cost_per_1k: Cost per 1000 output tokens in USD

    Returns:
        Dict with cost breakdown and total cost
    """
    input_cost = (input_tokens / 1000) * input_cost_per_1k
    output_cost = (output_tokens / 1000) * output_cost_per_1k
    total_cost = input_cost + output_cost

    return {
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6),
        "currency": "USD",
    }


def log_token_consumption_with_cost(
    agent_name: str,
    response: Any,
    input_message_count: int = 0,
    input_cost_per_1k: float = 0.0,
    output_cost_per_1k: float = 0.0,
) -> None:
    """
    Log token consumption with estimated cost calculation.

    Args:
        agent_name: Name of the agent making the LLM call
        response: Response object from model.ainvoke()
        input_message_count: Number of input messages for context
        input_cost_per_1k: Cost per 1000 input tokens in USD
        output_cost_per_1k: Cost per 1000 output tokens in USD
    """
    try:
        usage_data = {}

        # Extract token usage
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage_data = {
                "input_tokens": response.usage_metadata.get("input_tokens", 0),
                "output_tokens": response.usage_metadata.get("output_tokens", 0),
                "total_tokens": response.usage_metadata.get("total_tokens", 0),
            }
        elif hasattr(response, "response_metadata") and response.response_metadata:
            metadata = response.response_metadata
            if "usage" in metadata:
                usage = metadata["usage"]
                usage_data = {
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }

        if usage_data and usage_data.get("total_tokens", 0) > 0:
            # Calculate cost if pricing is provided
            cost_info = ""
            if input_cost_per_1k > 0 or output_cost_per_1k > 0:
                cost_data = calculate_token_cost(
                    usage_data["input_tokens"],
                    usage_data["output_tokens"],
                    input_cost_per_1k,
                    output_cost_per_1k,
                )
                cost_info = f"Cost: ${cost_data['total_cost']:.6f} USD | "

            guide_logger.info(
                f"🤖 TOKEN CONSUMPTION | Agent: {agent_name} | "
                f"Input: {usage_data['input_tokens']} tokens | "
                f"Output: {usage_data['output_tokens']} tokens | "
                f"Total: {usage_data['total_tokens']} tokens | "
                f"{cost_info}"
                f"Input Messages: {input_message_count}"
            )

    except Exception as e:
        guide_logger.error(
            f"Failed to log token consumption with cost for {agent_name}: {e}"
        )
