from django import template

register = template.Library()

@register.filter
def status_color(value):
    colors = {
        'pending': 'warning',
        'open': 'primary',
        'closed': 'success',
    }
    return colors.get(value.lower(), 'secondary')


@register.filter
def priority_color(value):
    color_map = {
        'low': 'success',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'dark',
    }
    return color_map.get(value.lower(), 'secondary')