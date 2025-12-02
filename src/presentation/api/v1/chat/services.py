import json
from typing import AsyncGenerator
from uuid import UUID

from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from sqlalchemy import exists, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.ai.graphs.chat import chat_app
from src.infrastructure.ai.graphs.chat.smart_system import (
    create_enhanced_mbras_system,
    create_pure_multi_agent_system,
)
from src.infrastructure.ai.graphs.chat.steps.memory_processing import (
    process_memory_step,
)
from src.infrastructure.ai.graphs.chat.utils import get_saver, get_store
from src.infrastructure.config.database import get_db_session
from src.infrastructure.lib.logger import guide_logger
from src.infrastructure.models.public import Photo
from src.infrastructure.models.relationship import UserThread


async def safe_background_memory_processing(
    state_data: dict, config: dict, system_type: str
):
    """Safe wrapper for background memory processing to handle any remaining errors."""
    try:
        thread_id = config.get("configurable", {}).get("thread_id", "unknown")
        user_id = config.get("configurable", {}).get("user_id", "unknown")
        message_count = len(state_data.get("messages", []))

        guide_logger.debug(
            f"Starting background memory processing for {system_type} system - "
            f"Thread: {thread_id}, User: {user_id}, Messages: {message_count}"
        )
        async for session in get_db_session():
            config["configurable"]["session"] = session
            await process_memory_step(state_data, config)

            guide_logger.info(
                f"Successfully completed background memory processing for {system_type} - "
                f"Thread: {thread_id}, User: {user_id}"
            )
    except Exception as e:
        guide_logger.error(
            f"Error in background memory processing for {system_type} - "
            f"Thread: {thread_id}, User: {user_id}: {e}"
        )


def create_legacy_chat_service() -> "ChatService":
    """Create ChatService with legacy system (original shared graph)."""
    return ChatService(system_type="legacy")


def create_enhanced_chat_service() -> "ChatService":
    """Create ChatService with enhanced shared system (recommended for most use cases)."""
    return ChatService(system_type="enhanced_shared")


def create_multi_agent_chat_service() -> "ChatService":
    """Create ChatService with pure multi-agent system."""
    return ChatService(system_type="multi_agent")


