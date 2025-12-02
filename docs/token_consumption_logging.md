# Token Consumption Logging System

## Overview

The MBRAS AI system now includes comprehensive token consumption logging that tracks input/output tokens and provides detailed consumption metrics for monitoring and optimization across all AI agents and LLM interactions.

## Features

- **Automatic Token Tracking**: Logs token usage for every LLM call across all agents
- **Agent-Specific Logging**: Tracks consumption per agent (Broker, Market_Analyst, Concierge_Agent, etc.)
- **Multiple Token Sources**: Supports various LLM response formats (OpenAI, Gemini, etc.)
- **Context Information**: Includes input message count and agent context
- **Cost Calculation**: Optional cost estimation with configurable pricing
- **Centralized Utility**: Single utility handles all token logging consistently

## Implementation

### Core Components

1. **Token Logger Utility** (`src/infrastructure/ai/utils/token_logger.py`)
   - Centralized token extraction and logging functions
   - Handles multiple LLM response formats
   - Provides cost calculation capabilities

2. **Agent Integration**
   - All agent files now include token consumption logging
   - Logs after each `model.ainvoke()` call
   - Uses consistent logging format across all agents

3. **System Integration**
   - Smart system isolated agents include token logging
   - Memory processing steps include token logging
   - Validation and suggestion steps include token logging

### Usage

#### Basic Token Logging

```python
from src.infrastructure.ai.utils import log_token_consumption

# After any LLM call
response = await model.ainvoke({"messages": messages})
log_token_consumption("AgentName", response, len(messages))
```

#### Enhanced Logging with Model Info

```python
from src.infrastructure.ai.utils import log_token_consumption_with_model_info

response = await model.ainvoke({"messages": messages})
log_token_consumption_with_model_info(
    "AgentName", 
    response, 
    len(messages), 
    model_name="gpt-4o"
)
```

#### Cost-Aware Logging

```python
from src.infrastructure.ai.utils import log_token_consumption_with_cost

response = await model.ainvoke({"messages": messages})
log_token_consumption_with_cost(
    "AgentName",
    response,
    len(messages),
    input_cost_per_1k=0.005,  # $0.005 per 1K input tokens
    output_cost_per_1k=0.015  # $0.015 per 1K output tokens
)
```

## Log Output Format

### Standard Token Consumption Log

```
🤖 TOKEN CONSUMPTION | Agent: Broker | Input: 1247 tokens | Output: 342 tokens | Total: 1589 tokens | Input Messages: 5
```

### Enhanced Log with Model Info

```
🤖 TOKEN CONSUMPTION | Agent: Market_Analyst | Model: gpt-4o | Input: 892 tokens | Output: 156 tokens | Total: 1048 tokens | Input Messages: 3
```

### Cost-Aware Log

```
🤖 TOKEN CONSUMPTION | Agent: Concierge_Agent | Input: 654 tokens | Output: 223 tokens | Total: 877 tokens | Cost: $0.006595 USD | Input Messages: 4
```

## Agent Coverage

Token consumption logging is now active for:

### Main Agents
- **Broker** (`general.py`) - Property search and coordination
- **Market_Analyst** (`market_analyst.py`) - Investment analysis and data
- **Concierge_Agent** (`concierge.py`) - Client services and logistics
- **lead_seeker** (`lead_seeker.py`) - Property listing assistance

### System Components
- **Smart System Isolated Agents** (`smart_system.py`)
  - BrokerIsolated
  - MarketAnalystIsolated
  - ConciergeIsolated
  - LeadSeekerIsolated

### Processing Steps
- **Memory Processing** (`memory_processing.py`)
  - memory_patch_extractor
  - memory_insertion_extractor
- **Validation** (`validation.py`) - Response validation
- **Suggestions** (`suggestions.py`) - Question generation

## Token Source Compatibility

The logging system automatically detects and extracts token usage from various LLM response formats:

### Modern LangChain Format
```python
response.usage_metadata = {
    "input_tokens": 1247,
    "output_tokens": 342,
    "total_tokens": 1589
}
```

### OpenAI Format
```python
response.response_metadata = {
    "usage": {
        "prompt_tokens": 1247,
        "completion_tokens": 342,
        "total_tokens": 1589
    }
}
```

### Alternative Format
```python
response.response_metadata = {
    "token_usage": {
        "prompt_tokens": 1247,
        "completion_tokens": 342,
        "total_tokens": 1589
    }
}
```

## Monitoring and Analysis

