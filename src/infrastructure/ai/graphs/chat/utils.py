from typing import Dict, List, Optional, Sequence, Tuple

from decouple import config
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, merge_message_runs
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore

from src.infrastructure.lib.logger import guide_logger


async def get_saver():
    return AsyncPostgresSaver.from_conn_string(config("DB_URI").replace("+psycopg", ""))


async def get_store():
    return AsyncPostgresStore.from_conn_string(
        conn_string=config("DB_URI").replace("+psycopg", ""),
        index={
            "dims": 1536,
            "embed": init_embeddings(
                "openai:text-embedding-3-small", api_key=str(config("OPENAI_API_KEY"))
            ),
            "fields": ["text"],
        },
    )


def init_model(fully_specified_name: str) -> BaseChatModel:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name
    return init_chat_model(model, model_provider=provider)


def prepare_messages(
    messages: Sequence[BaseMessage], system_prompt: str
) -> list[BaseMessage]:
    """Merge message runs and add instructions before and after to stay on task."""
    sys = {
        "role": "system",
        "content": f"""{system_prompt}

<memory-system>Reflect on following interaction. Use the provided tools to \
 retain any necessary memories about the user. Use parallel tool calling to handle updates & insertions simultaneously.</memory-system>
""",
    }
    m = {
        "role": "user",
        "content": "## End of conversation\n\n"
        "<memory-system>Reflect on the interaction above."
        " What memories ought to be retained or updated?</memory-system>",
    }
    return list(merge_message_runs(messages=[sys] + list(messages) + [m]))


