from django import template

register = template.Library()

@register.simple_tag
def range_tag(start, end):
    """Generate range for loop"""
    return range(start, end + 1)

@register.filter
def get_period_status(record, period):
    """Gets the status dynamically for a given period attribute name."""
    return getattr(record, period, 'Absent')

@register.filter
def is_student(user):
    return hasattr(user, 'student_profile')

@register.filter
def is_staff(user):
    return hasattr(user, 'staff_profile')

@register.filter
def get_period_time(record, period):
    """Gets the entry time dynamically for a given period attribute name."""
    time_attr = f"{period}_time"
    return getattr(record, time_attr, None)
