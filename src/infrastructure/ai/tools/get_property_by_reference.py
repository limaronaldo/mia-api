from langchain_community.tools import tool

from src.infrastructure.config.meilisearch import meilisearch_client


@tool
def get_property_by_reference(reference: str):
    """Get a property by its reference.
    Args:
        ref (str): The reference of the property.
    Returns:
        dict: The property.
    """
    response = meilisearch_client.index("immobiles").search(
        "", {"filter": f'ref = "{reference}"'}
    )

    return response
