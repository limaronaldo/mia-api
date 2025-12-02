import asyncio
import sys
from typing import Any, Dict

# Add the project root to the Python path
sys.path.append("..")

from langgraph.runtime import Runtime
from langgraph.types import StreamWriter

from src.infrastructure.lib.ai.agent_decorator import guide_agent


# Mock a simple StreamWriter
def mock_stream_writer(data: Any) -> None:
    print(f"📡 StreamWriter received: {data}")


# Create a test agent using the decorator
@guide_agent(
    agent_name="TestAgent",
    model="standard",
    tools=[],
    system_prompt="You are a test agent",
)
async def test_agent(
    state: Dict[str, Any], writer: StreamWriter, model
) -> Dict[str, Any]:
    """Test agent that uses the writer and model."""
    print(f"🧪 Test agent called with state: {state}")
    print(f"🧪 Writer type: {type(writer)}")
    print(f"🧪 Model type: {type(model)}")

    # Test using the writer
    writer({"event": "test_message", "data": {"content": "Hello from test agent!"}})

    return {"test_result": "success"}


async def test_langgraph_calling_pattern():
    """Test how LangGraph would call our agent function."""

    # Create a test state (what LangGraph passes as the single argument)
    test_state = {"messages": [], "user_id": "test_user"}

    # Mock the Runtime context that LangGraph would set up
    runtime = Runtime(
        context=None, store=None, stream_writer=mock_stream_writer, previous=None
    )

    print("=" * 60)
    print("🧪 Testing LangGraph calling pattern")
    print("=" * 60)

    # This simulates how LangGraph calls agent functions:
    # - Only passes state as a single positional argument
    # - StreamWriter is available through get_runtime()

    # We need to mock the get_runtime() function to return our test runtime
    import src.infrastructure.lib.ai.agent_decorator as agent_module

    original_get_runtime = agent_module.get_runtime
    agent_module.get_runtime = lambda: runtime

    try:
        # Call the decorated function the way LangGraph would
        result = await test_agent(test_state)  # Only pass state, no writer or model

        print(f"✅ Agent call successful! Result: {result}")

    except Exception as e:
        print(f"❌ Agent call failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Restore original function
        agent_module.get_runtime = original_get_runtime


async def test_without_runtime():
    """Test what happens when get_runtime() fails."""

    test_state = {"messages": [], "user_id": "test_user"}

    print("\n" + "=" * 60)
    print("🧪 Testing without Runtime (fallback scenario)")
    print("=" * 60)

    # Mock get_runtime to raise an exception (simulating when it's not available)
    import src.infrastructure.lib.ai.agent_decorator as agent_module

    original_get_runtime = agent_module.get_runtime

    def failing_get_runtime():
        raise RuntimeError("Runtime not available")

    agent_module.get_runtime = failing_get_runtime

    try:
        result = await test_agent(test_state)
        print(f"✅ Agent call with fallback successful! Result: {result}")

    except Exception as e:
        print(f"❌ Agent call with fallback failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Restore original function
        agent_module.get_runtime = original_get_runtime


if __name__ == "__main__":
    print("🚀 Starting StreamWriter Runtime Tests")

    # Run both tests
    asyncio.run(test_langgraph_calling_pattern())
    asyncio.run(test_without_runtime())

    print("\n🎉 Tests completed!")
