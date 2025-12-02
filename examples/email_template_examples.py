#!/usr/bin/env python3
"""
MBRAS Email Template System - Usage Examples

This script demonstrates how to use the MBRAS email template system
to generate professional emails for different scenarios.

Run this script to see example outputs and test the template system.
"""

# Add the src directory to the path so we can import our modules
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from infrastructure.templates.email_template_engine import get_email_template_engine


def save_example_email(content: str, filename: str, output_dir: Path = None):
    """Save email content to file for preview"""
    if output_dir is None:
        output_dir = Path(__file__).parent / "email_previews"

    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / f"{filename}.html"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Saved: {filepath}")


def example_portfolio_email():
    """Example: Portfolio email with multiple properties"""
    print("\n🏠 PORTFOLIO EMAIL EXAMPLE")
    print("=" * 50)

    template_engine = get_email_template_engine()

    # Sample property data
    properties = [
        {
            "reference": "MBRAS001",
            "address": "Rua Ataulfo de Paiva, 1000 - Leblon, Rio de Janeiro",
            "price": "R$ 3.200.000",
            "area": "150m²",
            "bedrooms": 3,
            "bathrooms": 2,
            "description": "Apartamento de luxo com vista panorâmica para o mar de Ipanema. Acabamentos de primeira linha, varandão gourmet e vaga na escritura. Localizado no coração do Leblon, próximo aos melhores restaurantes e comércios da cidade.",
        },
        {
            "reference": "MBRAS002",
            "address": "Rua Visconde de Pirajá, 500 - Ipanema, Rio de Janeiro",
            "price": "R$ 2.850.000",
            "area": "120m²",
            "bedrooms": 2,
            "bathrooms": 2,
            "description": "Cobertura moderna com terraço privativo e piscina. Vista deslumbrante da praia de Ipanema. Projeto de arquiteto renomado com integração total dos ambientes sociais e muito charme carioca.",
        },
        {
            "reference": "MBRAS003",
            "address": "Avenida Atlântica, 2000 - Copacabana, Rio de Janeiro",
            "price": "R$ 4.100.000",
            "area": "200m²",
            "bedrooms": 4,
            "bathrooms": 3,
            "description": "Apartamento frente mar na Avenida Atlântica. Planta ampla com suíte master, closet, home office e dependências completas. Prédio clássico com portaria 24h e localização privilegiada.",
        },
    ]

    try:
        html_content, text_content = template_engine.render_portfolio_email(
            client_name="João Silva Santos",
            client_email="joao.santos@email.com",
            properties=properties,
            pdf_count=3,
        )

        save_example_email(html_content, "portfolio_example")
        print(f"📧 Portfolio email generated with {len(properties)} properties")
        print(f"📄 Plain text version: {len(text_content)} characters")

    except Exception as e:
        print(f"❌ Error generating portfolio email: {e}")


def example_viewing_confirmation():
    """Example: Viewing confirmation email"""
    print("\n📅 VIEWING CONFIRMATION EMAIL EXAMPLE")
    print("=" * 50)

    template_engine = get_email_template_engine()

    try:
        html_content, text_content = template_engine.render_viewing_confirmation_email(
            client_name="Maria Fernanda Costa",
            client_email="maria.costa@email.com",
            property_reference="MBRAS001",
            property_address="Rua Ataulfo de Paiva, 1000 - Leblon, Rio de Janeiro - RJ",
            viewing_date="15 de Dezembro de 2024",
            viewing_time="14:30",
            appointment_id="VIEW-MBRAS001-202412121430",
        )

        save_example_email(html_content, "viewing_confirmation_example")
        print("✅ Viewing confirmation email generated")
        print("📅 Appointment: 15/12/2024 at 14:30")

    except Exception as e:
        print(f"❌ Error generating viewing confirmation: {e}")


def example_welcome_email():
    """Example: Welcome email for new clients"""
    print("\n👋 WELCOME EMAIL EXAMPLE")
    print("=" * 50)

    template_engine = get_email_template_engine()

    try:
        html_content, text_content = template_engine.render_welcome_email(
            client_name="Carlos Eduardo Mendes", client_email="carlos.mendes@email.com"
        )

        save_example_email(html_content, "welcome_example")
        print("🎉 Welcome email generated for new client")
        print("🔥 Includes MBRAS value proposition and next steps")

    except Exception as e:
        print(f"❌ Error generating welcome email: {e}")


