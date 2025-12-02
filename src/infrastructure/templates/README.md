# MBRAS Email Template System

This directory contains the email template system for the MBRAS Real Estate API, providing a professional and consistent email experience for all client communications.

## Overview

The email template system uses **Jinja2** templating engine with **Tailwind CSS** styling to create responsive, professional emails that maintain the MBRAS brand identity.

## Features

- 🎨 **Professional Design**: Modern, responsive email templates with MBRAS branding
- 🎯 **Template Engine**: Jinja2-powered dynamic content rendering
- 📱 **Mobile Responsive**: Optimized for desktop, tablet, and mobile devices
- 🌙 **Dark Mode Support**: CSS variables for light/dark theme compatibility
- 🔧 **Modular Architecture**: Base template with extensible blocks
- 📊 **Rich Content**: Support for property listings, images, charts, and interactive elements

## Directory Structure

```
templates/
├── README.md                          # This documentation
├── email_template_engine.py           # Core template engine
└── email/                             # Email templates directory
    ├── base.html                      # Base template with MBRAS styling
    ├── portfolio.html                 # Property portfolio email
    ├── viewing_confirmation.html      # Viewing appointment confirmation
    ├── welcome.html                   # Welcome email for new clients
    └── property_inquiry.html          # Property inquiry response
```

## Available Templates

### 1. Base Template (`base.html`)
The foundation template that includes:
- MBRAS branding and color scheme
- Tailwind CSS integration
- Responsive layout structure
- Header with logo and contact info
- Footer with company details and unsubscribe links

### 2. Portfolio Email (`portfolio.html`)
Professional property portfolio template featuring:
- Property listing cards with images and details
- Summary statistics (property count, PDFs, etc.)
- Feature highlights and benefits
- Call-to-action buttons for contact
- Mobile-optimized property grid

### 3. Viewing Confirmation (`viewing_confirmation.html`)
Appointment confirmation template including:
- Confirmation badge and appointment details
- Property information and location
- Important instructions for the viewing
- What to expect during the visit
- Contact options for changes/cancellations

### 4. Welcome Email (`welcome.html`)
Onboarding template for new clients with:
- Welcome message and MBRAS value proposition
- Next steps guidance
- Exclusive client benefits overview
- Contact information and support options

### 5. Property Inquiry Response (`property_inquiry.html`)
Response template for property inquiries featuring:
- Property summary and key details
- Response timeline and next steps
- Investment insights and projections
- Similar property suggestions
- Immediate contact options

## Usage

### Basic Usage

```python
from src.infrastructure.templates.email_template_engine import get_email_template_engine

# Get the template engine instance
template_engine = get_email_template_engine()

# Render a portfolio email
html_content, text_content = template_engine.render_portfolio_email(
    client_name="João Silva",
    client_email="joao@example.com",
    properties=[
        {
            "reference": "MBRAS001",
            "address": "Rua Exemplo, 123 - Leblon",
            "price": "R$ 2.500.000",
            "area": "120m²",
            "bedrooms": 3,
            "bathrooms": 2,
            "description": "Apartamento com vista para o mar..."
        }
    ],
    pdf_count=1
)
```

### Custom Template Usage

```python
# Render a custom template
html_content, text_content = template_engine.render_custom_template(
    template_name="welcome",
    context={
        "client_name": "Maria Santos",
        "client_email": "maria@example.com",
        "special_offer": True
    }
)
```

## Template Variables

### Common Variables (Available in all templates)
- `client_name`: Client's full name
- `recipient_email`: Client's email address
- `current_year`: Current year (auto-populated)
- `title`: Email subject/title

### Template-Specific Variables

#### Portfolio Email
- `properties`: List of property dictionaries
- `properties_count`: Number of properties in portfolio
- `pdf_count`: Number of PDF attachments

#### Viewing Confirmation
- `property_reference`: Property reference ID
- `property_address`: Property full address
- `viewing_date`: Scheduled viewing date
- `viewing_time`: Scheduled viewing time
- `appointment_id`: Unique appointment identifier

#### Welcome Email
- (Uses only common variables)

#### Property Inquiry
- `property_reference`: Property reference ID
- `property_details`: Property information dictionary
- `property_highlights`: List of property features
- `similar_properties`: List of similar properties
- `investment_data`: Investment metrics dictionary

