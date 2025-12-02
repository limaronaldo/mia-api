import json
from typing import Optional

from langchain_community.tools import tool
from langchain_core.runnables import RunnableConfig
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.entities.property import Property
from src.core.enums.details import Details
from src.core.enums.property_type import PropertyType
from src.infrastructure.models.public import DBProperty


@tool(response_format="content_and_artifact")
async def search_properties(
    config: RunnableConfig,
    property_type: Optional[PropertyType] = None,
    min_suites: Optional[int] = None,
    max_suites: Optional[int] = None,
    min_bedrooms: Optional[int] = None,
    max_bedrooms: Optional[int] = None,
    min_bathrooms: Optional[int] = None,
    max_bathrooms: Optional[int] = None,
    min_usable_area: Optional[float] = None,
    max_usable_are: Optional[float] = None,
    min_total_area: Optional[float] = None,
    max_total_area: Optional[float] = None,
    is_for_sale: Optional[bool] = None,
    is_for_rent: Optional[bool] = None,
    is_residential: Optional[bool] = None,
    is_commercial: Optional[bool] = None,
    is_rural: Optional[bool] = None,
    is_industrial: Optional[bool] = None,
    min_rent_value: Optional[float] = None,
    max_rent_value: Optional[float] = None,
    min_sale_value: Optional[float] = None,
    max_sale_value: Optional[float] = None,
    building_name: Optional[str] = None,
    street_name: Optional[str] = None,
    city: Optional[str] = None,
    neighborhood: Optional[str] = None,
    details: Optional[list[Details]] = [],
    keywords: list[str] = [],
) -> tuple[list[Property], dict]:
    """Search for properties using strict filters with range support.
    Args:
        property_type (PropertyType, optional): Property type from enum options
        min_suites (int, optional): Minimum number of suites to filter
        max_suites (int, optional): Maximum number of suites to filter
        min_bedrooms (int, optional): Minimum number of bedrooms to filter
        max_bedrooms (int, optional): Maximum number of bedrooms to filter
        min_bathrooms (int, optional): Minimum number of bathrooms to filter
        max_bathrooms (int, optional): Maximum number of bathrooms to filter
        min_usable_area: (float, optional) = Minimum usable area to filter
        max_usable_are: (float, optional) = Maximum usable area to filter
        min_total_area: (float, optional) = Minimum total area to filter
        max_total_area: (float, optional) = Maximum total area to filter
        is_for_sale: (bool, optional) = If is for sale filter
        is_for_rent: (bool, optional) = If is for rent filter
        is_residential: (bool, optional) = If is residential filter
        is_commercial: (bool, optional) = If is commercial filter
        is_rural: (bool, optional) = If is rural filter
        is_industrial: (bool, optional) = If is industrial filter
        min_rent_value: (float, optional) = Minimum rent value to filter
        max_rent_value: (float, optional) = Maximum rent value to filter
        min_sale_value: (float, optional) = Minimum sale value to filter
        max_sale_value: (float, optional) = Maximum sale value to filter
        building_name: (str, optional) = Building name to filter
        city (str, optional): City name to filter
        neighborhood (str, optional): Neighborhood name to filter
        details (list[Details], optional): List of property details (Piscina, Vista ampla, etc.)
        keywords (list[str], optional): List of general search keywords, such as "Residencial Becker", "Residencial Parque Cidade Jardim"
    Returns:
        list[dict]: A list of properties that match the filters
    """
    try:
        session: AsyncSession = config.get("configurable", {}).get("session")

        q = select(DBProperty).filter(DBProperty.active.__eq__(True))

        if property_type:
            q = q.filter(DBProperty.property_type.ilike(f"%{property_type.value}%"))

        if min_suites:
            q = q.filter(DBProperty.suites >= min_suites)
        if max_suites:
            q = q.filter(DBProperty.suites <= max_suites)

        if min_bedrooms:
            q = q.filter(DBProperty.bedrooms >= min_bedrooms)
        if max_bedrooms:
            q = q.filter(DBProperty.bedrooms <= max_bedrooms)

        if min_bathrooms:
            q = q.filter(DBProperty.bedrooms >= min_bathrooms)
        if max_bathrooms:
            q = q.filter(DBProperty.bedrooms <= max_bathrooms)

        if city or neighborhood or building_name:
            q = q.filter(
                (
                    func.lower(func.unaccent(DBProperty.city))
                    == func.lower(func.unaccent(city or neighborhood))
                )
                | (
                    (
                        func.lower(func.unaccent(DBProperty.neighborhood))
                        == func.lower(func.unaccent(neighborhood or city))
                    )
                    | (
                        func.lower(func.unaccent(DBProperty.commercial_neighborhood))
                        == func.lower(func.unaccent(neighborhood or city))
                    )
                )
                | (
                    func.lower(func.unaccent(DBProperty.building_name))
                    == func.lower(func.unaccent(building_name))
                )
                | (DBProperty.title.op("%")(city))
                | (DBProperty.title.op("%")(neighborhood))
                | (DBProperty.title.op("%")(building_name))
                | (DBProperty.promotion.op("%")(city))
                | (DBProperty.promotion.op("%")(neighborhood))
                | (DBProperty.promotion.op("%")(building_name))
                | (DBProperty.building_name.op("%")(building_name))
            )

        if min_usable_area:
            q = q.filter(DBProperty.usable_area >= min_usable_area)
        if max_usable_are:
            q = q.filter(DBProperty.usable_area <= max_usable_are)

        if min_total_area:
            q = q.filter(DBProperty.total_area >= min_total_area)
        if max_total_area:
            q = q.filter(DBProperty.total_area <= max_total_area)

        if not (is_for_sale and is_for_rent):
            if is_for_sale:
                q = q.filter(DBProperty.is_for_sale == 1)
            if is_for_rent:
                q = q.filter(DBProperty.is_for_rent == 1)

        # if is_residential:
        #     filter_conditions.append(f"is_residential = {'S' if is_residential else 'N'}")
        # if is_commercial:
        #     filter_conditions.append(f"is_commercial = {'S' if is_commercial else 'N'}")
        # if is_rural:
        #     filter_conditions.append(f"is_rural = {'S' if is_rural else 'N'}")
        # if is_industrial:
        #     filter_conditions.append(f"is_industrial = {'S' if is_industrial else 'N'}")

        if min_rent_value:
            q = q.filter(DBProperty.rent_value >= min_rent_value)
        if max_rent_value:
            q = q.filter(DBProperty.rent_value <= max_rent_value)

        if min_sale_value:
            q = q.filter(DBProperty.sale_value >= min_sale_value)
        if max_sale_value:
            q = q.filter(DBProperty.sale_value <= max_sale_value)

        if details:
            q = q.filter(
                or_(
                    *[DBProperty.unit_details.ilike(f"%{ud.value}%") for ud in details],
                    *[
                        DBProperty.condo_details.ilike(f"%{cd.value}%")
                        for cd in details
                    ],
                )
            )

        if street_name:
            q = q.filter(DBProperty.address.op("%")(street_name))

        if keywords:
            keyword_conditions = []
            for k in keywords:
                keyword_conditions.append(DBProperty.title.op("%")(k))
                keyword_conditions.append(DBProperty.promotion.op("%")(k))
                keyword_conditions.append(DBProperty.description.op("%")(k))
                keyword_conditions.append(DBProperty.building_name.op("%")(k))
            q = q.filter(or_(*keyword_conditions))

        results = (await session.execute(q)).scalars().all()

        properties = [Property.model_validate(p) for p in results]

        for prop in properties:
            if hasattr(prop, "location"):
                setattr(prop, "location", None)

        data = [p.model_dump() for p in properties]

        return json.dumps(
            {"hits": data[:6], "total_hits_without_trim": len(data)},
            default=str,
        ), {"ids": [str(d.get("id")) for d in data]}

    except Exception as e:
        print(e)
        raise e
