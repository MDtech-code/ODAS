from django import template

register = template.Library()

@register.filter
def get_day_display(day):
    """
    Converts the day_of_week integer to its display name.
    """
    days = {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday'
    }
    return days.get(day, 'Unknown')
