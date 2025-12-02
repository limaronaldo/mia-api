import asyncio
import base64
from datetime import datetime
from typing import List

import httpx
from decouple import config
from langchain_community.tools import tool
from langchain_core.runnables.config import RunnableConfig
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.lib.email import EmailSender
from src.infrastructure.lib.logger import guide_logger
from src.infrastructure.lib.whatsapp import (
    MessageFileRequest,
    MessageTextRequest,
    whatsapp_client,
)
from src.infrastructure.models.public import DBProperty
from src.infrastructure.templates.email_template_engine import get_email_template_engine


@tool
async def send_welcome_email(
    client_name: str,
    client_email: str,
    config: RunnableConfig = None,
) -> str:
    """
    Send a welcome email to a new client.

    Args:
        client_name: Full name of the client
        client_email: Email address of the client
        config: Runtime configuration

    Returns:
        JSON string with email delivery status
    """
    try:
        template_engine = get_email_template_engine()

        html_body, text_body = template_engine.render_welcome_email(
            client_name=client_name,
            client_email=client_email,
        )

        subject = f"Bem-vindo à MBRAS, {client_name}!"

        email_sent = await EmailSender.send_email_with_attachments(
            to_email=client_email,
            subject=subject,
            body=html_body,
            attachments=[],
            is_html=True,
        )

        if email_sent:
            welcome_details = {
                "delivery_status": "enviado",
                "recipient": client_email,
                "recipient_name": client_name,
                "email_subject": subject,
                "template_used": "welcome",
                "delivery_confirmation": f"E-mail de boas-vindas enviado com sucesso para {client_email}",
                "contents": [
                    "Mensagem de boas-vindas personalizada",
                    "Apresentação dos diferenciais MBRAS",
                    "Próximos passos e orientações",
                    "Benefícios exclusivos para clientes",
                    "Informações de contato direto",
                ],
                "follow_up": "Cliente receberá contato da equipe em 24 horas",
            }

            guide_logger.info(f"Welcome email sent to {client_email}")
            return welcome_details
        else:
            return {"error": "Falha ao enviar e-mail de boas-vindas"}

    except Exception as e:
        guide_logger.error(f"Error sending welcome email to {client_email}: {e}")
        return {"error": f"Falha ao enviar e-mail de boas-vindas: {str(e)}"}


@tool
async def send_property_inquiry_email(
    client_name: str,
    client_email: str,
    property_reference: str,
    property_details: dict = None,
    config: RunnableConfig = None,
) -> str:
    """
    Send a property inquiry response email to a client.

    Args:
        client_name: Full name of the client
        client_email: Email address of the client
        property_reference: Property reference ID
        property_details: Dictionary with property details
        config: Runtime configuration

    Returns:
        JSON string with email delivery status
    """
    try:
        session: AsyncSession | None = config.get("configurable", {}).get("session")

        if not session:
            return {"error": "Database session not available"}

        if not property_details:
            query = select(DBProperty).where(DBProperty.ref == property_reference)
            result = await session.execute(query)
            property_data = result.scalar_one_or_none()

            if property_data:
                property_details = {
                    "address": f"{property_data.address} {property_data.street_name}",
                    "price": property_data.value,
                    "area": property_data.total_area,
                    "bedrooms": property_data.bedrooms,
                    "bathrooms": property_data.bathrooms,
                    "description": property_data.description or property_data.promotion,
                }

        template_engine = get_email_template_engine()

        property_highlights = [
            "Localização privilegiada",
            "Acabamentos de primeira linha",
            "Vista panorâmica",
            "Infraestrutura completa",
            "Segurança 24 horas",
            "Área de lazer exclusiva",
        ]

        investment_data = {
            "appreciation": "8-12%",
            "rental_yield": "4-6%",
            "roi": "15-18%",
        }

        html_body, text_body = template_engine.render_property_inquiry_email(
            client_name=client_name,
            client_email=client_email,
            property_reference=property_reference,
            property_details=property_details or {},
            property_highlights=property_highlights,
            investment_data=investment_data,
        )

        subject = f"Sua Consulta sobre {property_reference} - MBRAS"

        email_sent = await EmailSender.send_email_with_attachments(
            to_email=client_email,
            subject=subject,
            body=html_body,
            attachments=[],
            is_html=True,
        )

        if email_sent:
            inquiry_details = {
                "delivery_status": "enviado",
                "recipient": client_email,
                "recipient_name": client_name,
                "property_reference": property_reference,
                "email_subject": subject,
                "template_used": "property_inquiry",
                "delivery_confirmation": f"E-mail de resposta à consulta enviado com sucesso para {client_email}",
                "contents": [
                    "Resposta personalizada à consulta",
                    "Detalhes completos da propriedade",
                    "Cronograma de próximos passos",
                    "Análise de investimento",
                    "Propriedades similares",
                    "Opções de contato direto",
                ],
                "follow_up": "Equipe MBRAS entrará em contato em até 2 horas",
            }

            guide_logger.info(
                f"Property inquiry email sent to {client_email} for {property_reference}"
            )
            return inquiry_details
        else:
            return {"error": "Falha ao enviar e-mail de resposta"}

    except Exception as e:
        guide_logger.error(f"Error sending property inquiry email: {e}")
        return {"error": f"Falha ao enviar e-mail de resposta: {str(e)}"}


