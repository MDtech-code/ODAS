from django.urls import path
from . import views
urlpatterns = [
    path("", views.home_patient, name="home_patient"),  # Patient home page
    path("doctor/", views.home_doctor, name="home_doctor"),  # Doctor home page
    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),  # Doctor dashboard
    path("patient/dashboard/", views.PatientDashboard, name="patient_dashboard"),  # Patient dashboard
    
    
]
