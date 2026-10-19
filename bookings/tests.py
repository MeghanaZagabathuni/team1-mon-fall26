from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from caregivers.models import CaregiverProfile, ServiceType
from pets.models import Pet, PetType

from .forms import BookingRequestForm
from .models import Booking

FMT = "%Y-%m-%dT%H:%M"


class BookingTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user("owner", password="pw-12345!")
        cls.other_owner = User.objects.create_user("other", password="pw-12345!")
        dog = PetType.objects.get_or_create(name="Dog")[0]
        cls.pet = Pet.objects.create(owner=cls.owner, name="Biscuit", pet_type=dog)
        cls.other_pet = Pet.objects.create(
            owner=cls.other_owner, name="Rex", pet_type=dog
        )
        cls.caregiver = CaregiverProfile.objects.create(
            name="Chloe Shih", service_area="Brooklyn"
        )
        # Created by the 0002 data migration.
        cls.walk = ServiceType.objects.get(name="Dog walking")
        cls.sitting = ServiceType.objects.get(name="Pet sitting")

    def form_data(self, **overrides):
        start = timezone.localtime() + timedelta(days=2)
        data = {
            "pet": self.pet.pk,
            "caregiver": self.caregiver.pk,
            "service_type": self.walk.pk,
            "start_time": start.strftime(FMT),
            "end_time": (start + timedelta(hours=1)).strftime(FMT),
            "notes": "Please bring treats.",
        }
        data.update(overrides)
        return data

    def make_booking(self, owner=None, pet=None, **fields):
        start = timezone.now() + timedelta(days=1)
        defaults = {
            "owner": owner or self.owner,
            "pet": pet or self.pet,
            "caregiver": self.caregiver,
            "service_type": self.walk,
            "start_time": start,
            "end_time": start + timedelta(hours=1),
        }
        defaults.update(fields)
        return Booking.objects.create(**defaults)


class BookingModelTests(BookingTestData):
    def test_new_booking_defaults_to_pending(self):
        self.assertEqual(self.make_booking().status, Booking.Status.PENDING)

    def test_default_service_types_exist(self):
        names = set(ServiceType.objects.values_list("name", flat=True))
        self.assertTrue({"Dog walking", "Pet sitting", "Drop-in visit"} <= names)


