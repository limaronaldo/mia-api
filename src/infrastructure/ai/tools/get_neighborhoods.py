from langchain_community.tools import tool
from langchain_core.runnables.config import RunnableConfig
from sqlalchemy import select

from src.infrastructure.models.public import DBProperty


@tool
async def get_neighborhoods(config: RunnableConfig):
    """Get all neighborhoods avaiable in MBRAS."""
    session = config.get("configurable", {}).get("session")

    neighborhoods = (
        (
            await session.execute(
                select(DBProperty.neighborhood).distinct(DBProperty.neighborhood)
            )
        )
        .scalars()
        .all()
    )

    return neighborhoods


# import asyncio
# from src.infrastructure.config.database import sessionmanager


# async def main():
#     async with sessionmanager.session() as session:
#         print(await get_neighborhoods({"session": session}))


# asyncio.run(main())
