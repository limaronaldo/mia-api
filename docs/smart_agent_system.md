# Smart Agent Graph System Documentation

## Overview

The Smart Agent Graph System is a revolutionary approach to building AI agent workflows that eliminates code duplication while providing maximum flexibility. The system supports three distinct architecture patterns:

1. **Isolated Agent Graphs**: Each agent has its own complete workflow
2. **Enhanced Shared Systems**: Traditional shared graphs with advanced features
3. **Pure Multi-Agent Systems**: Automatic handoff routing between agents

## Key Features

### 🎯 Zero Code Duplication
- All infrastructure handled automatically by the `@guide_agent` decorator
- Consistent behavior across all agents
- No need to manually implement routing, validation, or retry logic

### 🔧 Flexible Architecture
- Mix isolated and shared approaches as needed
- Switch between patterns without code changes
- Seamless integration with existing systems

### 🤖 Automatic Agent Capabilities
Every agent automatically gets:
- Tool execution flow
- Response validation
- Retry logic with context
- Event emission
- Memory management
- Partner handoff capabilities

### 🌐 Multi-Agent Handoffs
- Automatic tool creation for partner agents
- Comprehensive task descriptions
- Bidirectional transfers
- Context preservation across handoffs

## Architecture Patterns

### 1. Isolated Agent Graphs

Each agent operates in its own complete workflow with full control over its execution flow.

**When to Use:**
- Need complete agent isolation
- Want independent deployment/scaling
- Require agent-specific customizations
- Building microservice-style architectures

**Features:**
- Complete workflow isolation
- Independent tool execution
- Separate validation and retry logic
- Individual event streams

**Example:**
```python
@guide_agent(
    agent_name="ResearchAgent",
    model="heavy",
    tools=[search_tool, analyze_tool],
    system_prompt="You are a research specialist...",
    create_graph=True,  # Creates isolated graph
    state_class=State,
)
async def research_agent(state: State, writer, model) -> State:
    messages = state.get("messages", [])
    response = await model.ainvoke({"messages": messages})
    return {**state, "messages": messages + [response]}

# Usage
research_graph = research_agent  # This is now a compiled graph
result = await research_graph.ainvoke({"messages": [user_message]})
```

### 2. Enhanced Shared Systems

Traditional shared graph approach with advanced features like memory loading, suggestions, and comprehensive validation.

**When to Use:**
- Need centralized control
- Want shared memory and context
- Building traditional chatbot systems
- Require complex validation workflows

**Features:**
- Centralized memory management
- Shared validation and retry logic
- Suggestion generation
- Complex routing capabilities

**Example:**
```python
# Agents work within shared graph system
@guide_agent(
    agent_name="Broker",
    partners=["lead_seeker"],
    system_prompt="You are a luxury real estate assistant...",
)
async def broker_agent(state, writer, model):
    # Agent logic here
    return response

# System creates shared graph with all infrastructure
system = create_enhanced_mbras_system()
result = await system.ainvoke({"messages": [user_message], "user_id": "123"})
```

### 3. Pure Multi-Agent Systems

Automatic handoff routing between isolated agents using the decorator's built-in capabilities.

**When to Use:**
- Need automatic agent routing
- Want maximum flexibility
- Building complex multi-agent workflows
- Require dynamic conversation flows

**Features:**
- Automatic handoff routing
- Agent isolation with communication
- Dynamic conversation flows
- Built-in partner management

**Example:**
```python
# Create isolated agents with partner capabilities
broker_agent = create_isolated_broker()
lead_seeker_agent = create_isolated_lead_seeker()

# System automatically creates handoff routing
multi_system = create_multi_agent_system(
    agents=[broker_agent, lead_seeker_agent],
    state_class=State
)

result = await multi_system.ainvoke({"messages": [user_message]})
```

## Decorator Parameters

### Core Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_name` | `str` | Unique identifier for the agent |
| `model` | `Literal["standard", "heavy", "lite"]` | Model type to use |
| `tools` | `List[Callable]` | Tools available to the agent |
| `system_prompt` | `str` | System prompt template |

### Advanced Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `custom_prompt_template` | `ChatPromptTemplate` | Full prompt customization |
| `response_model` | `Type[BaseModel]` | Automatic structured output |
| `partners` | `List[str]` | Partner agents for handoffs |
| `create_graph` | `bool` | Create isolated graph |
| `state_class` | `Type` | State class for graph |

### Function Parameters

Decorated functions can accept these optional parameters:

| Parameter | Description |
|-----------|-------------|
| `state` | Current state (always first parameter) |
| `writer` | StreamWriter for event emission |
| `model` | Chained model (prompt + model + tools) |
| `base_model` | Raw model for advanced operations |
| `prompt_template` | The ChatPromptTemplate being used |

## Partner Handoff System

### Automatic Tool Creation

