import asyncio
import json
import logging
import uuid
from typing import Any, Dict, Type

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, ValidationError
from trustcall import create_extractor

from src.infrastructure.ai.graphs.chat.configuration import Configuration
from src.infrastructure.ai.graphs.chat.state import State
from src.infrastructure.ai.graphs.chat.utils import get_store, prepare_messages
from src.infrastructure.ai.models.gemini import gemini_2_5_flash
from src.infrastructure.ai.utils import log_token_consumption
from src.infrastructure.lib.logger import guide_logger


def ensure_json_serializable(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: ensure_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [ensure_json_serializable(item) for item in data]
    elif hasattr(data, "model_dump"):
        return ensure_json_serializable(data.model_dump(mode="json"))
    elif hasattr(data, "dict"):
        return ensure_json_serializable(data.dict())
    elif isinstance(data, BaseMessage):
        return str(data.content)
    else:
        return data


def sanitize_extracted_data(data: Any) -> Any:
    """Sanitize extracted data to ensure proper string conversion for validation."""
    if isinstance(data, dict):
        sanitized_dict = {}
        for k, v in data.items():
            # Convert None values to None (keep as is)
            if v is None:
                sanitized_dict[k] = None
            # Special handling for contact_info field based on the error
            elif k == "contact_info" and isinstance(v, (int, float)):
                sanitized_dict[k] = str(v)
            else:
                sanitized_dict[k] = sanitize_extracted_data(v)
        return sanitized_dict
    elif isinstance(data, list):
        return [sanitize_extracted_data(item) for item in data]
    elif data is None:
        return None
    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        # Convert numeric values to strings, which is often what pydantic expects for contact info
        return str(data)
    else:
        return data


async def handle_patch_memory(
    state: State,
    config: RunnableConfig,
) -> dict:
    """Extract the user's state from the conversation and update the memory."""

    async with await get_store() as store:
        configurable = Configuration.from_runnable_config(config)

        memory_config = next(
            conf
            for conf in configurable.memory_types
            if conf.name == state.get("function_name")
        )

        namespace = (configurable.user_id, "user_states")
        existing_item = await store.aget(namespace, memory_config.name)
        existing = {memory_config.name: existing_item.value} if existing_item else None

        extractor = create_extractor(
            gemini_2_5_flash,
            tools=[
                {
                    "name": memory_config.name,
                    "description": memory_config.description,
                    "parameters": memory_config.parameters.model_json_schema(),
                }
            ],
            tool_choice="any",
        )

        prepared_messages = prepare_messages(
            state.get("messages"), memory_config.system_prompt
        )

        inputs = {"messages": prepared_messages, "existing": existing}
        result = await extractor.ainvoke(inputs, config)

        # Log token consumption for patch memory extraction
        log_token_consumption("memory_patch_extractor", result, len(prepared_messages))

        if result and result.get("responses"):
            logging.info(
                f"Extractor returned responses for patch memory {memory_config.name}: {result['responses']}"
            )
            raw_extracted_data = result["responses"][0].model_dump(mode="json")

            # First, attempt validation on raw data
            memory_model: Type[BaseModel] = memory_config.parameters

            try:
                validated_data = memory_model.model_validate(raw_extracted_data)
                guide_logger.info(
                    f"Successfully validated raw data for patch memory '{memory_config.name}' using {memory_model.__name__}"
                )
                await store.aput(
                    namespace,
                    memory_config.name,
                    validated_data.model_dump(mode="json"),
                )
            except ValidationError:
                # Raw data validation failed, try with sanitized data
                guide_logger.debug(
                    f"Raw data validation failed for patch memory '{memory_config.name}', trying sanitized data"
                )

                # Sanitize the extracted data to handle type conversion issues
                sanitized_data = sanitize_extracted_data(raw_extracted_data)

                try:
                    validated_data = memory_model.model_validate(sanitized_data)

                    guide_logger.info(
                        f"Successfully validated sanitized data for patch memory '{memory_config.name}' using {memory_model.__name__}"
                    )

                    await store.aput(
                        namespace,
                        memory_config.name,
                        validated_data.model_dump(mode="json"),
                    )
                except ValidationError as e:
                    guide_logger.error(
                        f"Validation failed for patch memory '{memory_config.name}' using {memory_model.__name__}. "
                        f"Original data: {raw_extracted_data}. Sanitized data: {sanitized_data}. Errors: {e.errors()}"
                    )

                    await store.aput(namespace, memory_config.name, sanitized_data)
                except Exception as e:
                    guide_logger.error(
                        f"Unexpected error during patch memory processing for '{memory_config.name}': {e}"
                    )

                    await store.aput(namespace, memory_config.name, sanitized_data)
            except Exception as e:
                guide_logger.error(
                    f"Unexpected error during patch memory processing for '{memory_config.name}': {e}"
                )
                # Fallback to sanitized data
                sanitized_data = sanitize_extracted_data(raw_extracted_data)
                await store.aput(namespace, memory_config.name, sanitized_data)
        else:
            guide_logger.warning(
                f"Extractor returned no responses for patch memory {memory_config.name}"
            )


async def handle_insertion_memory(
    state: State,
    config: RunnableConfig,
) -> dict[str, list]:
    """Handle insertion memory events."""

    async with await get_store() as store:
        configurable = Configuration.from_runnable_config(config)

        memory_config = next(
            conf
            for conf in configurable.memory_types
            if conf.name == state.get("function_name")
        )

        namespace = (
            configurable.user_id,
            "events",
            memory_config.name,
        )

        query = "\n".join(str(message.content) for message in state.get("messages"))[
            -3000:
        ]

        existing_items = await store.asearch(namespace, query=query, limit=5)

        extractor = create_extractor(
            gemini_2_5_flash,
            tools=[
                {
                    "name": memory_config.name,
                    "description": memory_config.description,
                    "parameters": memory_config.parameters.model_json_schema(),
                }
            ],
            tool_choice="any",
            enable_inserts=True,
        )

        prepared_messages_for_insertion = prepare_messages(
            state.get("messages"), memory_config.system_prompt
        )

        extracted = await extractor.ainvoke(
            {
                "messages": prepared_messages_for_insertion,
                "existing": (
                    [
                        (
                            existing_item.key,
                            memory_config.name,
                            existing_item.value,
                        )
                        for existing_item in existing_items
                    ]
                    if existing_items
                    else None
                ),
            },
            config,
        )

        # Log token consumption for insertion memory extraction
        log_token_consumption(
            "memory_insertion_extractor",
            extracted,
            len(prepared_messages_for_insertion),
        )

        if extracted and extracted.get("responses"):
            logging.info(
                f"Extractor returned responses for insertion memory {memory_config.name}: {extracted['responses']}"
            )

            processed_responses_to_save = []
            memory_model: Type[BaseModel] = memory_config.parameters

            for r, rmeta in zip(extracted["responses"], extracted["response_metadata"]):
                raw_extracted_data = r.model_dump(mode="json")
                doc_id = str(rmeta.get("json_doc_id", uuid.uuid4()))

                # First, attempt validation on raw data
                validation_succeeded = False

                try:
                    validated_data = memory_model.model_validate(raw_extracted_data)
                    guide_logger.info(
                        f"Successfully validated raw data for insertion memory '{memory_config.name}' (ID: {doc_id}) using {memory_model.__name__}"
                    )
                    new_memory_content = validated_data.model_dump(mode="json")
                    validation_succeeded = True
                except ValidationError:
                    # Raw data validation failed, try with sanitized data
                    guide_logger.debug(
                        f"Raw data validation failed for insertion memory '{memory_config.name}' (ID: {doc_id}), trying sanitized data"
                    )

                    # Sanitize the extracted data to handle type conversion issues
                    sanitized_data = sanitize_extracted_data(raw_extracted_data)

                    try:
                        validated_data = memory_model.model_validate(sanitized_data)
                        guide_logger.info(
                            f"Successfully validated sanitized data for insertion memory '{memory_config.name}' (ID: {doc_id}) using {memory_model.__name__}"
                        )
                        new_memory_content = validated_data.model_dump(mode="json")
                        validation_succeeded = True
                    except ValidationError as e:
                        guide_logger.error(
                            f"Validation failed for insertion memory '{memory_config.name}' (ID: {doc_id}) using {memory_model.__name__}. "
                            f"Original data: {raw_extracted_data}. Sanitized data: {sanitized_data}. Errors: {e.errors()}"
                        )
                        new_memory_content = sanitized_data
                    except Exception as e:
                        guide_logger.error(
                            f"Unexpected error during insertion memory processing for '{memory_config.name}' (ID: {doc_id}): {e}"
                        )
                        new_memory_content = sanitized_data
                except Exception as e:
                    guide_logger.error(
                        f"Unexpected error during insertion memory processing for '{memory_config.name}' (ID: {doc_id}): {e}"
                    )
                    # Fallback to sanitized data
                    sanitized_data = sanitize_extracted_data(raw_extracted_data)
                    new_memory_content = sanitized_data

                # Only perform similarity check if validation succeeded
                if validation_succeeded:
                    try:
                        query_string = json.dumps(new_memory_content)

                        search_results = await store.asearch(
                            namespace, query=query_string, limit=5
                        )
                        similar_memory_found = False
                        if search_results:
                            for result in search_results:
                                score = getattr(result, "score", None)
                                if score is not None and score >= 0.75:
                                    similar_memory_found = True
                                    guide_logger.info(
                                        f"Similar memory detected via search for type '{memory_config.name}' (New ID: {doc_id}) with score {score:.4f}. Skipping insertion."
                                    )
                                    break

                        if similar_memory_found:
                            continue
                        else:
                            guide_logger.debug(
                                f"No similar memory found for {doc_id}. Proceeding with insertion."
                            )
                            processed_responses_to_save.append(
                                (namespace, doc_id, new_memory_content)
                            )

                    except Exception as search_err:
                        guide_logger.error(
                            f"Error during semantic search for {doc_id}: {search_err}. Proceeding with insertion."
                        )
                        processed_responses_to_save.append(
                            (namespace, doc_id, new_memory_content)
                        )
                else:
                    # If validation failed, still save the data but skip similarity check
                    processed_responses_to_save.append(
                        (namespace, doc_id, new_memory_content)
                    )

            if processed_responses_to_save:
                guide_logger.info(
                    f"Attempting to save {len(processed_responses_to_save)} new/updated memories for type '{memory_config.name}'."
                )
                await asyncio.gather(
                    *(
                        store.aput(ns, d_id, data)
                        for ns, d_id, data in processed_responses_to_save
                    )
                )
            else:
                guide_logger.info(
                    f"No new memories to save for type '{memory_config.name}' in this batch (either none extracted or all were duplicates/errors)."
                )
        else:
            guide_logger.warning(
                f"Extractor returned no responses for insertion memory {memory_config.name}"
            )
        return {}


async def process_memory_step(
    state: State, config: RunnableConfig, saver: Any = None
) -> Dict[str, Any]:
    """Process memories for different schemas in background tasks."""
    user_id = state.get("user_id")
    messages = state.get("messages")[-4:]

    guide_logger.debug("---STARTING MEMORY PROCESSING---")

    tasks = []

    configurable = Configuration.from_runnable_config(config)

    for schema in configurable.memory_types:
        guide_logger.debug(
            f"---HANDLING MEMORY PROCESSING for user {user_id} and type {schema.name}---"
        )

        processor_state = State(
            messages=messages,
            function_name=schema.name,
        )

        if schema.update_mode == "patch":
            task = asyncio.create_task(handle_patch_memory(processor_state, config))
            tasks.append(task)
        elif schema.update_mode == "insert":
            task = asyncio.create_task(handle_insertion_memory(processor_state, config))
            tasks.append(task)
        else:
            guide_logger.warning(
                f"Warning: Unknown update mode '{schema.update_mode}' for schema '{schema.name}'. Skipping."
            )

    if tasks:
        await asyncio.gather(*tasks)

    guide_logger.debug("---FINISHED MEMORY PROCESSING---")

    return {}
