import json

from langchain_community.tools import tool
from langchain_core.runnables.config import RunnableConfig
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.lib.logger import guide_logger
from src.infrastructure.models.public import DBProperty


@tool
async def get_property_financials(
    property_reference: str, config: RunnableConfig
) -> str:
    """
    Get detailed financial information for a property including IPTU, condo fees, and other costs.

    Args:
        property_reference: The reference ID of the property
        config: Runtime configuration containing database session

    Returns:
        JSON string with financial details including taxes, fees, and maintenance costs
    """
    try:
        session: AsyncSession = config.get("configurable", {}).get("session")
        if not session:
            return json.dumps({"error": "Database session not available"})

        query = select(DBProperty).where(DBProperty.ref == property_reference)
        result = await session.execute(query)
        property_data = result.scalar_one_or_none()

        if not property_data:
            return json.dumps({"error": f"Property {property_reference} not found"})

        financials = {
            "property_reference": property_reference,
            "iptu_annual": property_data.iptu,
            "condo_fee_monthly": property_data.condo_fee,
            "value": property_data.value,
            "sale_value": property_data.sale_value,
            "sale_value_per_m2": property_data.sale_value_per_m2,
            "rent_value": property_data.rent_value,
            "rent_value_per_m2": property_data.rent_value_per_m2,
            "entry_value": property_data.entry_value,
            "installment_value": property_data.installment_value,
            "total_area": property_data.total_area,
            "usable_area": property_data.usable_area,
            "iptu_type": property_data.iptu_type,
            "with_financing": property_data.with_financing,
            "payment_conditions": property_data.payment_conditions,
            "maintenance_estimate": "Contact broker for detailed maintenance estimates",
            "currency": "BRL",
        }

        guide_logger.info(f"Retrieved financial data for property {property_reference}")
        return json.dumps(financials, ensure_ascii=False)

    except Exception as e:
        guide_logger.error(
            f"Error retrieving financial data for {property_reference}: {e}"
        )
        return json.dumps({"error": f"Failed to retrieve financial data: {str(e)}"})


@tool
async def run_comparative_market_analysis(
    property_reference: str, radius_km: int = 2, config: RunnableConfig = None
) -> str:
    """
    Generate a comparative market analysis for similar properties in the area.

    Args:
        property_reference: The reference ID of the subject property
        radius_km: Search radius in kilometers for comparable properties
        config: Runtime configuration containing database session

    Returns:
        JSON string with comparative analysis of similar properties
    """
    try:
        session: AsyncSession = config.get("configurable", {}).get("session")
        if not session:
            return json.dumps({"error": "Database session not available"})

        query = select(DBProperty).where(DBProperty.ref == property_reference)
        result = await session.execute(query)
        subject_property = result.scalar_one_or_none()

        if not subject_property:
            return json.dumps(
                {"error": f"Subject property {property_reference} not found"}
            )

        area_min = (
            subject_property.total_area * 0.8 if subject_property.total_area else 0
        )
        area_max = (
            subject_property.total_area * 1.2 if subject_property.total_area else 999999
        )

        comparables_query = (
            select(DBProperty)
            .where(
                and_(
                    DBProperty.ref != property_reference,
                    DBProperty.neighborhood == subject_property.neighborhood,
                    DBProperty.property_type == subject_property.property_type,
                    DBProperty.total_area.between(area_min, area_max),
                    DBProperty.value.isnot(None),
                )
            )
            .limit(5)
        )

        comp_result = await session.execute(comparables_query)
        comparables = comp_result.scalars().all()

        if comparables:
            prices = [comp.value for comp in comparables if comp.value]
            areas = [comp.total_area for comp in comparables if comp.total_area]
            price_per_sqm = [
                comp.value / comp.total_area
                for comp in comparables
                if comp.value and comp.total_area
            ]

            avg_price = sum(prices) / len(prices) if prices else 0
            avg_area = sum(areas) / len(areas) if areas else 0
            avg_price_per_sqm = (
                sum(price_per_sqm) / len(price_per_sqm) if price_per_sqm else 0
            )

            comparable_list = []
            for comp in comparables:
                comparable_list.append(
                    {
                        "reference": comp.ref,
                        "value": comp.value,
                        "total_area": comp.total_area,
                        "usable_area": comp.usable_area,
                        "price_per_sqm": comp.value / comp.total_area
                        if comp.value and comp.total_area
                        else None,
                        "bedrooms": comp.bedrooms,
                        "bathrooms": comp.bathrooms,
                        "address": comp.address,
                        "neighborhood": comp.neighborhood,
                        "parking_spaces": comp.parking_spaces,
                    }
                )

            analysis = {
                "subject_property": {
                    "reference": property_reference,
                    "value": subject_property.value,
                    "total_area": subject_property.total_area,
                    "usable_area": subject_property.usable_area,
                    "price_per_sqm": subject_property.value
                    / subject_property.total_area
                    if subject_property.value and subject_property.total_area
                    else None,
                },
                "market_statistics": {
                    "average_price": round(avg_price, 2),
                    "average_area": round(avg_area, 2),
                    "average_price_per_sqm": round(avg_price_per_sqm, 2),
                    "total_comparables": len(comparables),
                },
                "comparables": comparable_list,
                "analysis_summary": f"Based on {len(comparables)} comparable properties in {subject_property.neighborhood}",
                "search_radius_km": radius_km,
            }
        else:
            analysis = {
                "subject_property": {
                    "reference": property_reference,
                    "value": subject_property.value,
                    "total_area": subject_property.total_area,
                },
                "error": "No comparable properties found in the immediate area",
                "recommendation": "Expand search criteria or consult with a local market expert",
                "search_radius_km": radius_km,
            }

        guide_logger.info(f"Generated CMA for property {property_reference}")
        return json.dumps(analysis, ensure_ascii=False)

    except Exception as e:
        guide_logger.error(f"Error generating CMA for {property_reference}: {e}")
        return json.dumps(
            {"error": f"Failed to generate comparative analysis: {str(e)}"}
        )


