from django import template
register = template.Library()

@register.filter
def get_item(post_data, key):
    return post_data.get(f"answer_{key}", "")
