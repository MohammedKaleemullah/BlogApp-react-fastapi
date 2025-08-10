# import bleach
from bleach.css_sanitizer import CSSSanitizer
from bleach.sanitizer import Cleaner

ALLOWED_TAGS = [
    'b', 'i', 'u', 'em', 'strong', 'a', 'p', 'ul', 'ol', 'li', 'br', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'span': ['style'],
}
ALLOWED_STYLES = ['color', 'font-weight', 'text-decoration']

css_sanitizer = CSSSanitizer(allowed_css_properties=ALLOWED_STYLES)

cleaner = Cleaner(
    tags=ALLOWED_TAGS,
    attributes=ALLOWED_ATTRIBUTES,
    css_sanitizer=css_sanitizer,
    strip=True
)

def sanitize_html(content: str) -> str:
    return cleaner.clean(content)
