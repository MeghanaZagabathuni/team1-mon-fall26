from django import template

from bookings.views import owner_bookings

register = template.Library()


@register.inclusion_tag("bookings/partials/request_panel_items.html", takes_context=True)
def my_booking_requests(context, limit=3):
    """The owner's latest booking requests, for the "My booking requests" panel."""
    user = context["request"].user
    bookings = owner_bookings(user)[:limit] if user.is_authenticated else []
    return {"bookings": bookings}
