from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import MessagesState


class RetryContext(TypedDict):
    failed_attempt: str
    feedback: str


class State(MessagesState):
    """Representa o estado do grafo de chat, incluindo contexto de memória e retry."""

    suggested_questions: Optional[List[str]]
    retry_context: Optional[RetryContext]
    user_id: Optional[str]
    loaded_memories: Optional[Dict[str, Any]]
    function_name: Optional[str]
    current_agent: Optional[str]
