from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from app.account.models import Patient,Report,Doctor,DoctorAvailability,PaymentMethod
from .forms import PatientRegistrationForm,PatientProfileForm,DoctorRegistrationForm,ReportForm,DoctorProfileForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView, PasswordResetView
from django.urls import reverse_lazy
from django.views.generic import CreateView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404,redirect
from django.contrib import messages
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views import View
from django.http import QueryDict
import json
#! patient functionality 
class PatientRegistrationView(FormView):
    template_name = 'account/patient_registration.html'
    form_class = PatientRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Save user and patient profile
        user = form.save()
        Patient.objects.create(
            user=user,
            gender=form.cleaned_data['gender'],
            date_of_birth=form.cleaned_data['date_of_birth'],
            phone_number=form.cleaned_data['phone_number'],
        )

        # Send a welcome email
        send_mail(
            subject="Welcome to the Platform",
            message=f"Hi {user.username}, thank you for registering!",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)
    

class PatientProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Get the logged-in user's patient profile
        patient = get_object_or_404(Patient, user=request.user)
        reports = patient.reports.all()
        print(patient)
        context = {
            'patient': patient,
            'reports':reports,
        }
        return render(request, 'account/profile/patient/patient_profile.html', context)

     
class PatientEditProfileView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientProfileForm
    template_name = 'account/profile/patient/patient_edit_profile.html'
    success_url = '/account/patient/profile'  # Redirect to the same page after update

    def get_object(self, queryset=None):
        # Ensure only the logged-in patient's profile is accessed
        return get_object_or_404(Patient, user=self.request.user)
    

# @method_decorator(csrf_exempt, name='dispatch')
class ReportView(View):
    def post(self, request, *args, **kwargs):
        # Check if we're updating an existing report
        report_id = kwargs.get('report_id')  # Fetch report_id from the URL
        if report_id:
            # Attempt to fetch the existing report for the logged-in patient
            report = get_object_or_404(Report, id=report_id, patient=request.user.patient)
            form = ReportForm(request.POST, request.FILES, instance=report)  # Bind the form to the existing report
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Report updated successfully!'}, status=200)
            return JsonResponse({'error': 'Invalid form data for update'}, status=400)

        # If no report_id, create a new report
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.patient = request.user.patient  # Assign the report to the logged-in patient
            report.save()
            return JsonResponse({'message': 'Report uploaded successfully!'}, status=200)
        return JsonResponse({'error': 'Invalid form data for upload'}, status=400)

    def delete(self, request, report_id):
        # Delete a specific report (must belong to the logged-in patient)
        report = get_object_or_404(Report, id=report_id, patient=request.user.patient)
        report.delete()
        return JsonResponse({'message': 'Report deleted successfully!'}, status=200)







