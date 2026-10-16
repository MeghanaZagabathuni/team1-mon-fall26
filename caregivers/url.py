from django.urls import path, include
from . import views

urlpatterns = [
    
path("create/", views.create_caregiver_profile, name="create_caregiver_profile"),

]
