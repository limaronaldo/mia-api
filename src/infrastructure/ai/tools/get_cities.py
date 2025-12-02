from langchain_community.tools import tool
from langchain_core.runnables.config import RunnableConfig
from sqlalchemy import select

from src.infrastructure.models.public import DBProperty


@tool
async def get_cities(config: RunnableConfig):
    """Get all cities avaiable in MBRAS."""
    session = config.get("configurable", {}).get("session")

    cities = (
        (await session.execute(select(DBProperty.city).distinct(DBProperty.city)))
        .scalars()
        .all()
    )

    return cities
