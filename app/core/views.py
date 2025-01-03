
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views  import View
from app.account.models import  Doctor
from django.db.models import Q
from app.appointments.models import Appointment
from django.utils import timezone
#! Home page for patients
def home_patient(request):
    """
    Home page for non-logged-in patients.
    """
    return render(request, "home/home_patient.html",{'user_role': 'patient'})

#! Home page for doctors
def home_doctor(request):
    """
    Home page for non-logged-in doctors.
    """
    return render(request, "home/home_doctor.html",{'user_role': 'doctor'})

#! Dashboard for doctors (requires login)
@login_required
def doctor_dashboard(request):
    """
    Dashboard for logged-in doctor .
    """
    if not request.user.is_doctor:
        return render(request, "home/home_patient.html")  # Redirect to patient page if not a doctor
    upcoming_appointments = Appointment.objects.filter(
      doctor=request.user.doctor,
      appointment_start_datetime__gte=timezone.now()  # Filter for future appointments
    ).order_by('appointment_start_datetime')
    print(upcoming_appointments)
    context = {
      'upcoming_appointments': upcoming_appointments,
    }
    return render(request, "dashboard/doctor_dashboard.html",context)

#! Dashboard for patients (requires login)
# @login_required
# def patient_dashboard(request):
#     """
#     Dashboard for logged-in patients.
#     """
#     if not request.user.is_patient:
#         return render(request, "home/home_doctor.html")  # Redirect to doctor page if not a patient
#     return render(request, "dashboard/patient_dashboard.html")

def user_home(request):

    """
    Redirects users based on their role and authentication status:
    - Non-authenticated users are redirected to home_patient or home_doctor.
    - Authenticated users are redirected to patient or doctor dashboard based on role.
    """

    if request.user.is_authenticated:
        if request.user.is_doctor:
            return render(request, 'dashboard/doctor_dashboard.html')
        else:
            return render(request, 'dashboard/patient_dashboard.html')
    return render(request, 'home/home_patient.html')




def redirect_to_dashboard(request):
   
    if request.user.is_authenticated:
        if request.user.is_doctor:
            return redirect('doctor_dashboard')  
        elif request.user.is_patient:
            return redirect('patient_dashboard')  
    else:
        return redirect('home_patient')  
    


def PatientDashboard(request):
    query = request.GET.get('search', '')
    # Fetch verified doctors with their availability prefetched
    doctors = (
        Doctor.objects.filter(is_verified=True)
        .select_related('speciality', 'user')
        .prefetch_related('availability')
    )
    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |  # Search by first name
            Q(user__last_name__icontains=query) |  # Search by last name
            Q(user__username__icontains=query) |   # Search by username
            Q(speciality__name__icontains=query)   # Search by speciality
        )
    # Add unique days for each doctor's availability
    for doctor in doctors:
        # Ensure unique days by using Python's set()
        doctor.unique_days = sorted(
            set(doctor.availability.values_list('day_of_week', flat=True))
        )
        print(doctor.unique_days)
    context = {
        'doctors': doctors,
        'query': query,
    }

    if not request.user.is_patient:
        return render(request, "home/home_doctor.html")

    return render(request, 'dashboard/patient_dashboard.html', context)
# class PatientDashboard(View):
#     """
#         Dashboard for logged-in patients.
#     """
#     template_name = 'dashboard/patient_dashboard.html'

#     def get(self, request, *args, **kwargs):
#         # Fetch verified doctors and their availability
#         doctors = (
#             Doctor.objects.filter(is_verified=True).select_related('speciality', 'user').prefetch_related('availability')
#         )
        
#         context = {
#             'doctors': doctors,
#         }
#         if not request.user.is_patient:
#             return render(request, "home/home_doctor.html")

#         return render(request, self.template_name, context)