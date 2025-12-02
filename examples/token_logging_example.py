#!/usr/bin/env python3
"""
Token Consumption Logging Example for MBRAS AI System

This script demonstrates how to use the token consumption logging utilities
with various agents and scenarios. It shows basic usage, enhanced logging,
and cost-aware logging patterns.

Run this script to see example outputs and understand how to integrate
token logging into your AI agents.
"""

import asyncio
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.infrastructure.ai.utils import (
    calculate_token_cost,
    log_token_consumption,
    log_token_consumption_with_cost,
    log_token_consumption_with_model_info,
)


def create_mock_response(
    input_tokens: int = 1247,
    output_tokens: int = 342,
    response_format: str = "usage_metadata",
) -> MagicMock:
    """Create a mock LLM response with token usage information."""
    response = MagicMock()

    if response_format == "usage_metadata":
        # Modern LangChain format
        response.usage_metadata = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }
        response.response_metadata = None
    elif response_format == "openai":
        # OpenAI format
        response.usage_metadata = None
        response.response_metadata = {
            "usage": {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
            "model": "gpt-4o",
        }
    elif response_format == "alternative":
        # Alternative format
        response.usage_metadata = None
        response.response_metadata = {
            "token_usage": {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            }
        }
    else:  # no_usage
        # Response with no usage data
        response.usage_metadata = None
        response.response_metadata = {}

    # Add common response attributes
    response.content = f"This is a mock response with {output_tokens} output tokens."
    response.tool_calls = []

    return response


def demonstrate_basic_logging():
    """Demonstrate basic token consumption logging."""
    print("\n" + "=" * 60)
    print("BASIC TOKEN CONSUMPTION LOGGING")
    print("=" * 60)

    # Example 1: Standard usage metadata format
    print("\n1. Standard Usage Metadata Format:")
    response1 = create_mock_response(1247, 342, "usage_metadata")
    log_token_consumption("Broker", response1, 5)

    # Example 2: OpenAI format
    print("\n2. OpenAI Response Format:")
    response2 = create_mock_response(892, 156, "openai")
    log_token_consumption("Market_Analyst", response2, 3)

    # Example 3: Alternative format
    print("\n3. Alternative Token Usage Format:")
    response3 = create_mock_response(654, 223, "alternative")
    log_token_consumption("Concierge_Agent", response3, 4)

    # Example 4: No usage data (debug logging)
    print("\n4. Response Without Usage Data (Debug Mode):")
    response4 = create_mock_response(0, 0, "no_usage")
    log_token_consumption("lead_seeker", response4, 2)


def demonstrate_enhanced_logging():
    """Demonstrate enhanced token logging with model information."""
    print("\n" + "=" * 60)
    print("ENHANCED TOKEN LOGGING WITH MODEL INFO")
    print("=" * 60)

    # Example 1: With explicit model name
    print("\n1. With Explicit Model Name:")
    response1 = create_mock_response(1456, 298, "usage_metadata")
    log_token_consumption_with_model_info(
        "Broker_PropertySearch", response1, 7, model_name="gpt-4o-mini"
    )

    # Example 2: Auto-extract model name from response
    print("\n2. Auto-Extract Model from Response:")
    response2 = create_mock_response(723, 189, "openai")
    log_token_consumption_with_model_info("Market_Analyst_Valuation", response2, 4)

    # Example 3: Large conversation context
    print("\n3. Large Conversation Context:")
    response3 = create_mock_response(2341, 567, "usage_metadata")
    log_token_consumption_with_model_info(
        "Concierge_Portfolio_Delivery", response3, 15, model_name="gpt-4-turbo"
    )


def demonstrate_cost_aware_logging():
    """Demonstrate cost-aware token consumption logging."""
    print("\n" + "=" * 60)
    print("COST-AWARE TOKEN CONSUMPTION LOGGING")
    print("=" * 60)

    # GPT-4 pricing example
    gpt4_input_cost = 0.005  # $0.005 per 1K input tokens
    gpt4_output_cost = 0.015  # $0.015 per 1K output tokens

    print("\n1. GPT-4 Cost Analysis:")
    response1 = create_mock_response(1847, 423, "openai")
    log_token_consumption_with_cost(
        "Broker_ComplexQuery",
        response1,
        8,
        input_cost_per_1k=gpt4_input_cost,
        output_cost_per_1k=gpt4_output_cost,
    )

    # GPT-3.5 pricing example
    gpt35_input_cost = 0.0005  # $0.0005 per 1K input tokens
    gpt35_output_cost = 0.0015  # $0.0015 per 1K output tokens

    print("\n2. GPT-3.5 Cost Analysis:")
    response2 = create_mock_response(956, 234, "usage_metadata")
    log_token_consumption_with_cost(
        "suggestion_agent",
        response2,
        12,
        input_cost_per_1k=gpt35_input_cost,
        output_cost_per_1k=gpt35_output_cost,
    )

    # High-volume scenario
    print("\n3. High-Volume Processing:")
    response3 = create_mock_response(4567, 1234, "alternative")
    log_token_consumption_with_cost(
        "memory_insertion_extractor",
        response3,
        25,
        input_cost_per_1k=gpt4_input_cost,
        output_cost_per_1k=gpt4_output_cost,
    )


def demonstrate_cost_calculation():
    """Demonstrate standalone cost calculation utility."""
    print("\n" + "=" * 60)
    print("STANDALONE COST CALCULATION")
    print("=" * 60)

    scenarios = [
        {
            "name": "Small Query",
            "input_tokens": 456,
            "output_tokens": 123,
            "input_cost": 0.005,
            "output_cost": 0.015,
        },
        {
            "name": "Medium Analysis",
            "input_tokens": 1847,
            "output_tokens": 678,
            "input_cost": 0.005,
            "output_cost": 0.015,
        },
        {
            "name": "Large Processing",
            "input_tokens": 8934,
            "output_tokens": 2456,
            "input_cost": 0.005,
            "output_cost": 0.015,
        },
    ]

    total_cost = 0

    for scenario in scenarios:
        cost_data = calculate_token_cost(
            scenario["input_tokens"],
            scenario["output_tokens"],
            scenario["input_cost"],
            scenario["output_cost"],
        )

        print(f"\n{scenario['name']}:")
        print(f"  Input Tokens: {scenario['input_tokens']:,}")
        print(f"  Output Tokens: {scenario['output_tokens']:,}")
        print(
            f"  Total Tokens: {scenario['input_tokens'] + scenario['output_tokens']:,}"
        )
        print(f"  Input Cost: ${cost_data['input_cost']:.6f}")
        print(f"  Output Cost: ${cost_data['output_cost']:.6f}")
        print(f"  Total Cost: ${cost_data['total_cost']:.6f} {cost_data['currency']}")

        total_cost += cost_data["total_cost"]

    print(f"\nCombined Total Cost: ${total_cost:.6f} USD")


def demonstrate_agent_scenarios():
    """Demonstrate realistic agent interaction scenarios."""
    print("\n" + "=" * 70)
    print("REALISTIC AGENT INTERACTION SCENARIOS")
    print("=" * 70)

    print("\n📋 Scenario 1: Property Search Flow")
    print("-" * 40)

    # User asks for properties
    broker_response = create_mock_response(892, 145, "openai")
    log_token_consumption("Broker", broker_response, 2)

    # Broker transfers to Market Analyst for detailed analysis
    analyst_response = create_mock_response(1456, 567, "usage_metadata")
    log_token_consumption("Market_Analyst", analyst_response, 4)

    # Concierge handles portfolio delivery
    concierge_response = create_mock_response(634, 189, "alternative")
    log_token_consumption("Concierge_Agent", concierge_response, 6)

    print("\n🏠 Scenario 2: Property Listing Process")
    print("-" * 40)

    # Lead seeker collects property info
    lead_response = create_mock_response(723, 234, "usage_metadata")
    log_token_consumption("lead_seeker", lead_response, 5)

    # Memory processing for user data
    memory_response = create_mock_response(445, 67, "openai")
    log_token_consumption("memory_insertion_extractor", memory_response, 3)

    print("\n✅ Scenario 3: System Processing")
    print("-" * 40)

    # Validation step
    validation_response = create_mock_response(567, 89, "alternative")
    log_token_consumption("validator", validation_response, 4)

    # Suggestion generation
    suggestion_response = create_mock_response(234, 123, "usage_metadata")
    log_token_consumption("suggestion_agent", suggestion_response, 8)


def demonstrate_monitoring_analysis():
    """Demonstrate how to analyze token consumption data."""
    print("\n" + "=" * 60)
    print("TOKEN CONSUMPTION MONITORING & ANALYSIS")
    print("=" * 60)

    # Simulate daily usage data
    daily_usage = {
        "Broker": {"calls": 45, "total_tokens": 67834, "avg_tokens": 1507},
        "Market_Analyst": {"calls": 23, "total_tokens": 89456, "avg_tokens": 3889},
        "Concierge_Agent": {"calls": 31, "total_tokens": 34567, "avg_tokens": 1115},
        "lead_seeker": {"calls": 12, "total_tokens": 23456, "avg_tokens": 1955},
        "validator": {"calls": 78, "total_tokens": 12345, "avg_tokens": 158},
        "suggestion_agent": {"calls": 67, "total_tokens": 8934, "avg_tokens": 133},
    }

    print("\nDaily Usage Summary:")
    print("-" * 50)

    total_calls = 0
    total_tokens = 0

    for agent, stats in daily_usage.items():
        print(
            f"{agent:20} | Calls: {stats['calls']:3} | "
            f"Tokens: {stats['total_tokens']:7,} | "
            f"Avg: {stats['avg_tokens']:4}"
        )
        total_calls += stats["calls"]
        total_tokens += stats["total_tokens"]

    print("-" * 50)
    print(
        f"{'TOTAL':20} | Calls: {total_calls:3} | "
        f"Tokens: {total_tokens:7,} | "
        f"Avg: {total_tokens // total_calls:4}"
    )

    # Cost analysis
    print("\nEstimated Daily Cost (GPT-4 pricing):")
    estimated_cost = (total_tokens / 1000) * 0.01  # Rough estimate
    print(f"  Daily: ${estimated_cost:.2f}")
    print(f"  Monthly: ${estimated_cost * 30:.2f}")
    print(f"  Yearly: ${estimated_cost * 365:.2f}")


def print_usage_tips():
    """Print usage tips and best practices."""
    print("\n" + "=" * 60)
    print("USAGE TIPS & BEST PRACTICES")
    print("=" * 60)

    tips = [
        "Always call log_token_consumption() immediately after model.ainvoke()",
        "Use descriptive agent names that match your actual agent identifiers",
        "Include input message count for better context analysis",
        "Use cost-aware logging for production environments with budget tracking",
        "Set up log aggregation to monitor daily/monthly usage trends",
        "Monitor high-consumption agents for prompt optimization opportunities",
        "Use debug logging to troubleshoot token extraction issues",
        "Consider using enhanced logging with model info for detailed analysis",
    ]

    for i, tip in enumerate(tips, 1):
        print(f"\n{i:2}. {tip}")

    print("\n📊 Log Analysis Commands:")
    print("  # Count calls by agent:")
    print(
        "  grep 'TOKEN CONSUMPTION' logs/app_*.log | grep -o 'Agent: [^|]*' | sort | uniq -c"
    )
    print("  ")
    print("  # Sum total tokens:")
    print(
        "  grep 'TOKEN CONSUMPTION' logs/app_*.log | grep -o 'Total: [0-9]*' | awk '{sum += $2} END {print sum}'"
    )
    print("  ")
    print("  # Daily cost (when using cost logging):")
    print(
        "  grep 'Cost:' logs/app_*.log | grep -o 'Cost: $[0-9.]*' | awk -F'$' '{sum += $2} END {print \"$\" sum}'"
    )


async def main():
    """Run all demonstration examples."""
    print("🤖 MBRAS Token Consumption Logging Examples")
    print("=" * 60)
    print("This script demonstrates various token logging patterns and utilities.")

    # Run all demonstrations
    demonstrate_basic_logging()
    demonstrate_enhanced_logging()
    demonstrate_cost_aware_logging()
    demonstrate_cost_calculation()
    demonstrate_agent_scenarios()
    demonstrate_monitoring_analysis()
    print_usage_tips()

    print("\n✅ All examples completed successfully!")
    print("Check the console output above to see token consumption logging in action.")
    print("Integrate these patterns into your agents for comprehensive token tracking.")


if __name__ == "__main__":
    asyncio.run(main())
