from django.urls import path, include
from . import views

urlpatterns = [
    
path("create/", views.create_caregiver_profile, name="create_caregiver_profile"),
path("<int:pk>/", views.caregiver_profile_detail, name="caregiver"),
path("<intLpk>",views.caregiver_list_services, name="services")
]