## Styling System

The templates use a custom CSS system based on MBRAS design tokens:

### Color Variables
```css
/* Light Mode */
--bg-blue: #1447e6;          /* Primary MBRAS blue */
--text-blue-mb: #005292;     /* MBRAS text blue */
--bg-bw: #ffffff;            /* Background white */
--text: #1f1f1f;             /* Primary text color */

/* Dark Mode */
--bg-blue: #2377fd;          /* Lighter blue for dark mode */
--text-blue-mb: #0074d2;     /* Adjusted blue for dark mode */
--bg-bw: #1e2939;            /* Dark background */
--text: #fdfdfd;             /* Light text color */
```

### CSS Classes
- `.mbras-brand`: Primary brand styling (blue background, white text)
- `.mbras-card`: Card styling with border and shadow
- `.mbras-gradient`: MBRAS gradient background
- `.mbras-text-blue`: MBRAS blue text color
- `.mbras-shadow`: Custom shadow with MBRAS blue tint

## Template Development

### Creating New Templates

1. **Create the HTML template**:
   ```html
   {% extends "base.html" %}
   
   {% block content %}
   <!-- Your template content here -->
   <h2>Hello {{ client_name }}!</h2>
   {% endblock %}
   ```

2. **Add template method to engine**:
   ```python
   def render_my_template(self, client_name: str, **kwargs) -> tuple[str, str]:
       template = self.env.get_template("my_template.html")
       context = {
           "client_name": client_name,
           "current_year": datetime.now().year,
           **kwargs
       }
       html_content = template.render(**context)
       text_content = self._generate_my_template_text_version(context)
       return html_content, text_content
   ```

3. **Add text version generator**:
   ```python
   def _generate_my_template_text_version(self, context: Dict[str, Any]) -> str:
       return f"Hello {context.get('client_name', 'Client')}!\n\n..."
   ```

### Design Guidelines

1. **Use the base template**: Always extend `base.html` for consistency
2. **Mobile-first**: Design for mobile devices first, then enhance for larger screens
3. **Accessibility**: Use semantic HTML and proper contrast ratios
4. **Brand consistency**: Use MBRAS color variables and classes
5. **Performance**: Optimize images and minimize inline styles

## Testing Templates

### Template Validation
```python
# Check if template exists
if template_engine.template_exists("my_template"):
    print("Template found!")

# List all available templates
templates = template_engine.list_available_templates()
print(f"Available templates: {templates}")
```

### Email Preview
For development and testing, you can save rendered templates as HTML files:

```python
html_content, _ = template_engine.render_portfolio_email(...)

with open("preview.html", "w", encoding="utf-8") as f:
    f.write(html_content)
```

## Dependencies

- **Jinja2**: Template rendering engine
- **Tailwind CSS**: CSS framework (loaded via CDN)
- **Python 3.8+**: Required for the template engine

## Email Client Compatibility

The templates are tested and compatible with:
- ✅ Gmail (Web, iOS, Android)
- ✅ Outlook (Web, Desktop, Mobile)
- ✅ Apple Mail (macOS, iOS)
- ✅ Yahoo Mail
- ✅ Thunderbird
- ✅ Mobile email clients (iOS Mail, Android Gmail)

## Best Practices

1. **Content**: Keep emails concise and focused
2. **Images**: Use alt text and fallback content
3. **Links**: Use absolute URLs and meaningful anchor text
4. **Testing**: Test across different email clients and devices
5. **Personalization**: Use client names and relevant property information
6. **Call-to-Action**: Make CTAs clear and prominent
7. **Mobile**: Ensure readability on small screens

## Troubleshooting

### Common Issues

1. **Template not found**: Check template name and file extension
2. **Rendering errors**: Verify all required variables are provided
3. **Styling issues**: Ensure CSS variables are properly defined
4. **Mobile display**: Test with actual mobile email clients

### Debug Mode

Enable debug logging to troubleshoot template issues:

```python
import logging
logging.getLogger("src.infrastructure.templates").setLevel(logging.DEBUG)
```

## Support

For questions or issues with the email template system:

1. Check the logs for detailed error messages
2. Verify template syntax and variable names
3. Test with minimal data to isolate issues
4. Contact the development team for assistance

---

**MBRAS Email Template System v1.0**  
*Created with ❤️ for exceptional client communication*