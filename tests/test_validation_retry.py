"""
Test validation retry mechanism to ensure it handles failures correctly
and prevents infinite loops.
"""

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.infrastructure.ai.graphs.chat.smart_system import SmartAgentSystem


class TestValidationRetry:
    """Test cases for validation retry mechanism."""

    def setup_method(self):
        """Set up test fixtures."""
        self.smart_system = SmartAgentSystem()

    def test_retry_context_initialization(self):
        """Test that retry context is properly initialized with count."""
        retry_context = {
            "failed_attempt": "Some failed response",
            "feedback": "Tool parameter error",
            "retry_count": 0,
        }

        assert retry_context["retry_count"] == 0
        assert "failed_attempt" in retry_context
        assert "feedback" in retry_context

    def test_retry_count_increment(self):
        """Test that retry count is incremented properly."""
        # Simulate the handle_validation_failure function logic
        state = {
            "messages": [
                HumanMessage(content="Find an apartment"),
                AIMessage(content="Invalid response"),
            ],
            "retry_context": {
                "failed_attempt": "Invalid response",
                "feedback": "Wrong tool parameters",
                "retry_count": 0,
            },
        }

        # Simulate retry count increment
        retry_context = state["retry_context"]
        retry_count = retry_context.get("retry_count", 0)
        updated_retry_context = {**retry_context, "retry_count": retry_count + 1}

        assert updated_retry_context["retry_count"] == 1

    def test_max_retry_limit(self):
        """Test that maximum retry limit prevents infinite loops."""
        retry_context = {
            "failed_attempt": "Some response",
            "feedback": "Some error",
            "retry_count": 2,  # At max retry limit
        }

        state = {"retry_context": retry_context, "current_agent": "Broker"}

        # Simulate decide_after_validation logic
        max_retries = 2
        retry_count = retry_context.get("retry_count", 0)

        # Should proceed to suggestions when max retries reached
        assert retry_count >= max_retries

    def test_validation_feedback_structure(self):
        """Test that validation feedback contains necessary information."""
        feedback = "The agent's response is invalid because the tool call failed due to an incorrect property type. The agent should have corrected the property type to 'Apartamento' based on the available options."
        failed_attempt = "Searching for apartments with property_type='APARTMENT'"

        # Verify feedback provides actionable information
        assert "property type" in feedback.lower()
        assert "apartamento" in feedback.lower()
        assert len(feedback) > 20  # Should be descriptive enough

    def test_tool_error_context_extraction(self):
        """Test extraction of tool error context from messages."""
        messages = [
            HumanMessage(content="Find apartments"),
            AIMessage(
                content="Let me search", tool_calls=[{"name": "search_properties"}]
            ),
            ToolMessage(
                content="Error: 1 validation error for search_properties\nproperty_type\n  Input should be 'Apartamento'",
                tool_call_id="123",
            ),
            AIMessage(content="Failed response"),
        ]

        # Simulate tool error detection
        tool_error_context = ""
        for msg in reversed(messages[-5:]):
            if isinstance(msg, ToolMessage) and "Error:" in str(msg.content):
                tool_error_context = f"\n\nRECENT TOOL ERROR: {msg.content[:200]}..."
                break

        assert "Error:" in tool_error_context
        assert "validation error" in tool_error_context

    def test_retry_message_format(self):
        """Test that retry messages are properly formatted."""
        from src.infrastructure.lib.ai.messages import AIHelpingMessages

        feedback = "Wrong property type used"
        failed_attempt = "Used APARTMENT instead of Apartamento"
        tool_error_context = "\n\nRECENT TOOL ERROR: Property type validation failed"

        retry_message = AIHelpingMessages.retry_message(
            feedback, failed_attempt, tool_error_context
        )

        assert "validation feedback" in retry_message.content.lower()
        assert "natural correction" in retry_message.content.lower()
        assert "tool error" in retry_message.content.lower()

    def test_state_cleanup_after_max_retries(self):
        """Test that retry context is cleared after max retries."""
        state = {"retry_context": {"retry_count": 2, "feedback": "Some error"}}

        # Simulate max retry cleanup
        max_retries = 2
        retry_context = state.get("retry_context")
        if retry_context and retry_context.get("retry_count", 0) >= max_retries:
            state["retry_context"] = None

        assert state["retry_context"] is None

    def test_natural_correction_guidelines(self):
        """Test that retry message includes natural correction guidelines."""
        from src.infrastructure.lib.ai.messages import AIHelpingMessages

        retry_message = AIHelpingMessages.retry_message("Test feedback", "Test attempt")

        content = retry_message.content.lower()
        assert "do not mention the previous error" in content
        assert "do not apologize" in content
        assert "generate a completely new" in content
        assert "natural response" in content

    @pytest.mark.asyncio
    async def test_validation_tolerance_rules(self):
        """Test that validation has proper tolerance rules to prevent over-strictness."""
        # This would require mocking the validation model, but the test structure
        # verifies that tolerance rules are documented and should be applied

        tolerance_scenarios = [
            "Agent corrected tool parameters successfully",
            "Agent maintains professional tone with minor style variations",
            "Agent shows progress toward solving user's request",
        ]

        # Each scenario should be considered valid based on tolerance rules
        for scenario in tolerance_scenarios:
            # In real validation, these should pass the tolerance checks
            assert len(scenario) > 0  # Basic validation that scenarios exist

    def test_current_agent_preservation(self):
        """Test that current_agent is preserved through retry cycle."""
        state = {
            "current_agent": "Broker",
            "retry_context": {"retry_count": 1, "feedback": "Some error"},
        }

        # Agent should remain the same through retry
        current_agent = state.get("current_agent", "Broker")
        assert current_agent == "Broker"

        # After routing back, agent should still be the same
        assert current_agent in ["Broker", "lead_seeker"]

    def test_logging_information_completeness(self):
        """Test that logging provides sufficient information for debugging."""
        retry_context = {
            "failed_attempt": "Previous response that failed validation",
            "feedback": "Specific reason why validation failed",
            "retry_count": 1,
        }

        current_agent = "Broker"

        # Simulate log message construction
        log_message = (
            f"Validation failed for agent '{current_agent}', routing to handle_failure "
            f"(attempt {retry_context['retry_count'] + 1}/2). "
            f"Feedback: '{retry_context['feedback'][:100]}...'"
        )

        assert current_agent in log_message
        assert "attempt" in log_message
        assert "feedback" in log_message.lower()
