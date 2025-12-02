from .broker_contact import suggest_broker_contact
from .calculator import get_calculator_toolkit
from .concierge import (
    find_nearby_amenities,
    get_property_media_links,
    schedule_viewing,
    send_portfolio_email,
    send_portfolio_whatsapp,
)
from .get_cities import get_cities
from .get_neighborhoods import get_neighborhoods
from .get_property_by_reference import get_property_by_reference
from .lead_seeker.send_listing_form import send_listing_form
from .market_analyst import (
    generate_property_report_pdf,
    get_property_financials,
    project_property_valuation,
    run_comparative_market_analysis,
)
from .meilisearch import (
    deep_search_properties,
    search_iptus,
    search_transactions,
)
from .property import search_properties

broker_tools = [
    search_properties,
    deep_search_properties,
    get_property_by_reference,
    get_neighborhoods,
    get_cities,
    *get_calculator_toolkit(),
    suggest_broker_contact,
]


market_analyst_tools = [
    get_property_financials,
    run_comparative_market_analysis,
    project_property_valuation,
    generate_property_report_pdf,
]


concierge_tools = [
    # schedule_viewing,
    send_portfolio_email,
    send_portfolio_whatsapp,
    find_nearby_amenities,
    get_property_media_links,
]


chat_tools = [
    search_properties,
    get_property_by_reference,
    get_neighborhoods,
    get_cities,
    *get_calculator_toolkit(),
    suggest_broker_contact,
]

lead_seeker_tools = [suggest_broker_contact, send_listing_form]

chat_ibvi_tools = [search_iptus, search_transactions]
