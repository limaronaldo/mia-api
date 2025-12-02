import json
import os
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any, List, Literal, Optional, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated


class ContactInfo(BaseModel):
    email: Optional[str] = Field(None, description="Email address.")
    phone: Optional[str] = Field(None, description="Phone number.")

    @classmethod
    def _parse_dict_field(cls, value):
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
        return value

    @field_validator("*", mode="before")
    def parse_dict_fields(cls, v):
        return cls._parse_dict_field(v)


class Budget(BaseModel):
    min: Optional[float] = Field(None, description="Minimum budget.")
    max: Optional[float] = Field(None, description="Maximum budget.")
    currency: Optional[str] = Field(None, description="Currency (e.g., BRL, USD, EUR).")

    @classmethod
    def _parse_dict_field(cls, value):
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
        return value

    @field_validator("*", mode="before")
    def parse_dict_fields(cls, v):
        return cls._parse_dict_field(v)


class ConversationPreferences(BaseModel):
    styles: Optional[List[str]] = Field(
        default_factory=list,
        description="Preferred conversation styles (e.g., formal, casual, concise).",
    )
    topics_to_avoid: Optional[List[str]] = Field(
        default_factory=list, description="Topics the customer prefers not to discuss."
    )

    @classmethod
    def _parse_list_field(cls, value):
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return value

    @field_validator("styles", "topics_to_avoid", mode="before")
    def parse_list_fields(cls, v):
        return cls._parse_list_field(v)