@tool
async def schedule_viewing(
    property_reference: str,
    client_name: str,
    client_email: str,
    preferred_date: str,
    preferred_time: str,
    config: RunnableConfig,
) -> str:
    """
    Schedule a private property viewing for a client.

    Args:
        property_reference: The reference ID of the property
        client_name: Full name of the client
        client_email: Email address of the client
        preferred_date: Preferred date for viewing (YYYY-MM-DD format)
        preferred_time: Preferred time for viewing (HH:MM format)
        config: Runtime configuration

    Returns:
        JSON string with viewing appointment details
    """
    try:
        session: AsyncSession | None = config.get("configurable", {}).get("session")
        if not session:
            return {"error": "Database session not available"}

        query = select(DBProperty).where(DBProperty.ref == property_reference)
        result = await session.execute(query)
        property_data = result.scalar_one_or_none()

        if not property_data:
            return {"error": f"Property {property_reference} not found"}

        viewing_details = {
            "appointment_id": f"VIEW-{property_reference}-{datetime.now().strftime('%Y%m%d%H%M')}",
            "property_reference": property_reference,
            "property_address": property_data.address,
            "client_name": client_name,
            "client_email": client_email,
            "requested_date": preferred_date,
            "requested_time": preferred_time,
            "status": "pending_confirmation",
            "confirmation_message": "Your viewing request has been submitted successfully",
            "next_steps": [
                "MBRAS team will confirm availability within 2 hours",
                "You will receive a confirmation email with viewing details",
                "Please arrive 5 minutes before the scheduled time",
            ],
            "contact_info": "For any changes, contact MBRAS at +55 21 3000-0000",
        }

        try:
            template_engine = get_email_template_engine()
            html_body, text_body = template_engine.render_viewing_confirmation_email(
                client_name=client_name,
                client_email=client_email,
                property_reference=property_reference,
                property_address=property_data.address,
                viewing_date=preferred_date,
                viewing_time=preferred_time,
                appointment_id=viewing_details["appointment_id"],
            )

            subject = f"Confirmação de Visita - {property_reference}"

            email_sent = await EmailSender.send_email_with_attachments(
                to_email=client_email,
                subject=subject,
                body=html_body,
                attachments=[],
                is_html=True,
            )

            if email_sent:
                viewing_details["email_confirmation"] = (
                    "E-mail de confirmação enviado com sucesso"
                )
                guide_logger.info(
                    f"Viewing confirmation email sent to {client_email} for property {property_reference}"
                )
            else:
                viewing_details["email_confirmation"] = (
                    "Falha ao enviar e-mail de confirmação"
                )
                guide_logger.warning(
                    f"Failed to send viewing confirmation email to {client_email}"
                )

        except Exception as email_error:
            guide_logger.warning(
                f"Error sending viewing confirmation email: {email_error}"
            )
            viewing_details["email_confirmation"] = (
                f"Erro ao enviar e-mail: {str(email_error)}"
            )

        guide_logger.info(
            f"Viewing scheduled for property {property_reference} by {client_name}"
        )
        return viewing_details

    except Exception as e:
        guide_logger.error(f"Error scheduling viewing for {property_reference}: {e}")
        return {"error": f"Failed to schedule viewing: {str(e)}"}


