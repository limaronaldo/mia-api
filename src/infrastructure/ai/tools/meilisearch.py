from langchain_community.tools import tool
from unidecode import unidecode

from src.infrastructure.config.meilisearch import meilisearch_client


@tool
async def deep_search_properties(query: str):
    """
    Perform a deep semantic search for properties using natural language queries.
    Use this tool when the user provides broad or general requirements, such as
    "properties near a specific neighborhood" or "houses with a swimming pool".

    Args:
        query (str): The user's natural language query describing desired property features.

    Returns:
        list[dict]: A list of properties matching the semantic intent of the query.
    """

    try:
        results = meilisearch_client.index("immobiles").search(
            query,
            {
                "limit": 6,
                "hybrid": {"semanticRatio": 1, "embedder": "openai"},
                "filter": 'active = "true"',
                "attributesToRetrieve": [
                    "id",
                    "ref",
                    "title",
                    "new_title",
                    "description",
                    "promotion",
                    "sale_value",
                    "rent_value",
                    "neighborhood",
                    "commercial_neighborhood",
                    "city",
                    "state",
                    "suites",
                    "parking_spaces",
                    "total_area",
                    "usable_area",
                    "property_type",
                    "features",
                    "bedrooms",
                    "bathrooms",
                    "value",
                ],
                "rankingScoreThreshold": 0.35,
            },
        )
    except Exception as e:
        print(e)
        return {"hits": [], "total_hits_without_trim": 0}

    return results


@tool
async def search_iptus(query: str) -> list[dict]:
    """Search for iptus using natural language queries.

    Args:
        query (str): The query to search for iptus.

    Returns:
        list[dict]: A list of iptus that match the query.
    """

    results = meilisearch_client.index("iptus").search(
        query,
        {
            "limit": 6,
            # "hybrid": {"semanticRatio": 1, "embedder": "openai"},
        },
    )

    return results


@tool
async def search_transactions(query: str) -> list[dict]:
    """Search for transactions using natural language queries.

    Args:
        query (str): The query to search for transactions.

    Returns:
        list[dict]: A list of transactions that match the query.
    """

    query = unidecode(query)

    results = meilisearch_client.index("iptus").search(
        unidecode(query),
        {
            "limit": 6,
            # "hybrid": {"semanticRatio": 1, "embedder": "openai"},
            "rankingScoreThreshold": 0.5,
        },
    )

    transactions = meilisearch_client.index("transactions").search(
        "",
        {
            "limit": 6,
            "filter": f"contributor_number IN [{','.join(f"'{iptu['contributor_number']}'" for iptu in results['hits'])}]",
            "rankingScoreThreshold": 1,
        },
    )

    return transactions
