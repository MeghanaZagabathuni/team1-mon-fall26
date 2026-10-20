from django.urls import path, include
from . import views

urlpatterns = [
    
path("", views.caregiver_list, name="caregiver_list"),
path("create/", views.create_caregiver_profile, name="create_caregiver_profile"),
path("<int:pk>/", views.caregiver_profile_detail, name="caregiver"),
path("<int:pk>/services/", views.caregiver_list_services, name="services"),
path("<int:pk>/services/add/", views.add_caregiver_service, name="add_caregiver_service"),
path("<int:pk>/edit/", views.edit_caregiver_profile, name="edit_caregiver_profile"),
path("<int:pk>/services/<int:service_id>/edit/", views.edit_caregiver_service, name="edit_caregiver_service"),
path("<int:pk>/services/<int:service_id>/delete/", views.delete_caregiver_service, name="delete_caregiver_service"),

]