When you specify `partners=["agent1", "agent2"]`, the decorator automatically creates:
- `transfer_to_agent1(task_description: str)`
- `transfer_to_agent2(task_description: str)`

### Automatic Instructions

The system automatically appends partner guidelines to system prompts:

```
<IMPORTANT_PARTNER_GUIDELINES>
You have access to specialized partner agents: agent1, agent2.

CRITICAL: If a user's question is related to specialized areas, you MUST 
transfer to the appropriate partner agent using transfer_to_[partner_name] tool.

Available transfers:
- transfer_to_agent1: Use when conversation involves agent1-related topics
- transfer_to_agent2: Use when conversation involves agent2-related topics

Always provide comprehensive task_description including:
- Complete context of user's request
- Relevant conversation history
- Specific requirements mentioned
- Important details partner needs

Do NOT handle specialized requests yourself when partner is available.
</IMPORTANT_PARTNER_GUIDELINES>
```

### Usage Examples

```python
# User asks: "I want to list my apartment"
# General agent automatically calls: 
# transfer_to_lead_seeker("User wants to list apartment for sale. Collect property details...")

# User asks: "Help me research market trends"  
# General agent automatically calls:
# transfer_to_research_agent("User needs market research on real estate trends...")
```

## Implementation Examples

### MBRAS Real Estate System

```python
from src.infrastructure.ai.graphs.chat.smart_system import (
    SmartAgentSystem,
    create_enhanced_mbras_system,
    create_isolated_broker,
    create_pure_multi_agent_system
)

# Option 1: Enhanced shared system (recommended)
mbras_system = create_enhanced_mbras_system()

# Option 2: Isolated agents
broker_graph = create_isolated_broker()
lead_seeker_graph = create_isolated_lead_seeker()

# Option 3: Pure multi-agent system
multi_agent_system = create_pure_multi_agent_system()

# Option 4: Full system manager
system_manager = SmartAgentSystem()
system_manager.create_broker_isolated()
system_manager.create_lead_seeker_isolated() 
system_manager.create_enhanced_shared_system()

# List available systems
available = system_manager.list_available_systems()
# Output: {
#     "isolated_agents": ["broker", "lead_seeker"],
#     "shared_systems": ["enhanced", "multi_agent"] 
# }
```

### Customer Support System

```python
@guide_agent(
    agent_name="customer_service",
    partners=["technical_support", "billing_specialist"],
    create_graph=True,
    state_class=State,
)
async def customer_service_agent(state, writer, model):
    # Automatically gets handoff tools for partners
    return response

@guide_agent(
    agent_name="technical_support", 
    partners=["research_agent", "customer_service"],
    create_graph=True,
    state_class=State,
)
async def technical_support_agent(state, writer, model):
    return response

# Create multi-agent support system
support_system = create_multi_agent_system(
    agents=[customer_service_agent, technical_support_agent],
    state_class=State
)
```

### Structured Output Agent

```python
class DataAnalysis(BaseModel):
    summary: str = Field(description="Analysis summary")
    insights: List[str] = Field(description="Key insights")
    recommendations: List[str] = Field(description="Recommendations")

@guide_agent(
    agent_name="data_analyzer",
    response_model=DataAnalysis,  # Automatic structured output
    create_graph=True,
    state_class=State,
)
async def data_analyzer_agent(state, writer, model):
    # Model automatically returns DataAnalysis instances
    result = await model.ainvoke({"messages": state["messages"]})
    # result is guaranteed to be DataAnalysis instance
    return {**state, "analysis": result}
```

## Migration Guide

### From Traditional Agents

**Before:**
```python
async def old_agent(state, writer, model):
    # Manual infrastructure code
    messages = state["messages"]
    retry_context = state.get("retry_context")
    
    if retry_context:
        # Manual retry handling
        pass
    
    response = await model.ainvoke({"messages": messages})
    
    # Manual tool call handling
    if response.tool_calls:
        # Manual tool emission
        pass
    
    # Manual message management
    messages.append(response)
    if len(messages) > 30:
        messages = messages[-30:]
    
    return {"messages": messages}
```

**After:**
```python
@guide_agent(
    agent_name="MyAgent",
    tools=my_tools,
    system_prompt="My agent prompt"
)
async def new_agent(state, writer, model):
    # All infrastructure handled automatically
    messages = state["messages"] 
    response = await model.ainvoke({"messages": messages})
    return response
```

### Adding Isolation

**Shared Agent:**
```python
@guide_agent(agent_name="MyAgent", tools=tools, system_prompt=prompt)
async def shared_agent(state, writer, model):
    return response
```

**Isolated Agent:**
```python
@guide_agent(
    agent_name="MyAgent", 
    tools=tools, 
    system_prompt=prompt,
    create_graph=True,    # Add this
    state_class=State,    # Add this
)
async def isolated_agent(state, writer, model):
    return {**state, "messages": updated_messages}  # Return state
```

### Adding Partners

