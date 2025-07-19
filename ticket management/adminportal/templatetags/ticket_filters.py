from django import template

register = template.Library()

@register.filter
def ticket_status_color(status):
    color_map = {
        'pending': 'warning',
        'assigned': 'info',
        'in_progress': 'primary',
        'completed': 'success',
        'closed': 'secondary',
        'rejected': 'danger',
    }
    return color_map.get(status.lower(), 'light')



@register.filter
def priority_color(priority):
    color_map = {
        'low': 'success',
        'medium': 'warning',
        'high': 'danger',
        'urgent': 'dark',
    }
    return color_map.get(priority.lower(), 'secondary')