class ChatService:
    def __init__(self, system_type: str = "enhanced_shared", config: dict = None):
        """
        Initialize ChatService with configurable agent system.

        Args:
            system_type: Type of agent system to use
                - "legacy": Original shared system
                - "enhanced_shared": Enhanced shared system with memory and suggestions
                - "multi_agent": Pure multi-agent system with isolated workflows
            config: Optional configuration dictionary for system-specific settings
        """
        self.system_type = system_type
        self.config = config or {}
        self._agent_system = None
        self._smart_system_manager = None
        self._setup_system_config()

    async def _get_agent_system(self):
        """Get or create the appropriate agent system based on configuration."""
        if self._agent_system is not None:
            return self._agent_system

        try:
            if self.system_type == "legacy":
                self._agent_system = chat_app
            elif self.system_type == "enhanced_shared":
                self._agent_system = create_enhanced_mbras_system()
            elif self.system_type == "multi_agent":
                self._agent_system = create_pure_multi_agent_system()
            else:
                guide_logger.warning(
                    f"Unknown system type '{self.system_type}', falling back to legacy"
                )
                self._agent_system = chat_app

            guide_logger.info(f"Initialized {self.system_type} agent system")
            return self._agent_system

        except Exception as e:
            guide_logger.error(
                f"Failed to initialize {self.system_type} system: {e}. Falling back to legacy."
            )
            self._agent_system = chat_app
            self.system_type = "legacy"
            return self._agent_system

    async def switch_system(self, new_system_type: str):
        """
        Switch to a different agent system at runtime.

        Args:
            new_system_type: New system type to switch to
        """
        if new_system_type != self.system_type:
            guide_logger.info(f"Switching from {self.system_type} to {new_system_type}")
            old_system = self.system_type
            self.system_type = new_system_type
            self._agent_system = None

            try:
                await self._get_agent_system()
            except Exception as e:
                guide_logger.error(
                    f"Failed to switch to {new_system_type}: {e}. Reverting to {old_system}"
                )
                self.system_type = old_system
                self._agent_system = None
                await self._get_agent_system()

    def get_current_system_type(self) -> str:
        """Get the currently active system type."""
        return self.system_type

    def get_system_info(self) -> dict:
        """Get information about the current agent system."""
        return {
            "system_type": self.system_type,
            "available_systems": ["legacy", "enhanced_shared", "multi_agent"],
            "system_descriptions": {
                "legacy": "Original shared system with basic functionality",
                "enhanced_shared": "Enhanced shared system with memory, suggestions, and validation",
                "multi_agent": "Pure multi-agent system with isolated workflows and automatic handoffs",
            },
        }

    def _setup_system_config(self):
        """Setup system-specific configuration."""
        default_configs = {
            "legacy": {
                "recursion_limit": 10,
                "enable_memory_processing": True,
                "enable_suggestions": False,
            },
            "enhanced_shared": {
                "recursion_limit": 20,
                "enable_memory_processing": True,
                "enable_suggestions": False,
                "enhanced_validation": True,
            },
            "multi_agent": {
                "recursion_limit": 20,
                "enable_memory_processing": True,
                "enable_suggestions": True,
                "agent_isolation": True,
                "auto_handoffs": True,
            },
        }

        system_defaults = default_configs.get(self.system_type, {})
        self.config = {**system_defaults, **self.config}

        guide_logger.debug(f"System config for {self.system_type}: {self.config}")

    @classmethod
    def create_with_config(cls, system_type: str, **kwargs) -> "ChatService":
        """
        Create ChatService with specific configuration.

        Args:
            system_type: Type of system to create
            **kwargs: Configuration options specific to the system type

        Returns:
            Configured ChatService instance
        """
        return cls(system_type=system_type, config=kwargs)

    def configure_system(self, **kwargs):
        """
        Update system configuration at runtime.

        Args:
            **kwargs: Configuration options to update
        """
        self.config.update(kwargs)
        guide_logger.info(f"Updated {self.system_type} config: {kwargs}")

    def _should_process_event(self, event_type: str) -> bool:
        """Determine if event should be processed based on system type."""
        system_specific_events = {
            "enhanced_shared": [
                "agent_handoff",
                "memory_loaded",
                "validation_enhanced",
            ],
            "multi_agent": ["agent_transfer", "workflow_isolation", "system_handoff"],
            "legacy": [],
        }
        return event_type in system_specific_events.get(self.system_type, [])

    async def _process_system_specific_event(
        self, event_type: str, event_data: dict, session: AsyncSession
    ):
        """Process system-specific events."""
        guide_logger.debug(
            f"Processing {self.system_type} specific event: {event_type}"
        )

        if self.system_type == "enhanced_shared":
            await self._process_enhanced_shared_event(event_type, event_data, session)
        elif self.system_type == "multi_agent":
            await self._process_multi_agent_event(event_type, event_data, session)

    async def _process_enhanced_shared_event(
        self, event_type: str, event_data: dict, session: AsyncSession
    ):
        """Process enhanced shared system specific events."""
        if event_type == "memory_loaded":
            guide_logger.info(
                f"Enhanced memory loading: {event_data.get('memory_count', 0)} memories loaded"
            )
        elif event_type == "agent_handoff":
            guide_logger.info(
                f"Agent handoff in shared system: {event_data.get('from_agent')} -> {event_data.get('to_agent')}"
            )

    async def _process_multi_agent_event(
        self, event_type: str, event_data: dict, session: AsyncSession
    ):
        """Process multi-agent system specific events."""
        if event_type == "agent_transfer":
            guide_logger.info(
                f"Multi-agent transfer: {event_data.get('from_agent')} -> {event_data.get('to_agent')}"
            )
        elif event_type == "workflow_isolation":
            guide_logger.info(
                f"Workflow isolated for agent: {event_data.get('agent_name')}"
            )

    async def _is_authenticated_user(self, session: AsyncSession, user_id: str) -> bool:
        """Verifica se o user_id existe na tabela auth.users."""
        try:
            guide_logger.debug("verifying user authenticated", user_id)
            query = text("SELECT EXISTS(SELECT 1 from auth.users WHERE id = :user_id)")
            result = await session.execute(query, {"user_id": user_id})
            exists = result.scalar_one()
            return exists
        except Exception as e:
            guide_logger.debug(f"Error checking authenticated user: {e}")

            return False

    async def _enrich_hits_with_photos(
        self, session: AsyncSession, hits: list[dict]
    ) -> list[dict]:
        """Busca fotos no banco de dados com base nas refs dos hits e as adiciona aos hits."""
        refs = [hit.get("ref") for hit in hits if hit.get("ref")]
        if not refs:
            return hits

        photos = (
            (await session.execute(select(Photo).filter(Photo.ref.in_(refs))))
            .scalars()
            .all()
        )

        photos_by_ref = {}
        for p in photos:
            if p.ref not in photos_by_ref:
                photos_by_ref[p.ref] = []
            photos_by_ref[p.ref].append(
                {
                    "id": str(p.id),
                    "title": p.title,
                    "ref": p.ref,
                    "src": p.src,
                    "seq": p.seq,
                    "featured": p.featured,
                }
            )

        updated_hits = []
        for hit in hits:
            hit_ref = hit.get("ref")
            serializable_photos = photos_by_ref.get(hit_ref, [])
            updated_hits.append({**hit, "photos": serializable_photos})

        return updated_hits

    async def _ensure_user_thread_exists(
        self, session: AsyncSession, user_id_str: str, thread_id_str: str
    ):
        """Checks if a UserThread relationship exists and creates it if not."""
        try:
            user_uuid = UUID(user_id_str)
            thread_uuid = UUID(thread_id_str)
        except ValueError:
            guide_logger.debug(
                f"Error: Invalid UUID format provided for user_id '{user_id_str}' or thread_id '{thread_id_str}'."
            )
            return

        exists_query = select(
            exists().where(
                UserThread.user_id == user_uuid, UserThread.thread_id == thread_uuid
            )
        )
        result = await session.execute(exists_query)
        relationship_exists = result.scalar_one_or_none()

        if not relationship_exists:
            try:
                new_relationship = UserThread(user_id=user_uuid, thread_id=thread_uuid)
                await session.merge(new_relationship)
                await session.commit()
                guide_logger.debug(
                    f"Created UserThread relationship: user_id={user_uuid}, thread_id={thread_uuid}"
                )
            except Exception as e:
                await session.rollback()
                guide_logger.debug(
                    f"Error creating UserThread relationship for user_id={user_uuid}, thread_id={thread_uuid}: {e}"
                )

    async def list_messages(self, session: AsyncSession, thread_id: str, user_id: str):
        await self._ensure_user_thread_exists(session, user_id, thread_id)

        guide_logger.debug(
            f"Listing messages for thread_id: {thread_id}, user_id: {user_id}"
        )
        async with await get_saver() as saver:
            chat_app.checkpointer = saver

            state = await saver.aget({"configurable": {"thread_id": thread_id}})

            if not state:
                return []

            messages = state.get("channel_values").get("messages")

            for message in messages:
                if not isinstance(message, ToolMessage):
                    continue

                if (
                    message.name == "search_properties"
                    or message.name == "deep_search_properties"
                    or message.name == "get_property_by_reference"
                ):
                    try:
                        content_data = json.loads(message.content)
                        hits = content_data.get("hits", [])
                        if hits:
                            updated_hits = await self._enrich_hits_with_photos(
                                session, hits
                            )
                            message.content = json.dumps({"hits": updated_hits})
                    except json.JSONDecodeError:
                        pass

            return messages

    async def stream_chat(
        self,
        session: AsyncSession,
        prompt: str,
        thread_id: str,
        user_id: str,
        background_tasks: BackgroundTasks,
    ) -> AsyncGenerator[str, None]:
        """Streams chat responses using SSE, processing custom graph events emitted via StreamWriter."""

        await self._ensure_user_thread_exists(session, user_id, thread_id)

        guide_logger.debug(
            f"Streaming chat for thread_id: {thread_id}, user_id: {user_id}"
        )
        async with await get_store() as store:
            await store.setup()
            guide_logger.debug("Store setup complete")

            async with await get_saver() as saver:
                await saver.setup()
                guide_logger.debug("Saver setup complete")

                try:
                    agent_system = await self._get_agent_system()

                    if hasattr(agent_system, "checkpointer"):
                        agent_system.checkpointer = saver
                    else:
                        chat_app.checkpointer = saver
                except Exception as e:
                    guide_logger.error(
                        f"Failed to get agent system: {e}. Using fallback."
                    )
                    agent_system = chat_app
                    agent_system.checkpointer = saver

                is_authenticated = await self._is_authenticated_user(session, user_id)
                guide_logger.debug(
                    f"User {user_id} authenticated status: {is_authenticated}"
                )

                if not is_authenticated:
                    state = await saver.aget({"configurable": {"thread_id": thread_id}})

                    if state is None:
                        messages = []
                    else:
                        messages = state.get("channel_values", {}).get("messages", [])

                    message_count = len(messages)
                    guide_logger.debug(
                        f"Temporary user message count for thread {thread_id}: {message_count}"
                    )

                    if message_count >= 30:
                        guide_logger.debug(
                            f"Message limit reached for temporary user {user_id} in thread {thread_id}."
                        )

                        yield json.dumps(
                            {
                                "event": "llm_message",
                                "data": {
                                    "content": "Limite de mensagens atingido! Para continuar sua conversa comigo, por favor realize seu log-in"
                                },
                            }
                        )

                        yield json.dumps(
                            {
                                "event": "tool_end",
                                "data": {
                                    "type": "tool",
                                    "name": "request_login",
                                    "content": {},
                                },
                            }
                        )

                        return

                config: RunnableConfig = {
                    "configurable": {
                        "thread_id": thread_id,
                        "session": session,
                        "user_id": user_id,
                        "system_type": self.system_type,
                        "system_configs": self.config,
                    },
                    "recursion_limit": self.config.get("recursion_limit", 10),
                }

                guide_logger.debug(
                    f"Starting chat stream with {self.system_type} system"
                )

                try:
                    existing_state = await saver.aget(
                        {"configurable": {"thread_id": thread_id}}
                    )
                    if existing_state and existing_state.get("channel_values"):
                        existing_messages = existing_state["channel_values"].get(
                            "messages", []
                        )
                        current_agent = existing_state["channel_values"].get(
                            "current_agent", "Broker"
                        )

                        inputs = {
                            "messages": existing_messages
                            + [HumanMessage(content=prompt)],
                            "current_agent": current_agent,
                        }
                        guide_logger.debug(
                            f"Retrieved existing state - current_agent: {current_agent}, existing_messages: {len(existing_messages)}"
                        )
                    else:
                        inputs = {"messages": [HumanMessage(content=prompt)]}
                        guide_logger.debug(
                            "No existing state found - starting new conversation"
                        )
                except Exception as e:
                    guide_logger.error(f"Error retrieving existing state: {e}")
                    inputs = {"messages": [HumanMessage(content=prompt)]}

                try:
                    agent_system = await self._get_agent_system()
                except Exception as e:
                    guide_logger.error(
                        f"Failed to get agent system for streaming: {e}. Using fallback."
                    )
                    agent_system = chat_app

                try:
                    async for event in agent_system.astream(
                        inputs, config, stream_mode="custom"
                    ):
                        try:
                            custom_event_type = event.get("event")
                            custom_event_data = event.get("data")
                            custom_event_artifact = (
                                custom_event_data.get("artifact")
                                if isinstance(custom_event_data, dict)
                                else None
                            )

                            guide_logger.debug(
                                f"[{self.system_type}] Event: {custom_event_type}"
                            )

                            if self._should_process_event(custom_event_type):
                                await self._process_system_specific_event(
                                    custom_event_type, custom_event_data, session
                                )

                            if not custom_event_type:
                                guide_logger.debug(
                                    f"Warning: Received event without 'event' key: {event}"
                                )
                                continue
                            if custom_event_type == "validate_message_before_tool":
                                yield json.dumps(
                                    {
                                        "event": "validate_message_before_tool",
                                        "data": custom_event_data,
                                    }
                                )
                            elif custom_event_type == "validation_failed":
                                yield json.dumps(
                                    {
                                        "event": "validation_failed",
                                        "data": custom_event_data,
                                    }
                                )
                            elif custom_event_type == "suggestions":
                                yield json.dumps(
                                    {"event": "suggestions", "data": custom_event_data}
                                )
                            elif custom_event_type == "tool_start":
                                yield json.dumps(
                                    {"event": "tool_start", "data": custom_event_data}
                                )
                            elif custom_event_type == "tool_end":
                                tool_name = custom_event_data.get("name")
                                output_content = custom_event_data.get("output")

                                try:
                                    output_parsed = (
                                        json.loads(output_content)
                                        if isinstance(output_content, str)
                                        else output_content
                                    )
                                except (json.JSONDecodeError, TypeError):
                                    output_parsed = output_content

                                if isinstance(output_parsed, dict):
                                    original_hits = output_parsed.get("hits", [])
                                    if original_hits and (
                                        tool_name == "search_properties"
                                        or tool_name == "deep_search_properties"
                                        or tool_name == "get_property_by_reference"
                                    ):
                                        output_parsed[
                                            "hits"
                                        ] = await self._enrich_hits_with_photos(
                                            session, original_hits
                                        )

                                yield json.dumps(
                                    {
                                        "event": "tool_end",
                                        "data": {
                                            "type": "tool",
                                            "name": tool_name,
                                            "content": output_parsed,
                                            "artifact": custom_event_artifact,
                                        },
                                    }
                                )
                            elif custom_event_type == "llm_message":
                                yield json.dumps(
                                    {"event": "llm_message", "data": custom_event_data}
                                )

                            else:
                                guide_logger.warning(
                                    f"Warning: Received unknown custom event type: {custom_event_type}"
                                )

                        except Exception as e:
                            error_message = f"Error processing custom SSE event '{event.get('event', 'N/A')}' in {self.system_type}: {e}"
                            guide_logger.error(error_message)
                            try:
                                yield json.dumps(
                                    {
                                        "event": "error",
                                        "data": {
                                            "message": error_message,
                                            "failed_event_type": event.get(
                                                "event", "N/A"
                                            ),
                                            "failed_event_name": event.get("name"),
                                            "system_type": self.system_type,
                                        },
                                    }
                                )
                            except Exception as dump_err:
                                guide_logger.error(
                                    f"Failed to dump error event to SSE: {dump_err}"
                                )

                except Exception as system_error:
                    error_message = (
                        f"Critical error in {self.system_type} system: {system_error}"
                    )
                    guide_logger.error(error_message)
                    yield json.dumps(
                        {
                            "event": "system_error",
                            "data": {
                                "message": error_message,
                                "system_type": self.system_type,
                            },
                        }
                    )

                # Verify graph execution completed and state should be persisted automatically
                try:
                    final_state = await saver.aget(
                        {"configurable": {"thread_id": thread_id}}
                    )
                    if final_state:
                        final_current_agent = final_state.get("channel_values", {}).get(
                            "current_agent", "Unknown"
                        )
                        guide_logger.info(
                            f"Graph execution completed. Final current_agent in state: {final_current_agent} for thread {thread_id}"
                        )
                    else:
                        guide_logger.warning(
                            f"No final state found after graph execution for thread {thread_id}"
                        )
                except Exception as e:
                    guide_logger.error(
                        f"Error checking final state after graph execution for thread {thread_id}: {e}"
                    )

        if self.system_type == "enhanced_shared":
            background_tasks.add_task(
                self._handle_background_memory_processing,
                thread_id,
                user_id,
                self.system_type,
            )

    async def _handle_background_memory_processing(
        self, thread_id: str, user_id: str, system_type: str
    ):
        """Handle background memory processing with a new saver instance."""
        if self.config.get("enable_memory_processing", True):
            try:
                async with await get_saver() as bg_saver:
                    await bg_saver.setup()

                    latest_state = await bg_saver.aget(
                        {"configurable": {"thread_id": thread_id}}
                    )
                    if latest_state:
                        channel_values = latest_state.get("channel_values", {})
                        state_messages = channel_values.get("messages", [])

                        guide_logger.info(
                            f"Processing background memory for {system_type} system - "
                            f"Thread: {thread_id}, User: {user_id}, Messages: {len(state_messages)}"
                        )

                        background_config = {
                            "configurable": {
                                "thread_id": thread_id,
                                "user_id": user_id,
                                "system_type": system_type,
                            },
                            "recursion_limit": self.config.get("recursion_limit", 15),
                        }

                        filtered_messages = []
                        for msg in state_messages[-6:]:
                            if isinstance(msg, HumanMessage):
                                filtered_messages.append(msg)
                            elif isinstance(msg, AIMessage) and not getattr(
                                msg, "tool_calls", None
                            ):
                                filtered_messages.append(msg)

                        background_state = {
                            "messages": filtered_messages[-4:],
                            "user_id": user_id,
                        }

                        await safe_background_memory_processing(
                            background_state,
                            background_config,
                            system_type,
                        )
                    else:
                        guide_logger.debug(
                            "Could not retrieve latest state for background memory processing."
                        )
            except Exception as e:
                guide_logger.error(
                    f"Error in background memory processing for {system_type} - "
                    f"Thread: {thread_id}, User: {user_id}: {e}"
                )

    async def list_chats(self, session: AsyncSession, user_id: str):
        """Lists all chat threads associated with a user with additional metadata."""
        user_uuid = UUID(user_id)

        query = select(UserThread).where(UserThread.user_id == user_uuid)
        result = await session.execute(query)
        user_threads = result.scalars().all()

        chat_threads = []

        async with await get_saver() as saver:
            for thread in user_threads:
                chat_app.checkpointer = saver
                try:
                    state = await saver.aget(
                        {"configurable": {"thread_id": str(thread.thread_id)}}
                    )
                except Exception:
                    continue

                last_message = None

                if state:
                    messages = state.get("channel_values", {}).get("messages", [])

                    for message in reversed(messages):
                        if not isinstance(message, ToolMessage):
                            last_message = (
                                message.content
                                if hasattr(message, "content")
                                else str(message)
                            )
                            break

                thread_data = {
                    "thread_id": str(thread.thread_id),
                    "startTime": thread.created_at.isoformat()
                    if thread.created_at
                    else None,
                    "preview": last_message,
                }
                chat_threads.append(thread_data)

        return chat_threads

    async def change_id(
        self, session: AsyncSession, user_id: str, user_identifier: str
    ):
        """Changes the user_id of a user and updates all related foreign key references."""
        user_uuid = UUID(user_id)
        new_uuid = UUID(user_identifier)

        current_user = (
            await session.execute(
                text("select id from auth.users where id = :user_id"),
                {"user_id": user_identifier},
            )
        ).fetchone()

        if current_user:
            return JSONResponse(
                content={"message": "I can't accept it"}, status_code=409
            )

        await session.execute(
            text("UPDATE auth.users SET id = :user_identifier WHERE id = :user_id"),
            {"user_id": user_uuid, "user_identifier": new_uuid},
        )

    async def delete_thread(self, session: AsyncSession, user_id: str, thread_id: str):
        thread = (
            await session.execute(
                text(
                    "select * from relationships.user_threads where user_id = (:user_id)::uuid and thread_id = (:thread_id)::uuid"
                ).bindparams(user_id=user_id, thread_id=thread_id)
            )
        ).scalar_one_or_none()

        if not thread:
            return JSONResponse(status_code=404, content={"detail": "Thread not found"})

        await session.execute(
            text(
                "delete from relationships.user_threads where user_id = (:user_id)::uuid and thread_id = (:thread_id)::uuid"
            ).bindparams(user_id=user_id, thread_id=thread_id)
        )
        await session.execute(
            text(
                "delete from public.checkpoints where thread_id = :thread_id"
            ).bindparams(thread_id=thread_id)
        )
        await session.execute(
            text(
                "delete from public.checkpoint_writes where thread_id = :thread_id"
            ).bindparams(thread_id=thread_id)
        )
        await session.execute(
            text(
                "delete from public.checkpoint_blobs where thread_id = :thread_id"
            ).bindparams(thread_id=thread_id)
        )
        return True