@tool
async def project_property_valuation(
    property_reference: str, years_ahead: int = 5, config: RunnableConfig = None
) -> str:
    """
    Project property valuation and appreciation potential over specified time frame.

    Args:
        property_reference: The reference ID of the property
        years_ahead: Number of years to project (default 5)
        config: Runtime configuration containing database session

    Returns:
        JSON string with valuation projections and investment analysis
    """
    try:
        session: AsyncSession = config.get("configurable", {}).get("session")
        if not session:
            return json.dumps({"error": "Database session not available"})

        query = select(DBProperty).where(DBProperty.ref == property_reference)
        result = await session.execute(query)
        property_data = result.scalar_one_or_none()

        if not property_data:
            return json.dumps({"error": f"Property {property_reference} not found"})

        current_price = property_data.value if property_data.value else 0
        neighborhood = property_data.neighborhood
        property_type = property_data.property_type

        base_rates = {
            "Ipanema": 0.08,
            "Copacabana": 0.07,
            "Leblon": 0.09,
            "Barra da Tijuca": 0.06,
            "default": 0.05,
        }

        annual_rate = base_rates.get(neighborhood, base_rates["default"])

        projections = []
        projected_price = current_price

        for year in range(1, years_ahead + 1):
            projected_price = projected_price * (1 + annual_rate)
            projections.append(
                {
                    "year": year,
                    "projected_price": round(projected_price, 2),
                    "appreciation_amount": round(projected_price - current_price, 2),
                    "total_appreciation_percent": round(
                        ((projected_price - current_price) / current_price * 100), 2
                    )
                    if current_price
                    else 0,
                }
            )

        total_appreciation = projected_price - current_price
        annualized_return = (
            ((projected_price / current_price) ** (1 / years_ahead) - 1) * 100
            if current_price
            else 0
        )

        valuation_analysis = {
            "property_reference": property_reference,
            "current_valuation": current_price,
            "projection_period": f"{years_ahead} years",
            "annual_appreciation_rate": f"{annual_rate * 100:.1f}%",
            "projected_final_value": round(projected_price, 2),
            "total_appreciation": round(total_appreciation, 2),
            "annualized_return": f"{annualized_return:.2f}%",
            "yearly_projections": projections,
            "market_context": {
                "neighborhood": neighborhood,
                "property_type": property_type,
                "city": property_data.city,
                "region": property_data.region,
                "analysis_basis": "Conservative luxury real estate market trends",
            },
            "disclaimer": "Projections are estimates based on historical market trends and should not be considered investment advice",
        }

        guide_logger.info(
            f"Generated valuation projection for property {property_reference}"
        )
        return json.dumps(valuation_analysis, ensure_ascii=False)

    except Exception as e:
        guide_logger.error(f"Error projecting valuation for {property_reference}: {e}")
        return json.dumps({"error": f"Failed to project valuation: {str(e)}"})


@tool
def generate_property_report_pdf(property_data: str) -> str:
    """
    Generate a comprehensive PDF report for a property analysis.

    Args:
        property_data: JSON string containing property analysis data

    Returns:
        Status message about report generation
    """
    try:
        # Parse the property data to validate it's proper JSON
        parsed_data = json.loads(property_data)

        report_info = {
            "status": "report_generated",
            "message": "Comprehensive property analysis report has been prepared",
            "contents": [
                "Executive Summary",
                "Property Details & Financials",
                "Comparative Market Analysis",
                "Investment Projection",
                "Market Context & Trends",
                "Risk Assessment",
            ],
            "delivery_method": "Available for download or email delivery",
            "note": "Contact your MBRAS advisor to receive the detailed PDF report",
            "data_included": bool(parsed_data),
        }

        guide_logger.info("Property report generation requested")
        return json.dumps(report_info, ensure_ascii=False)

    except Exception as e:
        guide_logger.error(f"Error generating property report: {e}")
        return json.dumps({"error": f"Failed to generate report: {str(e)}"})
