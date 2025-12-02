from datetime import datetime
from pathlib import Path
from typing import Any, Dict

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    raise ImportError(
        "Jinja2 is required for email templating. Install with: pip install Jinja2"
    )

from src.infrastructure.lib.logger import guide_logger


class EmailTemplateEngine:
    """
    Email template rendering engine using Jinja2 for dynamic content generation.
    Supports the MBRAS email template system with Tailwind CSS styling.
    """

    def __init__(self):
        self.template_dir = Path(__file__).parent / "email"
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters["currency"] = self._format_currency
        self.env.filters["date_format"] = self._format_date

        guide_logger.info(
            f"EmailTemplateEngine initialized with template directory: {self.template_dir}"
        )

    def _format_currency(self, value: str) -> str:
        """Format currency values for Brazilian Real"""
        if not value:
            return "Consulte"

        # If already formatted, return as is
        if "R$" in str(value):
            return str(value)

        # Try to extract numeric value and format
        try:
            # Remove non-numeric characters except dots and commas
            numeric_str = "".join(c for c in str(value) if c.isdigit() or c in ".,")
            if numeric_str:
                # Convert to float and format
                numeric_value = float(numeric_str.replace(",", "."))
                return f"R$ {numeric_value:,.0f}".replace(",", ".")
        except (ValueError, TypeError):
            pass

        return str(value)

    def _format_date(self, date_value: Any, format_str: str = "%d/%m/%Y") -> str:
        """Format date values"""
        if isinstance(date_value, str):
            return date_value
        if hasattr(date_value, "strftime"):
            return date_value.strftime(format_str)
        return str(date_value)

    def render_portfolio_email(
        self,
        client_name: str,
        client_email: str,
        properties: list,
        pdf_count: int = 0,
        **kwargs,
    ) -> tuple[str, str]:
        """
        Render the portfolio email template.

        Args:
            client_name: Name of the client
            client_email: Email address of the client
            properties: List of property dictionaries
            pdf_count: Number of PDF attachments
            **kwargs: Additional template variables

        Returns:
            tuple: (html_content, text_content)
        """
        try:
            template = self.env.get_template("portfolio.html")

            context = {
                "title": f"Seu Portfólio Personalizado MBRAS - {len(properties)} Propriedades",
                "client_name": client_name,
                "recipient_email": client_email,
                "properties": properties,
                "properties_count": len(properties),
                "pdf_count": pdf_count,
                "current_year": datetime.now().year,
                **kwargs,
            }

            html_content = template.render(**context)
            text_content = self._generate_text_version(context)

            guide_logger.info(
                f"Portfolio email rendered for {client_name} with {len(properties)} properties"
            )
            return html_content, text_content

        except Exception as e:
            guide_logger.error(f"Error rendering portfolio email template: {e}")
            raise

    def render_viewing_confirmation_email(
        self,
        client_name: str,
        client_email: str,
        property_reference: str,
        property_address: str,
        viewing_date: str,
        viewing_time: str,
        appointment_id: str,
        **kwargs,
    ) -> tuple[str, str]:
        """
        Render the viewing confirmation email template.

        Args:
            client_name: Name of the client
            client_email: Email address of the client
            property_reference: Property reference ID
            property_address: Property address
            viewing_date: Scheduled viewing date
            viewing_time: Scheduled viewing time
            appointment_id: Unique appointment identifier
            **kwargs: Additional template variables

        Returns:
            tuple: (html_content, text_content)
        """
        try:
            template = self.env.get_template("viewing_confirmation.html")

            context = {
                "title": f"Confirmação de Visita - {property_reference}",
                "client_name": client_name,
                "recipient_email": client_email,
                "property_reference": property_reference,
                "property_address": property_address,
                "viewing_date": viewing_date,
                "viewing_time": viewing_time,
                "appointment_id": appointment_id,
                "current_year": datetime.now().year,
                **kwargs,
            }

            html_content = template.render(**context)
            text_content = self._generate_viewing_text_version(context)

            guide_logger.info(
                f"Viewing confirmation email rendered for {client_name}, property {property_reference}"
            )
            return html_content, text_content

        except Exception as e:
            guide_logger.error(
                f"Error rendering viewing confirmation email template: {e}"
            )
            # Return basic template if main template fails
            return self._render_fallback_viewing_email(
                context
            ), self._generate_viewing_text_version(context)

    def render_welcome_email(
        self,
        client_name: str,
        client_email: str,
        **kwargs,
    ) -> tuple[str, str]:
        """
        Render the welcome email template for new clients.

        Args:
            client_name: Name of the client
            client_email: Email address of the client
            **kwargs: Additional template variables

        Returns:
            tuple: (html_content, text_content)
        """
        try:
            template = self.env.get_template("welcome.html")

            context = {
                "title": "Bem-vindo à MBRAS - Real Estate Excellence",
                "client_name": client_name,
                "recipient_email": client_email,
                "current_year": datetime.now().year,
                **kwargs,
            }

            html_content = template.render(**context)
            text_content = self._generate_welcome_text_version(context)

            guide_logger.info(f"Welcome email rendered for {client_name}")
            return html_content, text_content

        except Exception as e:
            guide_logger.error(f"Error rendering welcome email template: {e}")
            raise

    def render_property_inquiry_email(
        self,
        client_name: str,
        client_email: str,
        property_reference: str,
        property_details: dict = None,
        property_highlights: list = None,
        similar_properties: list = None,
        investment_data: dict = None,
        **kwargs,
    ) -> tuple[str, str]:
        """
        Render the property inquiry response email template.

        Args:
            client_name: Name of the client
            client_email: Email address of the client
            property_reference: Property reference ID
            property_details: Dictionary with property details
            property_highlights: List of property highlights
            similar_properties: List of similar properties
            investment_data: Dictionary with investment metrics
            **kwargs: Additional template variables

        Returns:
            tuple: (html_content, text_content)
        """
        try:
            template = self.env.get_template("property_inquiry.html")

            context = {
                "title": f"Sua Consulta sobre {property_reference} - MBRAS",
                "client_name": client_name,
                "recipient_email": client_email,
                "property_reference": property_reference,
                "property_details": property_details or {},
                "property_highlights": property_highlights or [],
                "similar_properties": similar_properties or [],
                "investment_data": investment_data or {},
                "current_year": datetime.now().year,
                **kwargs,
            }

            html_content = template.render(**context)
            text_content = self._generate_property_inquiry_text_version(context)

            guide_logger.info(
                f"Property inquiry email rendered for {client_name}, property {property_reference}"
            )
            return html_content, text_content

        except Exception as e:
            guide_logger.error(f"Error rendering property inquiry email template: {e}")
            raise

    def render_custom_template(
        self, template_name: str, context: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        Render a custom email template.

        Args:
            template_name: Name of the template file (without .html extension)
            context: Template context variables

        Returns:
            tuple: (html_content, text_content)
        """
        try:
            template = self.env.get_template(f"{template_name}.html")

            # Add default context variables
            default_context = {
                "current_year": datetime.now().year,
                "recipient_email": context.get("client_email", ""),
            }
            default_context.update(context)

            html_content = template.render(**default_context)
            text_content = self._generate_text_version(default_context)

            guide_logger.info(
                f"Custom email template '{template_name}' rendered successfully"
            )
            return html_content, text_content

        except Exception as e:
            guide_logger.error(
                f"Error rendering custom email template '{template_name}': {e}"
            )
            raise

    def _generate_text_version(self, context: Dict[str, Any]) -> str:
        """Generate a plain text version of the portfolio email"""
        client_name = context.get("client_name", "Cliente Valorizado")
        properties = context.get("properties", [])

        text_content = f"""
Prezado(a) {client_name},

Obrigado pelo seu interesse nas propriedades MBRAS. Em anexo você encontrará seu portfólio personalizado com {len(properties)} propriedades exclusivas.

PROPRIEDADES EM SEU PORTFÓLIO:
"""

        for prop in properties:
            text_content += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REF: {prop.get("reference", "N/A")}
Endereço: {prop.get("address", "N/A")}
Preço: {self._format_currency(prop.get("price", "Consulte"))}
Área: {prop.get("area", "N/A")}
Quartos: {prop.get("bedrooms", "N/A")}
Banheiros: {prop.get("bathrooms", "N/A")}

{prop.get("description", "Descrição não disponível")}
"""

        text_content += f"""

O QUE ESTÁ INCLUÍDO:
• Apresentações profissionais em PDF
• Fotos HD e tours virtuais das propriedades
• Especificações detalhadas das propriedades
• Destaques do bairro
• Resumo de análise de investimento
• Informações diretas de contato para solicitação de visitas

PRÓXIMOS PASSOS:
Nossa equipe entrará em contato em até 24 horas para discutir agendamentos de visitas e esclarecer qualquer dúvida.

CONTATOS:
Telefone: +55 21 3000-0000
WhatsApp: +55 21 3000-0000
Email: contato@mbras.com

Atenciosamente,
Equipe MBRAS
MBRAS Real Estate - Rio de Janeiro, Brasil

© {context.get("current_year", 2024)} MBRAS Real Estate. Todos os direitos reservados.
"""

    def _generate_welcome_text_version(self, context: Dict[str, Any]) -> str:
        """Generate a plain text version of the welcome email"""
        client_name = context.get("client_name", "Cliente Valorizado")

        return f"""
Bem-vindo(a) à MBRAS!

Prezado(a) {client_name},

É com grande prazer que damos as boas-vindas ao mundo dos imóveis de luxo no Rio de Janeiro.
Você agora faz parte de um seleto grupo de investidores que busca excelência.

POR QUE ESCOLHER A MBRAS?

✓ Propriedades Premium
  Acesso exclusivo aos melhores imóveis em Leblon, Ipanema e Copacabana

✓ Consultoria Especializada
  Equipe experiente para guiar você em cada etapa do investimento

✓ Análise de Investimento
  Relatórios detalhados sobre potencial de valorização e retorno

✓ Serviço Personalizado
  Atendimento 24/7 e acompanhamento completo do processo

SEUS PRÓXIMOS PASSOS:

1. Explore Nosso Portfólio
   Navegue por nossa coleção exclusiva de propriedades premium

2. Agende uma Consulta
   Nossa equipe está pronta para uma conversa personalizada

3. Receba Updates Exclusivos
   Mantenha-se informado sobre novos lançamentos e oportunidades

BENEFÍCIOS EXCLUSIVOS:
• Acesso Prioritário a propriedades antes do lançamento público
• Concierge Service completo para visitas e documentação
• Relatórios VIP com análises de mercado exclusivas

CONTATOS:
Telefone: +55 21 3000-0000
WhatsApp: +55 21 3000-0000
E-mail: contato@mbras.com

Obrigado por escolher a MBRAS. Estamos comprometidos em oferecer uma experiência excepcional
e ajudar você a fazer o melhor investimento imobiliário da sua vida.

Com os melhores cumprimentos,
Equipe MBRAS
Real Estate Excellence Since 2010

© {context.get("current_year", 2024)} MBRAS Real Estate. Todos os direitos reservados.
"""

    def _generate_property_inquiry_text_version(self, context: Dict[str, Any]) -> str:
        """Generate a plain text version of the property inquiry email"""
        client_name = context.get("client_name", "Cliente")
        property_reference = context.get("property_reference", "")
        property_details = context.get("property_details", {})

        text_content = f"""
Obrigado pelo seu interesse!

Prezado(a) {client_name},

Recebemos sua consulta sobre a propriedade {property_reference} e nossa equipe
já está preparando informações detalhadas para você.

PROPRIEDADE CONSULTADA: {property_reference}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        if property_details:
            text_content += f"""
Localização: {property_details.get("address", "Informação em breve")}
Preço: {self._format_currency(property_details.get("price", "Consulte-nos"))}
Área Total: {property_details.get("area", "Informação em breve")}
Layout: {property_details.get("bedrooms", "N/A")} quartos, {property_details.get("bathrooms", "N/A")} banheiros
"""

        text_content += f"""

O QUE ACONTECE AGORA?

1. Próximas 2 horas
   Nossa equipe especializada entrará em contato para entender melhor
   suas necessidades e preferências para esta propriedade.

2. Até 24 horas
   Você receberá um dossiê completo da propriedade incluindo fotos HD,
   plantas, análise de investimento e informações do bairro.

3. Agendamento
   Agendaremos uma visita privada no horário mais conveniente para você,
   com um de nossos consultores especializados.

INSIGHTS DE INVESTIMENTO:
• Valorização anual estimada: 8-12%
• Rendimento de aluguel: 4-6%
• ROI projetado (5 anos): 15-18%

*Projeções baseadas em análise de mercado. Investimentos imobiliários envolvem riscos.

NÃO PODE ESPERAR? FALE CONOSCO AGORA!

Telefone: +55 21 3000-0000
WhatsApp: +55 21 3000-0000
E-mail: contato@mbras.com

Horário de atendimento: Segunda a Sábado, 8h às 20h

Obrigado por confiar na MBRAS! Estamos empolgados em ajudar você a conhecer
melhor esta propriedade excepcional.

Com os melhores cumprimentos,
Equipe MBRAS
Especialistas em Imóveis de Luxo

© {context.get("current_year", 2024)} MBRAS Real Estate. Todos os direitos reservados.
"""

        return text_content.strip()

    def _generate_viewing_text_version(self, context: Dict[str, Any]) -> str:
        """Generate a plain text version of the viewing confirmation email"""
        return f"""
Prezado(a) {context.get("client_name", "Cliente")},

CONFIRMAÇÃO DE VISITA

Sua visita foi confirmada com sucesso!

DETALHES DA VISITA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Propriedade: {context.get("property_reference", "N/A")}
Endereço: {context.get("property_address", "N/A")}
Data: {context.get("viewing_date", "N/A")}
Horário: {context.get("viewing_time", "N/A")}
ID do Agendamento: {context.get("appointment_id", "N/A")}

INSTRUÇÕES IMPORTANTES:
• Chegue 5 minutos antes do horário agendado
• Traga um documento de identificação
• Use roupas e calçados confortáveis
• Sinta-se à vontade para fazer perguntas

Para alterações ou cancelamentos, entre em contato:
Telefone: +55 21 3000-0000
WhatsApp: +55 21 3000-0000
Email: contato@mbras.com

Atenciosamente,
Equipe MBRAS
MBRAS Real Estate - Rio de Janeiro, Brasil

© {context.get("current_year", 2024)} MBRAS Real Estate. Todos os direitos reservados.
"""

    def _render_fallback_viewing_email(self, context: Dict[str, Any]) -> str:
        """Fallback viewing confirmation email if template fails"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Confirmação de Visita - MBRAS</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #1447e6;">MBRAS - Confirmação de Visita</h1>

        <p>Prezado(a) {context.get("client_name", "Cliente")},</p>

        <p>Sua visita foi confirmada com sucesso!</p>

        <div style="background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h3>Detalhes da Visita:</h3>
            <p><strong>Propriedade:</strong> {context.get("property_reference", "N/A")}</p>
            <p><strong>Endereço:</strong> {context.get("property_address", "N/A")}</p>
            <p><strong>Data:</strong> {context.get("viewing_date", "N/A")}</p>
            <p><strong>Horário:</strong> {context.get("viewing_time", "N/A")}</p>
            <p><strong>ID do Agendamento:</strong> {context.get("appointment_id", "N/A")}</p>
        </div>

        <p>Para alterações ou cancelamentos, entre em contato conosco:</p>
        <p><strong>Telefone:</strong> +55 21 3000-0000</p>

        <p>Atenciosamente,<br>
        <strong>Equipe MBRAS</strong></p>
    </div>
</body>
</html>
"""

    def list_available_templates(self) -> list[str]:
        """List all available email templates"""
        try:
            templates = []
            for file_path in self.template_dir.glob("*.html"):
                if file_path.name != "base.html":  # Exclude base template
                    templates.append(file_path.stem)
            return sorted(templates)
        except Exception as e:
            guide_logger.error(f"Error listing available templates: {e}")
            return []

    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists"""
        template_path = self.template_dir / f"{template_name}.html"
        return template_path.exists()


# Singleton instance
_email_template_engine = None


def get_email_template_engine() -> EmailTemplateEngine:
    """Get singleton instance of EmailTemplateEngine"""
    global _email_template_engine
    if _email_template_engine is None:
        _email_template_engine = EmailTemplateEngine()
    return _email_template_engine