class UserMemoryModel(BaseModel):
    full_name: Optional[str] = Field(None, description="The customer's full name.")
    contact_info: Optional[ContactInfo | str] = Field(
        default_factory=ContactInfo, description="Contact details for the customer."
    )
    preferred_contact_method: Optional[str] = Field(
        None,
        description="How the customer prefers to be contacted (e.g., email, phone, text).",
    )
    age: Optional[int] = Field(None, description="The customer's age in years.")
    pronouns: Optional[str] = Field(
        None, description="The customer's preferred pronouns."
    )
    location: Optional[str] = Field(
        None, description="The customer's current city, hometown, or region."
    )
    occupation: Optional[str] = Field(
        None, description="The customer's current occupation or field of work."
    )
    budget: Optional[Budget | str] = Field(
        default_factory=Budget,
        description="The customer's budget range for real estate purchases or rentals.",
    )
    property_type_preferences: Optional[List[str] | str] = Field(
        default_factory=list,
        description="Preferred types of properties (e.g., apartment, house, condo, commercial).",
    )
    location_preferences: Optional[List[str] | str] = Field(
        default_factory=list, description="Preferred neighborhoods, cities, or regions."
    )
    move_in_timeframe: Optional[str] = Field(
        None,
        description="Desired timeframe for moving (e.g., immediately, within 3 months).",
    )
    must_have_features: Optional[List[str] | str] = Field(
        default_factory=list,
        description="Essential features or amenities (e.g., parking, balcony, pet-friendly).",
    )
    dealbreakers: Optional[List[str] | str] = Field(
        default_factory=list,
        description="Features or conditions that are unacceptable to the customer.",
    )
    goals: Optional[List[str] | str] = Field(
        default_factory=list,
        description="Short- or long-term real estate goals (e.g., investment, first home, downsizing).",
    )
    conversation_preferences: Optional[ConversationPreferences | str] = Field(
        default_factory=ConversationPreferences,
        description="Customer's preferences for conversation, including style and sensitive topics.",
    )

    @field_validator(
        "contact_info",
        "property_type_preferences",
        "location_preferences",
        "must_have_features",
        "dealbreakers",
        "goals",
        "conversation_preferences",
        mode="before",
    )
    def _parse_stringified_json(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return v

    class Config:
        extra = "ignore"


class PropertyInteractionMemoryModel(BaseModel):
    timestamp: Optional[datetime | str] = Field(
        default_factory=datetime.now,
        description="The date and time of the interaction.",
    )
    property_ref: str = Field(..., description="Unique identifier for the property.")
    interaction_type: str = Field(
        ...,
        description="Type of interaction (e.g., viewed online, scheduled tour, made offer).",
    )
    customer_feedback: Optional[str] = Field(
        None, description="Customer's feedback or comments about the property."
    )
    agent_notes: Optional[str] = Field(
        None, description="Additional notes from the agent or system."
    )

    class Config:
        extra = "ignore"


class GeneralMemoryModel(BaseModel):
    timestamp: Optional[datetime | str] = Field(
        default_factory=datetime.now,
        description="The date and time when this memory was recorded or shared.",
    )
    context: str = Field(
        ...,
        description="The situation, conversation, or circumstance where this memory is relevant. Include any caveats, conditions, or meta-information that help interpret the memory.",
    )
    content: str = Field(
        ...,
        description="The specific information, preference, or event being remembered.",
    )
    source: Optional[str] = Field(
        None,
        description="Where or how this memory was obtained (e.g., direct conversation, observation).",
    )

    class Config:
        extra = "ignore"


@dataclass(kw_only=True)
class MemoryConfig:
    """Configuration for memory-related operations."""

    name: str
    """This tells the model how to reference the function and organizes related memories within the namespace."""
    description: str
    """Description for what this memory type is intended to capture."""

    parameters: Type[BaseModel]
    """The Pydantic model defining the structure of the memory document to manage."""
    system_prompt: str = ""
    """The system prompt to use for the memory assistant."""
    update_mode: Literal["patch", "insert"] = field(default="patch")
    """Whether to continuously patch the memory, or treat each new generation as a new memory."""


@dataclass(kw_only=True)
class Configuration:
    """Main configuration class for the memory graph system."""

    user_id: str = "default"
    """The ID of the user to remember in the conversation."""
    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="anthropic/claude-3-5-sonnet-20240620",
        metadata={
            "description": "The name of the language model to use for the agent. "
            "Should be in the form: provider/model-name."
        },
    )
    """The model to use for generating memories. """
    memory_types: list[MemoryConfig] = field(default_factory=list)
    """The memory_types for the memory assistant."""

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }

        if values.get("memory_types") is None:
            values["memory_types"] = [mc for mc in DEFAULT_MEMORY_CONFIGS]
        else:
            raw_mem_types = values["memory_types"] or []
            parsed_mem_types = []

            model_map = {m.name: m.parameters for m in DEFAULT_MEMORY_CONFIGS}
            for mt_config in raw_mem_types:
                if isinstance(mt_config, dict):
                    if isinstance(mt_config.get("parameters"), str):
                        model_name = mt_config["parameters"]
                        if model_name in model_map:
                            mt_config["parameters"] = model_map[model_name]
                        else:
                            raise ValueError(f"Unknown memory model name: {model_name}")
                    elif not isinstance(mt_config.get("parameters"), type):
                        raise TypeError(
                            f"Expected 'parameters' to be a Pydantic model type or known name string, got {type(mt_config.get('parameters'))}"
                        )

                    try:
                        parsed_mem_types.append(MemoryConfig(**mt_config))
                    except Exception as e:
                        print(f"Error parsing memory config: {mt_config}. Error: {e}")

                        raise
                elif isinstance(mt_config, MemoryConfig):
                    parsed_mem_types.append(mt_config)
                else:
                    raise TypeError(
                        f"Unexpected type for memory_type configuration: {type(mt_config)}"
                    )
            values["memory_types"] = parsed_mem_types

        init_values = {k: v for k, v in values.items() if v is not None}
        return cls(**init_values)


DEFAULT_MEMORY_CONFIGS = [
    MemoryConfig(
        name="User",
        description=(
            "Maintain a comprehensive, up-to-date profile of the real estate customer, "
            "including personal details, preferences, and relevant background information. "
            "This memory is continuously patched to reflect the latest known state."
        ),
        update_mode="patch",
        parameters=UserMemoryModel,
    ),
    MemoryConfig(
        name="PropertyInteraction",
        description=(
            "Track each property the customer has shown interest in, inquired about, or visited. "
            "Each entry is inserted as a new memory, preserving the full history for later recall."
        ),
        update_mode="insert",
        parameters=PropertyInteractionMemoryModel,
    ),
    MemoryConfig(
        name="GeneralMemory",
        description=(
            "Store significant events, preferences, or facts the customer has shared that are not directly related to real estate. "
            "Each entry is inserted as a new memory, preserving the full history for later recall."
        ),
        update_mode="insert",
        parameters=GeneralMemoryModel,
    ),
]
