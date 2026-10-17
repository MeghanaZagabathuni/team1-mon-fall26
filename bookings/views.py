from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingRequestForm
from .models import Booking


def owner_bookings(user):
    """Bookings the signed-in owner made, with the related records preloaded."""
    return Booking.objects.filter(owner=user).select_related(
        "pet__pet_type", "caregiver", "service_type"
    )


@login_required
def booking_create(request):
    if request.method == "POST":
        form = BookingRequestForm(request.POST, owner=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.owner = request.user
            booking.status = Booking.Status.PENDING
            booking.save()
            messages.success(
                request,
                f"Request sent to {booking.caregiver.name}. "
                "It stays Pending until they respond.",
            )
            return redirect(booking)
    else:
        # Pre-select a caregiver or pet when coming from their profile page.
        initial = {
            key: request.GET[key]
            for key in ("caregiver", "pet")
            if request.GET.get(key, "").isdigit()
        }
        form = BookingRequestForm(initial=initial, owner=request.user)
    return render(request, "bookings/booking_form.html", {"form": form})


@login_required
def booking_list(request):
    return render(
        request,
        "bookings/booking_list.html",
        {"bookings": owner_bookings(request.user)},
    )


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(owner_bookings(request.user), pk=pk)
    return render(request, "bookings/booking_detail.html", {"booking": booking})
