import httpx
from decouple import config
from langchain_core.tools import tool

from src.infrastructure.ai.schemas.listing_form import ListingForm


@tool
async def send_listing_form(listing_form: ListingForm) -> str:
    """Send a listing form to the commercial team of MBRAS.

    Args:
        listing_form (ListingForm): The listing form to send.

    Returns:
        str: A message indicating that the form was sent successfully.
    """

    form_data = listing_form.model_dump()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://formspree.io/f/xnnbnjoo",
                json=form_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config('MASTER_FORMSPREE_API_KEY')}",
                },
            )
            response.raise_for_status()
            return "Form sent successfully to MBRAS commercial team"
        except httpx.HTTPError as e:
            return f"Failed to send form: {str(e)}"