**Before:**
```python
system_prompt = """
You are an assistant.
For technical issues, transfer to technical_support using transfer_to_technical_support.
"""

# Manual tool creation and binding
```

**After:**
```python
@guide_agent(
    agent_name="assistant",
    partners=["technical_support"],  # Automatic tool creation and instructions
    system_prompt="You are an assistant."  # Clean prompt
)
```

## Best Practices

### 1. Choose the Right Pattern

- **Isolated Graphs**: For microservices, independent scaling, specialized workflows
- **Shared Systems**: For traditional chatbots, centralized control, complex validation
- **Multi-Agent**: For dynamic workflows, automatic routing, conversation handoffs

### 2. Agent Naming

```python
# Good: Consistent naming
@guide_agent(agent_name="Broker", partners=["lead_seeker"])
@guide_agent(agent_name="lead_seeker", partners=["Broker"]) 

# Bad: Inconsistent casing
@guide_agent(agent_name="broker", partners=["Lead_Seeker"])
```

### 3. Memory Management

```python
# Good: Handle user memory
user_memory_str = "No relevant past interactions found."
if loaded_memories:
    memory_parts = []
    for schema_name, content in loaded_memories.items():
        memory_parts.append(f"### {schema_name} Memory\n{content}")
    user_memory_str = "\n\n".join(memory_parts)

response = await model.ainvoke({
    "messages": messages, 
    "user_memory": user_memory_str
})
```

### 4. Error Handling

```python
# Good: Let decorator handle infrastructure errors
@guide_agent(agent_name="MyAgent")
async def my_agent(state, writer, model):
    try:
        # Focus on business logic errors only
        result = await some_business_operation()
        response = await model.ainvoke({"messages": state["messages"]})
        return response
    except BusinessLogicError as e:
        # Handle business-specific errors
        writer({"event": "business_error", "data": str(e)})
        return {"error": str(e)}
```

### 5. Testing

```python
# Test isolated agents
async def test_isolated_agent():
    agent_graph = my_isolated_agent
    result = await agent_graph.ainvoke({
        "messages": [{"role": "user", "content": "test message"}]
    })
    assert "messages" in result

# Test shared systems  
async def test_shared_system():
    system = create_my_shared_system()
    result = await system.ainvoke({
        "messages": [{"role": "user", "content": "test message"}],
        "user_id": "test_user"
    })
    assert result["messages"]
```

## Troubleshooting

### Common Issues

1. **Agent not transferring to partners**
   - Check partner names match exactly (case-sensitive)
   - Verify system prompt includes transfer instructions
   - Ensure partners list is provided to decorator

2. **Isolated graph not working**
   - Verify `create_graph=True` is set
   - Ensure `state_class` is provided
   - Check agent returns State dict, not just response

3. **Tools not executing**
   - Verify tools are bound to model
   - Check tool names and parameters
   - Ensure tools are importable

4. **Memory not loading**
   - Check `loaded_memories` in state
   - Verify memory formatting in agent
   - Ensure memory step runs before agent

### Debugging

```python
# Enable debug logging
from src.infrastructure.lib.logger import guide_logger
import logging
guide_logger.setLevel(logging.DEBUG)

# Check agent configuration
if hasattr(agent_func, '_agent_config'):
    config = agent_func._agent_config
    print(f"Agent: {config['agent_name']}")
    print(f"Partners: {config['partners']}")
    print(f"Tools: {len(config['tools'])}")

# Check graph structure
if hasattr(graph, '_agent_name'):
    print(f"Graph agent: {graph._agent_name}")
    print(f"Graph tools: {graph._agent_tools}")
```

## Performance Considerations

### Memory Usage
- Isolated graphs use more memory per agent
- Shared systems more memory-efficient for many agents
- Consider agent lifecycle management

### Latency
- Isolated graphs: Lower latency (no routing overhead)
- Shared systems: Higher latency (routing and validation)
- Multi-agent: Variable latency (depends on handoffs)

### Scaling
- Isolated graphs: Independent scaling per agent
- Shared systems: Scale entire system together
- Multi-agent: Hybrid scaling approach

## Future Enhancements

### Planned Features
- [ ] Dynamic agent creation
- [ ] Agent hot-swapping
- [ ] Advanced routing strategies
- [ ] Performance monitoring
- [ ] Agent composition patterns

### Contributing
The smart agent system is designed to be extensible. Key areas for contribution:
- New routing strategies
- Performance optimizations
- Additional validation patterns
- Monitoring and observability features

## Conclusion

The Smart Agent Graph System represents a paradigm shift in AI agent architecture, eliminating boilerplate code while providing unprecedented flexibility. Whether you need isolated agents, shared systems, or multi-agent handoffs, the decorator-based approach ensures consistent, maintainable, and scalable agent implementations.

Choose the pattern that best fits your use case, and let the system handle all the infrastructure complexity automatically.