from django import template
register = template.Library()

@register.filter
def get_item(post_data, key):
    return post_data.get(f"answer_{key}", "")

@register.filter
def letter_label(value):
    """Convert 1,2,3... to a,b,c... for assessment option labels."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return value
    if 1 <= number <= 26:
        return chr(96 + number)
    return str(number)
