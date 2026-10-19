from django import template

from bookings.views import owner_bookings

register = template.Library()


@register.inclusion_tag("bookings/partials/request_panel_items.html", takes_context=True)
def my_booking_requests(context, limit=3):
    """The owner's latest booking requests, for the "My booking requests" panel."""
    user = context["request"].user
    bookings = owner_bookings(user)[:limit] if user.is_authenticated else []
    return {"bookings": bookings}


@register.filter
def short_name(user):
    """A user's name as "Kat W.", falling back to their username."""
    first = (user.first_name or "").strip()
    last = (user.last_name or "").strip()
    if first and last:
        return f"{first} {last[0]}."
    return first or user.username


@register.filter
def first_name(user):
    """A user's first name, falling back to their username."""
    return (user.first_name or "").strip() or user.username