"""
COMPREHENSIVE USAGE EXAMPLES AND DOCUMENTATION

The ChatService now supports three different agent system architectures:

1. Legacy System (Original)
2. Enhanced Shared System (Recommended)
3. Multi-Agent System (Advanced)

=== USAGE EXAMPLES ===


chat_service = ChatService()

chat_service = ChatService(system_type="enhanced_shared")


legacy_service = ChatService(system_type="legacy")

legacy_service = create_legacy_chat_service()


enhanced_service = create_enhanced_chat_service()


multi_agent_service = create_multi_agent_chat_service()


custom_service = ChatService.create_with_config(
    system_type="multi_agent",
    recursion_limit=25,
    enable_suggestions=True,
    agent_isolation=True
)


chat_service = ChatService()
await chat_service.switch_system("multi_agent")


chat_service.configure_system(
    recursion_limit=15,
    enable_memory_processing=True
)

=== SYSTEM COMPARISONS ===

Legacy System:
- Original MBRAS chat functionality
- Basic agent routing
- Standard memory processing
- Best for: Backward compatibility

Enhanced Shared System (RECOMMENDED):
- Improved memory management
- Enhanced validation and suggestions
- Better error handling
- Partner agent handoffs
- Best for: Production MBRAS deployment

Multi-Agent System:
- Isolated agent workflows
- Automatic handoff routing
- Independent scaling capabilities
- Advanced fault tolerance
- Best for: High-scale, specialized deployments

=== SYSTEM SWITCHING EXAMPLES ===


chat_service = create_enhanced_chat_service()


if high_load_detected:
    await chat_service.switch_system("multi_agent")


if load_normalized:
    await chat_service.switch_system("enhanced_shared")

=== CONFIGURATION OPTIONS ===

Legacy System Config:
- recursion_limit: Maximum recursion depth (default: 10)
- enable_memory_processing: Enable background memory processing (default: True)
- enable_suggestions: Enable suggestion generation (default: False)

Enhanced Shared System Config:
- recursion_limit: Maximum recursion depth (default: 15)
- enable_memory_processing: Enable background memory processing (default: True)
- enable_suggestions: Enable suggestion generation (default: True)
- enhanced_validation: Enhanced response validation (default: True)

Multi-Agent System Config:
- recursion_limit: Maximum recursion depth (default: 20)
- enable_memory_processing: Enable background memory processing (default: True)
- enable_suggestions: Enable suggestion generation (default: True)
- agent_isolation: Enable agent workflow isolation (default: True)
- auto_handoffs: Enable automatic agent handoffs (default: True)

=== MONITORING AND DEBUGGING ===


service = ChatService()
info = service.get_system_info()
print(f"Current system: {info['system_type']}")
print(f"Available systems: {info['available_systems']}")


current_type = service.get_current_system_type()
print(f"Active system: {current_type}")






=== INTEGRATION WITH EXISTING CODE ===






chat_service = create_enhanced_chat_service()

chat_service = create_multi_agent_chat_service()

chat_service = create_legacy_chat_service()


async with session_manager() as session:
    async for chunk in chat_service.stream_chat(
        session, prompt, thread_id, user_id, background_tasks
    ):
        yield chunk

=== PERFORMANCE CONSIDERATIONS ===

System Performance Characteristics:

Legacy System:
- Memory Usage: Low
- CPU Usage: Low
- Latency: Medium
- Throughput: Medium
- Best for: Small to medium deployments

Enhanced Shared System:
- Memory Usage: Medium
- CPU Usage: Medium
- Latency: Low
- Throughput: High
- Best for: Production deployments

Multi-Agent System:
- Memory Usage: High (isolated agents)
- CPU Usage: Variable (per agent)
- Latency: Variable (handoff overhead)
- Throughput: Very High (parallel processing)
- Best for: High-scale, specialized deployments

=== MIGRATION GUIDE ===

From Legacy to Enhanced Shared:
1. Replace ChatService() with create_enhanced_chat_service()
2. Test suggestion generation and enhanced validation
3. Monitor memory usage (slight increase expected)
4. Verify handoff functionality works as expected

From Enhanced Shared to Multi-Agent:
1. Replace with create_multi_agent_chat_service()
2. Test agent isolation and handoffs
3. Monitor resource usage (increase expected)
4. Verify fault tolerance improvements

=== TROUBLESHOOTING ===

Common Issues:

1. System not switching:
   - Ensure await chat_service.switch_system() is called
   - Check logs for system initialization errors

2. Events not processing:
   - Verify system_type matches expected events
   - Check _should_process_event() method logic

3. Performance degradation:
   - Monitor recursion_limit settings
   - Check memory_processing configuration
   - Consider system type appropriateness

4. Agent handoffs failing:
   - Verify partner configurations in agent decorators
   - Check network connectivity for multi-agent systems
   - Review handoff event logs

=== BEST PRACTICES ===

1. Use Enhanced Shared System for most production deployments
2. Reserve Multi-Agent System for high-scale or specialized needs
3. Monitor system performance and switch as needed
4. Configure recursion_limit based on conversation complexity
5. Enable memory_processing for better user experience
6. Use system-specific events for monitoring and debugging
7. Test system switching in staging environment first
8. Keep configuration simple unless specific needs require customization

For more information, see the Smart Agent System documentation.
"""