class BookingRequestFormTests(BookingTestData):
    def make_form(self, **overrides):
        return BookingRequestForm(data=self.form_data(**overrides), owner=self.owner)

    def test_valid_request(self):
        self.assertTrue(self.make_form().is_valid())

    def test_only_owners_pets_are_offered(self):
        form = BookingRequestForm(owner=self.owner)
        self.assertEqual(list(form.fields["pet"].queryset), [self.pet])

    def test_cannot_book_someone_elses_pet(self):
        form = self.make_form(pet=self.other_pet.pk)
        self.assertFalse(form.is_valid())
        self.assertIn("pet", form.errors)

    def test_pet_caregiver_service_and_times_are_required(self):
        form = self.make_form(
            pet="", caregiver="", service_type="", start_time="", end_time=""
        )
        self.assertFalse(form.is_valid())
        for field in ("pet", "caregiver", "service_type", "start_time", "end_time"):
            self.assertIn(field, form.errors)

    def test_start_time_must_be_in_future(self):
        past = timezone.localtime() - timedelta(hours=1)
        form = self.make_form(
            start_time=past.strftime(FMT),
            end_time=(past + timedelta(hours=2)).strftime(FMT),
        )
        self.assertFalse(form.is_valid())
        self.assertIn("start_time", form.errors)

    def test_times_are_entered_in_local_time(self):
        # A time later today in New York must be accepted (not read as UTC).
        soon = timezone.localtime() + timedelta(minutes=30)
        form = self.make_form(
            start_time=soon.strftime(FMT),
            end_time=(soon + timedelta(hours=1)).strftime(FMT),
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_end_time_must_be_after_start(self):
        data = self.form_data()
        form = self.make_form(end_time=data["start_time"])
        self.assertFalse(form.is_valid())
        self.assertIn("end_time", form.errors)

    def test_caregiver_not_accepting_bookings_cannot_be_selected(self):
        self.caregiver.accepting_new_bookings = False
        self.caregiver.save()
        form = self.make_form()
        self.assertFalse(form.is_valid())
        self.assertIn("caregiver", form.errors)

    def test_service_must_be_offered_by_caregiver(self):
        with mock.patch(
            "bookings.forms.offered_service_type_ids", return_value={self.sitting.pk}
        ):
            form = self.make_form()
            self.assertFalse(form.is_valid())
            self.assertIn("service_type", form.errors)

    def test_service_accepted_when_offered_by_caregiver(self):
        with mock.patch(
            "bookings.forms.offered_service_type_ids", return_value={self.walk.pk}
        ):
            self.assertTrue(self.make_form().is_valid())


class BookingCreateViewTests(BookingTestData):
    url = reverse("bookings:booking_create")

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_get_shows_form_with_own_pets_only(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url)
        self.assertContains(response, "Request care")
        self.assertContains(response, "Biscuit")
        self.assertContains(response, "Chloe Shih")
        self.assertContains(response, "Dog walking")
        self.assertNotContains(response, "Rex")

    def test_owner_without_pets_is_asked_to_add_one(self):
        self.client.force_login(get_user_model().objects.create_user("new"))
        response = self.client.get(self.url)
        self.assertContains(response, "Add a pet first")

    def test_caregiver_and_pet_can_be_preselected(self):
        self.client.force_login(self.owner)
        response = self.client.get(
            self.url, {"caregiver": self.caregiver.pk, "pet": self.pet.pk}
        )
        initial = response.context["form"].initial
        self.assertEqual(initial["caregiver"], str(self.caregiver.pk))
        self.assertEqual(initial["pet"], str(self.pet.pk))

    def test_post_saves_pending_booking_and_confirms(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, self.form_data(), follow=True)
        booking = Booking.objects.get()
        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.assertEqual(booking.owner, self.owner)
        self.assertEqual(booking.pet, self.pet)
        self.assertEqual(booking.caregiver, self.caregiver)
        self.assertEqual(booking.service_type, self.walk)
        self.assertRedirects(response, booking.get_absolute_url())
        self.assertContains(response, "Request sent to Chloe Shih")
        self.assertContains(response, "Pending")

    def test_invalid_post_saves_nothing(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, self.form_data(pet=""))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose one of your pets.")
        self.assertFalse(Booking.objects.exists())


class BookingListAndDetailViewTests(BookingTestData):
    def test_list_login_required(self):
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual(response.status_code, 302)

    def test_empty_list(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertContains(response, "No requests yet")

    def test_list_shows_submitted_booking(self):
        self.make_booking()
        self.client.force_login(self.owner)
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertContains(response, "Biscuit · Dog walking")
        self.assertContains(response, "Chloe Shih")
        self.assertContains(response, "Pending")

    def test_owner_sees_only_their_bookings(self):
        self.make_booking()
        other = self.make_booking(owner=self.other_owner, pet=self.other_pet)
        self.client.force_login(self.owner)
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual(len(response.context["bookings"]), 1)
        self.assertNotContains(response, "Rex")
        detail = self.client.get(other.get_absolute_url())
        self.assertEqual(detail.status_code, 404)

    def test_detail_shows_request_details(self):
        booking = self.make_booking(notes="Feed at 6pm")
        self.client.force_login(self.owner)
        response = self.client.get(booking.get_absolute_url())
        self.assertContains(response, "Feed at 6pm")
        self.assertContains(response, "Pending")
        self.assertContains(response, "Chloe Shih")


class BookingPanelTests(BookingTestData):
    def test_my_pets_page_shows_latest_requests(self):
        self.make_booking()
        self.client.force_login(self.owner)
        response = self.client.get(reverse("pets:list"))
        self.assertContains(response, "My booking requests")
        self.assertContains(response, "Biscuit · Dog walking")
        self.assertContains(response, reverse("bookings:booking_create"))

    def test_nav_links_to_my_requests(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("pets:list"))
        self.assertContains(response, f'href="{reverse("bookings:booking_list")}"')