### Log Levels
- **INFO**: Successful token extraction and logging
- **DEBUG**: Failed token extraction (with fallback info)
- **ERROR**: Exceptions during token logging process

### Log File Location
Token consumption logs are written to:
- Console output (with color coding)
- Daily log files: `logs/app_YYYY-MM-DD.log`

### Aggregation Examples

#### Daily Token Usage by Agent
```bash
grep "TOKEN CONSUMPTION" logs/app_2024-12-12.log | \
grep -o "Agent: [^|]*" | sort | uniq -c
```

#### Total Tokens per Day
```bash
grep "TOKEN CONSUMPTION" logs/app_2024-12-12.log | \
grep -o "Total: [0-9]* tokens" | \
awk '{sum += $2} END {print "Total tokens:", sum}'
```

#### Cost Analysis (when using cost logging)
```bash
grep "TOKEN CONSUMPTION.*Cost:" logs/app_2024-12-12.log | \
grep -o "Cost: \$[0-9.]*" | \
awk -F'$' '{sum += $2} END {print "Total cost: $" sum}'
```

## Configuration

### Environment Variables (Optional)

```env
# Enable enhanced token logging
AI_TOKEN_LOGGING=true

# Default cost per 1K tokens (if using cost logging)
AI_INPUT_COST_PER_1K=0.005
AI_OUTPUT_COST_PER_1K=0.015

# Log level for token consumption
TOKEN_LOG_LEVEL=INFO
```

## Best Practices

### For Developers

1. **Always Log After LLM Calls**
   ```python
   response = await model.ainvoke(inputs)
   log_token_consumption("AgentName", response, message_count)
   # Continue with response processing
   ```

2. **Use Descriptive Agent Names**
   ```python
   # Good
   log_token_consumption("Broker_PropertySearch", response, len(messages))
   
   # Better - matches actual agent names
   log_token_consumption("Broker", response, len(messages))
   ```

3. **Include Context Information**
   ```python
   # Provide input message count for better context
   log_token_consumption("AgentName", response, len(input_messages))
   ```

4. **Handle Errors Gracefully**
   ```python
   # The logging function already handles errors internally
   # No need for try/catch around log_token_consumption calls
   ```

### For Operations

1. **Monitor Daily Usage**
   - Set up log aggregation for daily token consumption
   - Track usage trends by agent
   - Identify high-consumption patterns

2. **Cost Management**
   - Use cost logging for budget tracking
   - Set up alerts for unusual consumption spikes
   - Regular cost analysis per agent/feature

3. **Performance Optimization**
   - Identify agents with high token usage
   - Analyze input/output ratios
   - Optimize prompts based on token consumption data

## Troubleshooting

### Common Issues

1. **No Token Data Logged**
   ```
   🤖 TOKEN CONSUMPTION | Agent: AgentName | Unable to extract token usage
   ```
   **Cause**: LLM response format not recognized
   **Solution**: Check LLM provider compatibility, update token extraction logic if needed

2. **Zero Token Counts**
   ```
   🤖 TOKEN CONSUMPTION | Agent: AgentName | Input: 0 tokens | Output: 0 tokens
   ```
   **Cause**: Response metadata missing or in unexpected format
   **Solution**: Verify LLM response structure, update extraction logic

3. **Missing Logs**
   **Cause**: Import error or function not called after LLM invocation
   **Solution**: Ensure `log_token_consumption` is imported and called after each `model.ainvoke()`

### Debug Mode

Enable debug logging to see detailed information:

```python
import logging
logging.getLogger("src.infrastructure.ai.utils.token_logger").setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Real-time Dashboards**
   - Live token consumption monitoring
   - Agent performance metrics
   - Cost tracking dashboards

2. **Advanced Analytics**
   - Token efficiency metrics
   - Conversation-level aggregation
   - Usage pattern analysis

3. **Integration Enhancements**
   - Webhook notifications for high usage
   - Integration with monitoring systems
   - Automated cost reporting

4. **Optimization Tools**
   - Prompt optimization suggestions
   - Token usage alerts
   - Performance recommendations

## API Reference

### Functions

#### `log_token_consumption(agent_name, response, input_message_count=0)`
Basic token consumption logging.

**Parameters:**
- `agent_name` (str): Name of the agent making the LLM call
- `response` (Any): Response object from `model.ainvoke()`
- `input_message_count` (int): Number of input messages for context

#### `log_token_consumption_with_model_info(agent_name, response, input_message_count=0, model_name=None)`
Enhanced logging with model information.

**Parameters:**
- `agent_name` (str): Name of the agent
- `response` (Any): LLM response object
- `input_message_count` (int): Number of input messages
- `model_name` (str, optional): Name of the model used

#### `log_token_consumption_with_cost(agent_name, response, input_message_count=0, input_cost_per_1k=0.0, output_cost_per_1k=0.0)`
Cost-aware token logging.

**Parameters:**
- `agent_name` (str): Name of the agent
- `response` (Any): LLM response object
- `input_message_count` (int): Number of input messages
- `input_cost_per_1k` (float): Cost per 1000 input tokens in USD
- `output_cost_per_1k` (float): Cost per 1000 output tokens in USD

#### `calculate_token_cost(input_tokens, output_tokens, input_cost_per_1k=0.0, output_cost_per_1k=0.0)`
Calculate cost for given token usage.

**Returns:**
```python
{
    "input_cost": 0.006235,
    "output_cost": 0.00513,
    "total_cost": 0.011365,
    "currency": "USD"
}
```

## Examples

### Complete Agent Implementation

```python
from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langgraph.types import StreamWriter

from src.infrastructure.ai.utils import log_token_consumption
from src.infrastructure.lib.ai.agent_decorator import guide_agent
from src.infrastructure.lib.logger import guide_logger

@guide_agent(
    agent_name="ExampleAgent",
    tools=example_tools,
    system_prompt=system_prompt,
    partners=["OtherAgent"],
    description="Example agent with token logging",
)
async def call_example_agent(
    state: State,
    writer: StreamWriter,
    model: Runnable,
) -> dict:
    """Example agent with comprehensive token logging."""

    messages: List[BaseMessage] = state.get("messages", [])
    loaded_memories: Optional[Dict[str, Any]] = state.get("loaded_memories")

    # Prepare user memory
    user_memory_str = "No relevant past interactions found."
    if loaded_memories:
        memory_parts = []
        for schema_name, content in loaded_memories.items():
            memory_parts.append(f"### {schema_name} Memory\n{content}")
        user_memory_str = "\n\n".join(memory_parts)

    guide_logger.debug(f"Example Agent invoked with {len(messages)} messages")

    # Make LLM call
    response = await model.ainvoke(
        {"messages": messages, "user_memory": user_memory_str}
    )

    # Log token consumption
    log_token_consumption("ExampleAgent", response, len(messages))

    return response
```

### Monitoring Script

```python
#!/usr/bin/env python3
"""
Token consumption monitoring script for MBRAS AI system.
"""

import re
from collections import defaultdict
from datetime import datetime, timedelta

def analyze_token_usage(log_file_path: str):
    """Analyze token usage from log file."""
    
    agent_stats = defaultdict(lambda: {
        'total_calls': 0,
        'total_input_tokens': 0,
        'total_output_tokens': 0,
        'total_tokens': 0
    })
    
    token_pattern = r'🤖 TOKEN CONSUMPTION \| Agent: (\w+) \| Input: (\d+) tokens \| Output: (\d+) tokens \| Total: (\d+) tokens'
    
    with open(log_file_path, 'r') as f:
        for line in f:
            match = re.search(token_pattern, line)
            if match:
                agent, input_tokens, output_tokens, total_tokens = match.groups()
                
                agent_stats[agent]['total_calls'] += 1
                agent_stats[agent]['total_input_tokens'] += int(input_tokens)
                agent_stats[agent]['total_output_tokens'] += int(output_tokens)
                agent_stats[agent]['total_tokens'] += int(total_tokens)
    
    # Print summary
    print("Token Usage Summary")
    print("=" * 50)
    
    for agent, stats in agent_stats.items():
        print(f"\n{agent}:")
        print(f"  Calls: {stats['total_calls']}")
        print(f"  Input Tokens: {stats['total_input_tokens']:,}")
        print(f"  Output Tokens: {stats['total_output_tokens']:,}")
        print(f"  Total Tokens: {stats['total_tokens']:,}")
        if stats['total_calls'] > 0:
            print(f"  Avg Tokens/Call: {stats['total_tokens'] / stats['total_calls']:.1f}")

if __name__ == "__main__":
    # Analyze today's logs
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/app_{today}.log"
    analyze_token_usage(log_file)
```

This comprehensive token consumption logging system provides complete visibility into LLM usage across the MBRAS AI system, enabling effective monitoring, optimization, and cost management.