class TransferLoopDetector:
    """
    Detects and prevents agent transfer loops in multi-agent conversations.

    This class analyzes conversation history to identify patterns where agents
    transfer tasks back and forth without making progress, which wastes resources
    and creates poor user experiences.
    """

    def __init__(self, max_history: int = 10, loop_threshold: int = 2):
        """
        Initialize the transfer loop detector.

        Args:
            max_history: Maximum number of transfers to track
            loop_threshold: Number of back-and-forth transfers to consider a loop
        """
        self.max_history = max_history
        self.loop_threshold = loop_threshold

    def extract_recent_transfers(
        self, messages: List[BaseMessage]
    ) -> List[Dict[str, any]]:
        """
        Extract recent transfer information from message history.

        Args:
            messages: List of conversation messages

        Returns:
            List of transfer records with agent names and positions
        """
        transfers = []

        recent_messages = (
            messages[-self.max_history :]
            if len(messages) > self.max_history
            else messages
        )

        for i, msg in enumerate(recent_messages):
            if (
                isinstance(msg, AIMessage)
                and hasattr(msg, "tool_calls")
                and msg.tool_calls
            ):
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.get("name", "")
                    if tool_name.startswith("transfer_to_"):
                        target_agent = tool_name.replace("transfer_to_", "")

                        source_agent = self._infer_source_agent(recent_messages, i)

                        transfers.append(
                            {
                                "from": source_agent,
                                "to": target_agent,
                                "message_index": len(messages)
                                - len(recent_messages)
                                + i,
                                "tool_call_id": tool_call.get("id", ""),
                                "timestamp_relative": i,
                            }
                        )

        return transfers[-self.max_history :]

    def _infer_source_agent(
        self, messages: List[BaseMessage], current_index: int
    ) -> str:
        """
        Infer the source agent that made the transfer call.

        Args:
            messages: Recent messages to analyze
            current_index: Index of current message with transfer

        Returns:
            Name of the source agent
        """

        if current_index > 0:
            return "previous_agent"
        return "unknown_agent"

    def detect_immediate_loop(
        self, current_agent: str, target_agent: str, transfers: List[Dict[str, any]]
    ) -> bool:
        """
        Detect if the proposed transfer would create an immediate loop.

        Args:
            current_agent: Agent attempting to transfer
            target_agent: Agent being transferred to
            transfers: Recent transfer history

        Returns:
            True if this would create an immediate loop
        """
        if not transfers:
            return False

        most_recent = transfers[-1] if transfers else None
        if (
            most_recent
            and most_recent.get("from") == target_agent
            and most_recent.get("to") == current_agent
        ):
            guide_logger.warning(
                f"Immediate loop detected: {target_agent} → {current_agent} → {target_agent}"
            )
            return True

        return False

    def detect_ping_pong_pattern(
        self, current_agent: str, target_agent: str, transfers: List[Dict[str, any]]
    ) -> bool:
        """
        Detect ping-pong patterns between two agents.

        Args:
            current_agent: Agent attempting to transfer
            target_agent: Agent being transferred to
            transfers: Recent transfer history

        Returns:
            True if a ping-pong pattern is detected
        """
        if len(transfers) < self.loop_threshold:
            return False

        agent_pair = {current_agent, target_agent}
        recent_relevant_transfers = []

        for transfer in reversed(transfers):
            from_agent = transfer.get("from", "")
            to_agent = transfer.get("to", "")

            if from_agent in agent_pair and to_agent in agent_pair:
                recent_relevant_transfers.append(transfer)

                if len(recent_relevant_transfers) >= self.loop_threshold:
                    break

        if len(recent_relevant_transfers) >= self.loop_threshold:
            alternating = True
            for i in range(1, len(recent_relevant_transfers)):
                prev_transfer = recent_relevant_transfers[i - 1]
                curr_transfer = recent_relevant_transfers[i]

                if prev_transfer.get("from") != curr_transfer.get(
                    "to"
                ) or prev_transfer.get("to") != curr_transfer.get("from"):
                    alternating = False
                    break

            if alternating:
                guide_logger.warning(
                    f"Ping-pong pattern detected between {current_agent} and {target_agent}"
                )
                return True

        return False

    def is_transfer_loop(
        self, current_agent: str, target_agent: str, messages: List[BaseMessage]
    ) -> Tuple[bool, str]:
        """
        Main method to detect if a proposed transfer would create a loop.

        Args:
            current_agent: Agent attempting to transfer
            target_agent: Agent being transferred to
            messages: Full conversation history

        Returns:
            Tuple of (is_loop, reason) where reason explains why it's a loop
        """

        transfers = self.extract_recent_transfers(messages)

        if self.detect_immediate_loop(current_agent, target_agent, transfers):
            return (
                True,
                f"Immediate loop: {target_agent} just transferred to {current_agent}",
            )

        if self.detect_ping_pong_pattern(current_agent, target_agent, transfers):
            return (
                True,
                f"Ping-pong pattern detected between {current_agent} and {target_agent}",
            )

        return False, ""

    def get_transfer_suggestion(
        self, current_agent: str, user_request: str, transfers: List[Dict[str, any]]
    ) -> Optional[str]:
        """
        Suggest what the current agent should do instead of transferring.

        Args:
            current_agent: Agent that needs guidance
            user_request: Original user request
            transfers: Recent transfer history

        Returns:
            Suggestion for what agent should do instead of transferring
        """
        suggestions = {
            "Broker": "Use search_properties or deep_search_properties to find matching properties",
            "Concierge_Agent": "Use scheduling tools to arrange viewings or send portfolio via email/WhatsApp",
            "Market_Analyst": "Use analysis tools to provide investment insights and market data",
            "lead_seeker": "Collect property details from user wanting to list their property",
        }

        base_suggestion = suggestions.get(
            current_agent, "Execute your primary function"
        )

        if transfers:
            recent_transfer = transfers[-1]
            from_agent = recent_transfer.get("from", "")

            if current_agent == "Broker" and from_agent == "Concierge_Agent":
                return "Complete the property search that Concierge transferred to you, then you can transfer logistics back"

            elif current_agent == "Concierge_Agent" and from_agent == "Broker":
                return "Execute the logistics tasks (portfolio delivery, neighborhood research) that Broker assigned to you"

        return base_suggestion


loop_detector = TransferLoopDetector()


def detect_transfer_loop(
    current_agent: str, target_agent: str, messages: List[BaseMessage]
) -> Tuple[bool, str]:
    """
    Convenience function to detect transfer loops.

    Args:
        current_agent: Agent attempting transfer
        target_agent: Target agent
        messages: Conversation history

    Returns:
        Tuple of (is_loop, reason)
    """
    return loop_detector.is_transfer_loop(current_agent, target_agent, messages)


def get_loop_prevention_guidance(
    current_agent: str, user_request: str, messages: List[BaseMessage]
) -> str:
    """
    Get guidance for agent on what to do instead of transferring.

    Args:
        current_agent: Agent needing guidance
        user_request: User's request
        messages: Conversation history

    Returns:
        Specific guidance for the agent
    """
    transfers = loop_detector.extract_recent_transfers(messages)
    suggestion = loop_detector.get_transfer_suggestion(
        current_agent, user_request, transfers
    )

    return (
        suggestion
        or f"Execute {current_agent} core function as defined in system prompt"
    )
