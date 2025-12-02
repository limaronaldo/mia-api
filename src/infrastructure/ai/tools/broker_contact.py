from langchain_community.tools import tool
from langchain_core.runnables.config import RunnableConfig

from src.infrastructure.lib.logger import guide_logger
from src.infrastructure.models.public import UserInterest


@tool
async def suggest_broker_contact(
    user_self_presentation_message: str, property_reference: str, config: RunnableConfig
):
    """
    Suggests the user contact the broker for a specific property.
    Use this when the user shows interest in a property.
    This tool will return the broker contact related to property_reference, not any broker.

    Args:
        user_self_presentation_message (str): A detailed user's self message indicating interest in the property. Here you should talk as the user, explaining its interests in the property.
        property_reference (str): The reference of the property the user is interested in.
    """
    # In a real application, this might trigger an event or API call to the UI
    guide_logger.info(
        f"Broker contact suggestion triggered for property: {property_reference}"
    )

    try:
        session = config.get("configurable").get("session")
        user_id = config.get("configurable").get("user_id")

        new_interest = UserInterest()
        new_interest.user_id = user_id
        new_interest.type = "property"
        new_interest.reference = property_reference

        session.add(new_interest)
        await session.commit()

        return {
            "message": user_self_presentation_message,
            "ref": property_reference,
            "phone": "5511988373606",
        }
    except Exception as e:
        print(e)
        raise e