def example_property_inquiry():
    """Example: Property inquiry response email"""
    print("\n❓ PROPERTY INQUIRY EMAIL EXAMPLE")
    print("=" * 50)

    template_engine = get_email_template_engine()

    # Sample property details
    property_details = {
        "address": "Rua Ataulfo de Paiva, 1000 - Leblon, Rio de Janeiro - RJ",
        "price": "R$ 3.200.000",
        "area": "150m²",
        "bedrooms": 3,
        "bathrooms": 2,
    }

    # Sample highlights
    property_highlights = [
        "Vista panorâmica para o mar",
        "Varandão gourmet com churrasqueira",
        "Vaga na escritura",
        "Acabamentos de luxo",
        "Portaria 24h",
        "Localização privilegiada no Leblon",
    ]

    # Sample similar properties
    similar_properties = [
        {
            "reference": "MBRAS002",
            "address": "Rua Visconde de Pirajá - Ipanema",
            "price": "R$ 2.850.000",
            "bedrooms": 2,
            "bathrooms": 2,
            "area": "120m²",
        },
        {
            "reference": "MBRAS004",
            "address": "Rua General Urquiza - Leblon",
            "price": "R$ 3.500.000",
            "bedrooms": 3,
            "bathrooms": 3,
            "area": "160m²",
        },
    ]

    # Sample investment data
    investment_data = {
        "appreciation": "10-15%",
        "rental_yield": "4-5%",
        "roi": "18-22%",
    }

    try:
        html_content, text_content = template_engine.render_property_inquiry_email(
            client_name="Ana Beatriz Oliveira",
            client_email="ana.oliveira@email.com",
            property_reference="MBRAS001",
            property_details=property_details,
            property_highlights=property_highlights,
            similar_properties=similar_properties,
            investment_data=investment_data,
        )

        save_example_email(html_content, "property_inquiry_example")
        print("🏡 Property inquiry response generated")
        print(
            f"📊 Includes investment data and {len(similar_properties)} similar properties"
        )

    except Exception as e:
        print(f"❌ Error generating property inquiry email: {e}")


def example_custom_template():
    """Example: Using custom template rendering"""
    print("\n🎨 CUSTOM TEMPLATE EXAMPLE")
    print("=" * 50)

    template_engine = get_email_template_engine()

    try:
        # List available templates
        templates = template_engine.list_available_templates()
        print(f"📋 Available templates: {templates}")

        # Check if template exists
        template_name = "portfolio"
        exists = template_engine.template_exists(template_name)
        print(f"✅ Template '{template_name}' exists: {exists}")

        # Render using custom template method
        html_content, text_content = template_engine.render_custom_template(
            template_name="welcome",
            context={
                "client_name": "Roberto Silva",
                "client_email": "roberto@example.com",
                "special_message": "Bem-vindo ao programa VIP MBRAS!",
            },
        )

        save_example_email(html_content, "custom_welcome_example")
        print("🎯 Custom template rendering successful")

    except Exception as e:
        print(f"❌ Error with custom template: {e}")


def main():
    """Run all email template examples"""
    print("🏢 MBRAS EMAIL TEMPLATE SYSTEM - EXAMPLES")
    print("=" * 60)
    print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create output directory
    output_dir = Path(__file__).parent / "email_previews"
    print(f"📁 Output directory: {output_dir}")

    # Run all examples
    example_portfolio_email()
    example_viewing_confirmation()
    example_welcome_email()
    example_property_inquiry()
    example_custom_template()

    print("\n" + "=" * 60)
    print("✅ ALL EXAMPLES COMPLETED!")
    print(f"📁 Check the '{output_dir}' directory for HTML previews")
    print("🌐 Open the HTML files in your browser to see the results")
    print("\n💡 TIP: You can modify this script to test your own data")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        sys.exit(1)