class DoctorRegisterView(CreateView):
    form_class = DoctorRegistrationForm
    template_name = 'account/doctor_registration.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Send welcome email to the doctor
        user = form.instance
        send_mail(
            subject="Welcome to Our Platform",
            message=f"Hi {user.username}, your registration as a doctor was successful!",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return response


class DoctorProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Get the logged-in user's doctor profile
        doctor = get_object_or_404(Doctor, user=request.user)
        print(doctor)
        context = {
            'doctor': doctor,
        }
        return render(request, 'account/profile/doctor/doctor_profile.html', context)

class DoctorEditProfileView(LoginRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorProfileForm
    template_name = 'account/profile/doctor/doctor_edit_profile.html'
    success_url = '/account/doctor/profile'  # Redirect to the same page after update

    def get_object(self, queryset=None):
        # Ensure only the logged-in patient's profile is accessed
        return get_object_or_404(Doctor, user=self.request.user)



@csrf_exempt  # Disable CSRF just for this API (use cautiously in production)
@login_required  # Ensure the user is authenticated
def doctor_availability_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON from the request body
            doctor = request.user.doctor  # Get the currently logged-in doctor

            # Create the DoctorAvailability instance
            DoctorAvailability.objects.create(
                doctor=doctor,
                day_of_week=data["day_of_week"],
                start_time=data["start_time"],
                end_time=data["end_time"],
            )
            return JsonResponse({"success": True, "message": "Availability saved successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    elif request.method == "DELETE":
        try:
            data = json.loads(request.body)  # Parse JSON from the request body
            availability_id = data.get("id")  # Get the availability ID from the request

            # Ensure the availability belongs to the current doctor
            availability = DoctorAvailability.objects.get(id=availability_id, doctor=request.user.doctor)
            availability.delete()

            return JsonResponse({"success": True, "message": "Availability deleted successfully!"})
        except DoctorAvailability.DoesNotExist:
            return JsonResponse({"success": False, "message": "Availability not found."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)



# @csrf_exempt  # Disable CSRF just for this API (use cautiously in production)
# @login_required  # Ensure the user is authenticated
# def payment_methods_api(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         doctor = request.user.doctor

#         PaymentMethod.objects.create(
#             doctor=doctor,
#             payment_type=data["payment_type"],
#             account_number=data.get("account_number"),
#             iban=data.get("iban"),
#             bank_name=data.get("bank_name"),
#             card_number=data.get("card_number"),
#             card_expiry=data.get("card_expiry"),
#             card_holder_name=data.get("card_holder_name"),
#         )
#         return JsonResponse({"success": True, "message": "Payment method saved successfully!"})
#     return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)
@csrf_exempt  # Disable CSRF just for this API (use cautiously in production)
@login_required  # Ensure the user is authenticated
def payment_methods_api(request):
    doctor = request.user.doctor  # Ensure we operate only on the logged-in doctor's data
    
    if request.method == "POST":
        # Handle addition of a new payment method
        data = json.loads(request.body)
        PaymentMethod.objects.create(
            doctor=doctor,
            payment_type=data["payment_type"],
            account_number=data.get("account_number"),
            iban=data.get("iban"),
            bank_name=data.get("bank_name"),
            card_number=data.get("card_number"),
            card_expiry=data.get("card_expiry"),
            card_holder_name=data.get("card_holder_name"),
        )
        return JsonResponse({"success": True, "message": "Payment method saved successfully!"})
    
    elif request.method == "DELETE":
        # Handle deletion of a payment method
        data = json.loads(request.body)
        payment_id = data.get("id")
        try:
            payment_method = PaymentMethod.objects.get(id=payment_id, doctor=doctor)
            payment_method.delete()
            return JsonResponse({"success": True, "message": "Payment method deleted successfully!"})
        except PaymentMethod.DoesNotExist:
            return JsonResponse({"success": False, "message": "Payment method not found."}, status=404)
    
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)

'''
class DoctorProfileView(LoginRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorProfileForm
    template_name = 'account/profile/doctor_profile.html'
    success_url = '/account/profile/doctor_profile/'  # Redirect to the same page after update

    def get_object(self, queryset=None):
        # Ensure only the logged-in doctor's profile is accessed
        return get_object_or_404(Doctor, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        # avaliability section
        context['availability_form'] = DoctorAvailabilityForm()
        context['availabilities'] = DoctorAvailability.objects.filter(doctor=self.get_object())

        # Payment method section
        if doctor.is_verified:
            context['payment_form'] = PaymentMethodForm()
            context['payment_methods'] = PaymentMethod.objects.filter(doctor=doctor)
        else:
            context['payment_methods'] = None  # No payment methods for unverified doctors

        
        return context

    def post(self, request, *args, **kwargs):

        # Handle adding availability
        if 'add_availability' in request.POST:  # Check if the availability form is submitted
            availability_form = DoctorAvailabilityForm(request.POST)
            if availability_form.is_valid():
                availability = availability_form.save(commit=False)
                availability.doctor = self.get_object()
                availability.save()
                messages.success(request, "Availability added successfully.")
            else:
                messages.error(request, "Error adding availability. Please correct the form.")
            return redirect(self.success_url)
        # Handle adding payment method (only for verified doctors)
        if doctor.is_verified and 'add_payment_method' in request.POST:
            payment_form = PaymentMethodForm(request.POST)
            if payment_form.is_valid():
                payment_method = payment_form.save(commit=False)
                payment_method.doctor = doctor
                payment_method.save()
                messages.success(request, "Payment method added successfully.")
            else:
                messages.error(request, "Error adding payment method. Please correct the form.")
            return redirect(self.success_url)
        

        return super().post(request, *args, **kwargs)
    
@login_required
def delete_availability(request, pk):
    doctor = getattr(request.user, 'doctor', None)
    availability = get_object_or_404(DoctorAvailability, pk=pk, doctor=doctor)

    # Ensure only the doctor who owns the availability can delete it
    availability.delete()
    messages.success(request, "Availability deleted successfully.")
    return redirect('doctor-profile')

@login_required
def delete_payment_method(request, pk):
    doctor = getattr(request.user, 'doctor', None)
    payment_method = get_object_or_404(PaymentMethod, pk=pk, doctor=doctor)

    # Ensure only the doctor who owns the payment method can delete it
    payment_method.delete()
    messages.success(request, "Payment method deleted successfully.")
    return redirect('doctor-profile')
'''


#! for doctor and patient login,logout,forget,reset


class CustomLoginView(LoginView):
    template_name = 'account/auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """
        Determines where to redirect users after successful login
        based on their user type (doctor or patient).
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_doctor():
                return reverse_lazy('doctor_dashboard')  # Redirect to doctor dashboard
            elif user.is_patient():
                return reverse_lazy('patient_dashboard')  # Redirect to patient dashboard
        return reverse_lazy('home_patient')  # Default fallback

class PasswordResetView(PasswordResetView):
    template_name = 'account/auth/password_reset.html'
    email_template_name = 'account/auth/password_reset_email.html'
    subject_template_name = 'account/auth/password_reset_subject.txt'
    success_url = reverse_lazy('login')




def custom_logout(request):
    """
    Custom logout view to redirect to the appropriate home page
    based on the user's role before logging out.
    """
    if request.user.is_authenticated:
        # Save the user type before logging out
        user_type = request.user.user_type
        logout(request)
        
        # Redirect based on the saved user type
        if user_type == 'doctor':
            return redirect("home_doctor")
        elif user_type == 'patient':
            return redirect("home_patient")

    # Default redirect for unauthenticated or other cases
    return redirect("home_patient")