from django import template

register = template.Library()

@register.filter
def get_by_date(events, date):
    return events.filter(date=date)