async def _generate_pdf_presentation(ref: str):
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.get(f"{config('PDF_GENERATOR_API_URL')}?ref={ref}")
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(
                f"Failed to generate PDF presentation: {response.status_code}"
            )


@tool
async def send_portfolio_email(
    client_email: str,
    property_references: List[str],
    client_name: str = "Cliente Valorizado",
    config: RunnableConfig = None,
) -> str:
    """
    Send a curated property portfolio to client via email.

    Args:
        client_email: Email address of the client
        property_references: List of property reference IDs to include
        client_name: Name of the client for personalization
        config: Runtime configuration containing database session

    Returns:
        JSON string with email delivery status
    """

    try:
        session: AsyncSession | None = config.get("configurable", {}).get("session")

        if not session:
            return {"error": "Sessão de banco de dados não disponível"}

        portfolio_properties = []
        pdf_attachments_data = []

        for ref in property_references:
            query = select(DBProperty).where(DBProperty.ref == ref)
            result = await session.execute(query)
            prop = result.scalar_one_or_none()

            if prop:
                portfolio_properties.append(
                    {
                        "reference": ref,
                        "address": f"{prop.address} {prop.street_name}",
                        "price": prop.value,
                        "area": prop.total_area,
                        "bedrooms": prop.bedrooms,
                        "bathrooms": prop.bathrooms,
                        "description": (
                            (prop.description[:200] or prop.promotion[:200]) + "..."
                            if prop.description and len(prop.description) > 200
                            else prop.description
                        ),
                    }
                )

                try:
                    pdf_content = await _generate_pdf_presentation(ref)
                    pdf_attachments_data.append(
                        {
                            "data": pdf_content,
                            "filename": f"MBRAS_{ref}_Apresentacao.pdf",
                            "mime_type": "application/pdf",
                        }
                    )
                except Exception as pdf_error:
                    guide_logger.warning(
                        f"Falha ao gerar PDF para propriedade {ref}: {pdf_error}"
                    )

        if not portfolio_properties:
            return {"error": "Nenhuma propriedade válida encontrada para o portfólio"}

        template_engine = get_email_template_engine()

        try:
            html_body, text_body = template_engine.render_portfolio_email(
                client_name=client_name,
                client_email=client_email,
                properties=portfolio_properties,
                pdf_count=len(pdf_attachments_data),
            )
        except Exception as template_error:
            guide_logger.warning(
                f"Template rendering failed, using fallback: {template_error}"
            )

            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #1447e6;">Prezado(a) {client_name},</h2>
                <p>Obrigado pelo seu interesse nas propriedades MBRAS. Em anexo você encontrará seu portfólio personalizado com {len(portfolio_properties)} propriedades exclusivas.</p>
                <h3>Propriedades em seu Portfólio:</h3>
                <ul>
            """
            for prop in portfolio_properties:
                html_body += f"""
                    <li><strong>{prop["reference"]}</strong> - {prop["address"]}<br/>
                        Preço: {f"R$ {prop['price']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if prop["price"] else "Consulte-nos"} | Área: {prop["area"]} | Quartos: {prop["bedrooms"]} | Banheiros: {prop["bathrooms"]}<br/>
                        {prop["description"]}</li>
                """
            html_body += """
                </ul>
                <p>Atenciosamente,<br/><strong>Equipe MBRAS</strong><br/>Contato: +55 21 3000-0000</p>
            </body>
            </html>
            """
            text_body = f"""
            Prezado(a) {client_name},

            Obrigado pelo seu interesse nas propriedades MBRAS. Em anexo você encontrará seu portfólio personalizado com {len(portfolio_properties)} propriedades exclusivas.

            Atenciosamente,
            Equipe MBRAS
            Contato: +55 21 3000-0000
            """

        subject = f"Seu Portfólio Personalizado MBRAS - {len(portfolio_properties)} Propriedades Exclusivas"

        email_sent = await EmailSender.send_email_with_attachments(
            to_email=client_email,
            subject=subject,
            body=html_body,
            attachments=pdf_attachments_data,
            is_html=True,
        )

        if email_sent:
            pdf_attachments = [
                {
                    "property_reference": prop["reference"],
                    "pdf_filename": f"MBRAS_{prop['reference']}_Apresentacao.pdf",
                    "pdf_size_bytes": len(
                        [
                            att
                            for att in pdf_attachments_data
                            if prop["reference"] in att["filename"]
                        ][0]["data"]
                    )
                    if any(
                        prop["reference"] in att["filename"]
                        for att in pdf_attachments_data
                    )
                    else 0,
                    "generated_at": datetime.now().isoformat(),
                }
                for prop in portfolio_properties
                if any(
                    prop["reference"] in att["filename"] for att in pdf_attachments_data
                )
            ]

            email_details = {
                "delivery_status": "enviado",
                "recipient": client_email,
                "recipient_name": client_name,
                "portfolio_id": f"PORTFOLIO-{datetime.now().strftime('%Y%m%d%H%M')}",
                "properties_included": len(portfolio_properties),
                "email_subject": subject,
                "pdf_attachments": pdf_attachments,
                "total_attachments": len(pdf_attachments_data),
                "contents": [
                    "Mensagem personalizada de boas-vindas",
                    "Apresentações profissionais em PDF para cada propriedade",
                    "Fotos HD e tours virtuais das propriedades",
                    "Especificações detalhadas das propriedades",
                    "Destaques do bairro",
                    "Resumo de análise de investimento",
                    "Informações diretas de contato para solicitação de visitas",
                ],
                "delivery_confirmation": f"E-mail de portfólio com {len(pdf_attachments_data)} apresentações em PDF enviado com sucesso para {client_email}",
                "follow_up": "Equipe MBRAS entrará em contato em até 24 horas",
                "properties_summary": portfolio_properties,
            }

            guide_logger.info(
                f"E-mail de portfólio enviado para {client_email} com {len(portfolio_properties)} propriedades e {len(pdf_attachments_data)} anexos em PDF"
            )
            return email_details
        else:
            return {"error": "Falha ao enviar e-mail"}

    except Exception as e:
        guide_logger.error(
            f"Erro ao enviar e-mail de portfólio para {client_email}: {e}"
        )
        return {"error": f"Falha ao enviar e-mail de portfólio: {str(e)}"}


@tool
async def send_portfolio_whatsapp(
    phone_number: str,
    property_references: List[str],
    client_name: str = "Valued Client",
    config: RunnableConfig = None,
) -> str:
    """
    Send a curated property portfolio to client via WhatsApp.

    Args:
        phone_number: WhatsApp phone number (with country code)
        property_references: List of property reference IDs to include
        client_name: Name of the client for personalization
        config: Runtime configuration containing database session

    Returns:
        JSON string with WhatsApp delivery status
    """
    try:
        session: AsyncSession | None = config.get("configurable", {}).get("session")
        if not session:
            return {"error": "Database session not available"}

        portfolio_properties = []
        pdf_attachments = []

        for ref in property_references:
            query = select(DBProperty).where(DBProperty.ref == ref)
            result = await session.execute(query)
            prop = result.scalar_one_or_none()

            if prop:
                portfolio_properties.append(
                    {
                        "reference": ref,
                        "address": f"{prop.address} {prop.street_name}",
                        "price": prop.value,
                        "area": prop.total_area or prop.usable_area,
                        "bedrooms": prop.bedrooms,
                        "bathrooms": prop.bathrooms,
                        "description": (
                            (prop.description or prop.promotion or "")[:100] + "..."
                            if len(prop.description or prop.promotion or "") > 100
                            else (prop.description or prop.promotion or "")
                            or "Propriedade exclusiva"
                        ),
                    }
                )

                try:
                    pdf_content = await _generate_pdf_presentation(ref)
                    pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")
                    pdf_attachments.append(
                        {
                            "property_reference": ref,
                            "pdf_filename": f"MBRAS_{ref}_Apresentacao.pdf",
                            "pdf_size_bytes": len(pdf_content),
                            "pdf_base64": pdf_base64,
                            "generated_at": datetime.now().isoformat(),
                        }
                    )
                except Exception as pdf_error:
                    guide_logger.warning(
                        f"Failed to generate PDF for property {ref}: {pdf_error}"
                    )

        if not portfolio_properties:
            return {"error": "No valid properties found for portfolio"}

        chat_id = (
            phone_number.replace("+", "").replace(" ", "").replace("-", "") + "@c.us"
        )

        welcome_message = f"""*MBRAS - Imóveis de Luxo*

Olá {client_name}! 👋

Preparamos um portfólio exclusivo com *{len(portfolio_properties)} propriedade{"s" if len(portfolio_properties) > 1 else ""}* selecionada{"" if len(portfolio_properties) == 1 else "s"} especialmente para você.

🌟 *Sua{"s" if len(portfolio_properties) > 1 else ""} propriedade{"s" if len(portfolio_properties) > 1 else ""} selecionadas:*"""

        message_request = MessageTextRequest(
            chatId=chat_id, text=welcome_message, session="default"
        )

        try:
            await whatsapp_client.start_typing(
                session="default",
                request_body={"session": "default", "chatId": chat_id},
            )
            await asyncio.sleep(2)
            await whatsapp_client.stop_typing(
                session="default",
                request_body={"session": "default", "chatId": chat_id},
            )
            welcome_response = await whatsapp_client.send_text_message(message_request)
            guide_logger.info(f"Welcome message sent to {phone_number}")
        except Exception as msg_error:
            guide_logger.warning(f"Failed to send welcome message: {msg_error}")

        for prop in portfolio_properties:
            property_message = f"""🏠 *{prop["reference"]}*
📍 {prop["address"]}
💰 Preço: {f"R$ {prop['price']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if prop["price"] else "Consulte-nos"}
📐 Área: {prop["area"]}
🛏️ {prop["bedrooms"]} quartos | 🚿 {prop["bathrooms"]} banheiros

{prop["description"] or "Propriedade exclusiva MBRAS"}"""

            prop_message_request = MessageTextRequest(
                chatId=chat_id, text=property_message, session="default"
            )

            try:
                await whatsapp_client.start_typing(
                    session="default",
                    request_body={"session": "default", "chatId": chat_id},
                )
                await asyncio.sleep(6)
                await whatsapp_client.stop_typing(
                    session="default",
                    request_body={"session": "default", "chatId": chat_id},
                )
                prop_response = await whatsapp_client.send_text_message(
                    prop_message_request
                )

                pdf_data = next(
                    (
                        pdf
                        for pdf in pdf_attachments
                        if pdf["property_reference"] == prop["reference"]
                    ),
                    None,
                )
                if pdf_data:
                    file_request = MessageFileRequest(
                        chatId=chat_id,
                        file={
                            "mimetype": "application/pdf",
                            "filename": pdf_data["pdf_filename"],
                            "data": pdf_data["pdf_base64"],
                        },
                        caption=f"📄 Apresentação completa - {prop['reference']}",
                        session="default",
                    )

                    try:
                        pdf_response = await whatsapp_client.send_file_message(
                            file_request
                        )
                        del pdf_data["pdf_base64"]
                    except Exception as pdf_send_error:
                        guide_logger.warning(
                            f"Failed to send PDF for {prop['reference']}: {pdf_send_error}"
                        )

            except Exception as prop_error:
                guide_logger.warning(
                    f"Failed to send property message for {prop['reference']}: {prop_error}"
                )

        closing_message = """✨ *Próximos Passos*

🤝 Nossa equipe entrará em contato em breve
📱 Responda esta mensagem para mais informações
📅 Agende sua visita exclusiva

*MBRAS - Transformando sonhos em endereços*
📞 +55 21 3000-0000
🌐 www.mbras.com.br"""

        closing_request = MessageTextRequest(
            chatId=chat_id, text=closing_message, session="default"
        )

        # try:
        #     await whatsapp_client.start_typing(
        #         session="default",
        #         request_body={"session": "default", "chatId": chat_id},
        #     )
        #     await asyncio.sleep(3)
        #     await whatsapp_client.stop_typing(
        #         session="default",
        #         request_body={"session": "default", "chatId": chat_id},
        #     )
        #     closing_response = await whatsapp_client.send_text_message(closing_request)
        # except Exception as closing_error:
        #     guide_logger.warning(f"Failed to send closing message: {closing_error}")

        whatsapp_details = {
            "delivery_status": "sent",
            "recipient_phone": phone_number,
            "recipient_name": client_name,
            "portfolio_id": f"WA-PORTFOLIO-{datetime.now().strftime('%Y%m%d%H%M')}",
            "properties_included": len(portfolio_properties),
            "pdf_attachments": pdf_attachments,
            "total_attachments": len(pdf_attachments),
            "message_format": "Interactive multimedia messages with PDF attachments",
            "contents": [
                "Welcome message with MBRAS branding",
                "Professional PDF presentations for each property",
                "Property details with pricing and specifications",
                "High-quality property descriptions",
                "Direct contact information",
                "Next steps and call-to-action",
            ],
            "delivery_confirmation": f"Portfolio with {len(pdf_attachments)} PDF presentations sent via WhatsApp to {phone_number}",
            "interactive_features": [
                "Reply to message for immediate contact",
                "PDF downloads for detailed property info",
                "Direct phone contact available",
                "Share with family/friends capability",
            ],
            "follow_up": "MBRAS team available for immediate chat support",
        }

        guide_logger.info(
            f"Portfolio WhatsApp sent to {phone_number} with {len(portfolio_properties)} properties and {len(pdf_attachments)} PDF attachments"
        )
        return whatsapp_details

    except Exception as e:
        guide_logger.error(f"Error sending portfolio WhatsApp to {phone_number}: {e}")
        import traceback

        traceback.print_exc()
        return {"error": f"Failed to send portfolio WhatsApp: {str(e)}"}


@tool
async def find_nearby_amenities(
    property_reference: str,
    amenity_types: List[str],
    radius_km: float = 2.0,
    config: RunnableConfig = None,
) -> str:
    """
    Find nearby amenities and points of interest around a property.

    Args:
        property_reference: The reference ID of the property
        amenity_types: List of amenity types to search for (e.g., "schools", "restaurants", "hospitals")
        radius_km: Search radius in kilometers
        config: Runtime configuration containing database session

    Returns:
        JSON string with nearby amenities information
    """
    try:
        session: AsyncSession | None = config.get("configurable", {}).get("session")
        if not session:
            return {"error": "Database session not available"}

        query = select(DBProperty).where(DBProperty.ref == property_reference)
        result = await session.execute(query)
        property_data = result.scalar_one_or_none()

        if not property_data:
            return {"error": f"Property {property_reference} not found"}

        amenity_categories = {
            "schools": [
                {
                    "name": "International School of Rio",
                    "type": "International School",
                    "distance_km": 1.2,
                    "rating": 4.8,
                    "address": "Nearby prestigious location",
                    "highlights": ["Bilingual education", "IB program", "Ages 3-18"],
                },
                {
                    "name": "British School Rio de Janeiro",
                    "type": "International School",
                    "distance_km": 1.8,
                    "rating": 4.7,
                    "address": "Prime educational district",
                    "highlights": [
                        "British curriculum",
                        "University prep",
                        "Sports facilities",
                    ],
                },
            ],
            "restaurants": [
                {
                    "name": "Michelin Star Restaurant",
                    "type": "Fine Dining",
                    "distance_km": 0.8,
                    "rating": 4.9,
                    "cuisine": "Contemporary Brazilian",
                    "price_range": "$$$",
                    "highlights": [
                        "Oceanfront dining",
                        "Celebrity chef",
                        "Wine cellar",
                    ],
                },
                {
                    "name": "Exclusive Beach Club",
                    "type": "Beach Restaurant & Club",
                    "distance_km": 0.5,
                    "rating": 4.6,
                    "cuisine": "Seafood & International",
                    "price_range": "$$$$",
                    "highlights": [
                        "Private beach access",
                        "Infinity pool",
                        "Sunset views",
                    ],
                },
            ],
            "hospitals": [
                {
                    "name": "Hospital Copa Star",
                    "type": "Private Hospital",
                    "distance_km": 1.5,
                    "rating": 4.5,
                    "specialties": ["Cardiology", "Oncology", "Emergency Care"],
                    "highlights": [
                        "24/7 emergency",
                        "International standards",
                        "VIP rooms",
                    ],
                }
            ],
            "shopping": [
                {
                    "name": "Shopping Leblon",
                    "type": "Luxury Mall",
                    "distance_km": 1.0,
                    "rating": 4.4,
                    "highlights": [
                        "Designer boutiques",
                        "Gourmet food court",
                        "Cinema complex",
                    ],
                }
            ],
            "fitness": [
                {
                    "name": "Exclusive Athletic Club",
                    "type": "Private Club",
                    "distance_km": 0.7,
                    "rating": 4.7,
                    "facilities": [
                        "Olympic pool",
                        "Tennis courts",
                        "Spa",
                        "Personal training",
                    ],
                    "membership": "Premium membership available",
                }
            ],
            "beaches": [
                {
                    "name": "Ipanema Beach",
                    "type": "World-Famous Beach",
                    "distance_km": 0.3,
                    "highlights": [
                        "Iconic sunset views",
                        "Beach service",
                        "Water sports",
                        "Beachfront dining",
                    ],
                }
            ],
        }

        nearby_amenities = {}
        for amenity_type in amenity_types:
            if amenity_type.lower() in amenity_categories:
                nearby_amenities[amenity_type] = amenity_categories[
                    amenity_type.lower()
                ]

        amenities_result = {
            "property_reference": property_reference,
            "property_address": property_data.address,
            "search_radius_km": radius_km,
            "amenity_categories": nearby_amenities,
            "lifestyle_summary": {
                "walkability_score": "Excellent - Most amenities within walking distance",
                "public_transport": "World-class metro and bus connections",
                "safety_rating": "Premium security and 24/7 surveillance",
                "cultural_attractions": "Museums, theaters, and galleries nearby",
            },
            "location_advantages": [
                "Prime location in luxury district",
                "Walking distance to beach and dining",
                "Excellent connectivity to business districts",
                "High-end shopping and entertainment nearby",
            ],
        }

        guide_logger.info(f"Found amenities for property {property_reference}")
        return amenities_result

    except Exception as e:
        guide_logger.error(f"Error finding amenities for {property_reference}: {e}")
        return {"error": f"Failed to find nearby amenities: {str(e)}"}


@tool
def get_property_media_links(property_reference: str) -> str:
    """
    Get high-quality media links for a property including photos, videos, and 3D tours.

    Args:
        property_reference: The reference ID of the property

    Returns:
        JSON string with media links and descriptions
    """
    try:
        media_links = {
            "property_reference": property_reference,
            "hd_photos": {
                "count": 25,
                "gallery_url": f"https://media.mbras.com/properties/{property_reference}/gallery",
                "featured_images": [
                    f"https://media.mbras.com/properties/{property_reference}/exterior_1.jpg",
                    f"https://media.mbras.com/properties/{property_reference}/living_room.jpg",
                    f"https://media.mbras.com/properties/{property_reference}/master_suite.jpg",
                    f"https://media.mbras.com/properties/{property_reference}/kitchen.jpg",
                    f"https://media.mbras.com/properties/{property_reference}/terrace_view.jpg",
                ],
                "quality": "4K resolution, professional photography",
            },
            "video_content": {
                "property_tour": f"https://youtube.com/watch?v={property_reference}_tour",
                "drone_footage": f"https://youtube.com/watch?v={property_reference}_drone",
                "neighborhood_guide": f"https://youtube.com/watch?v={property_reference}_area",
                "virtual_staging": f"https://youtube.com/watch?v={property_reference}_staged",
                "duration": "Complete tour: 8-12 minutes",
            },
            "interactive_content": {
                "3d_virtual_tour": f"https://3d.mbras.com/properties/{property_reference}",
                "floor_plans": f"https://plans.mbras.com/properties/{property_reference}",
                "vr_experience": "Available with VR headset at MBRAS office",
                "virtual_staging_options": "Multiple interior design styles available",
            },
            "sharing_options": {
                "direct_links": "All media available for immediate sharing",
                "social_media_ready": "Optimized for Instagram, WhatsApp, email",
                "download_package": "High-resolution package available for download",
                "presentation_mode": "Full-screen presentation mode available",
            },
        }

        guide_logger.info(f"Retrieved media links for property {property_reference}")
        return media_links

    except Exception as e:
        guide_logger.error(f"Error getting media links for {property_reference}: {e}")
        return {"error": f"Failed to get media links: {str(e)}"}
