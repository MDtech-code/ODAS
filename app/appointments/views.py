# views.py
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from app.account.models import Doctor, DoctorAvailability,PaymentMethod
from .models import Appointment,Payment,Prescription
from django.db.models import Q
from datetime import datetime
import requests
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

def get_payment_url(payment_type):
    """ Return the appropriate URL based on the payment type """
    if payment_type == 'jazzcash':
        return 'https://www.jazzcash.com'
    elif payment_type == 'easypaisa':
        return 'https://www.easypaisa.com'
    elif payment_type == 'bank_account':
        return 'https://www.yourbank.com'
    elif payment_type == 'credit_card':
        return 'https://www.paymentgateway.com'
    return '#'

def check_availability(request):
    doctor_name = request.GET.get('doctor_name')
    selected_date = request.GET.get('date')

    # Fetch the doctor
    try:
        doctor = Doctor.objects.get(user__username=doctor_name)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)

    # Parse the selected date
    try:
        date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    # Determine the day of the week (0 = Monday, 6 = Sunday)
    # day_of_week = date_obj.weekday()
    # Adjust for your model's definition of the day_of_week
    day_of_week = (date_obj.weekday() + 1) % 7  # This maps Monday=1, ..., Sunday=0

    # Fetch all availability slots for the given doctor and day of the week
    availability = DoctorAvailability.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week
    )
    print(f"Availability slots for {doctor_name} on day {day_of_week}: {[{'start_time': slot.start_time, 'end_time': slot.end_time} for slot in availability]}")

    # Fetch all booked appointments for the selected date
    booked_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_start_datetime__date=date_obj
    ).values_list('appointment_start_datetime', 'appointment_end_datetime')

    # Convert booked appointments into a list of time ranges
    booked_time_ranges = [
        (appt[0].time(), appt[1].time()) for appt in booked_appointments
    ]

    # Filter out slots that overlap with booked appointments
    available_slots = []
    for slot in availability:
        # Check if the slot overlaps with any booked time range
        is_overlapping = any(
            slot.start_time < booked_end and slot.end_time > booked_start
            for booked_start, booked_end in booked_time_ranges
        )

        # Only include slots that do not overlap
        if not is_overlapping:
            available_slots.append({
                'date': date_obj.strftime('%d-%m-%Y'),  # Include the selected date
                'start_time': slot.start_time.strftime('%H:%M'),  # Start time in 24-hour format
            })
    # Debug print statements to check the available_slots and consultation_fee
    print(f"Available slots for {doctor_name} on {selected_date}: {available_slots}")
    print(f"Consultation fee: {doctor.consultation_fee if doctor.consultation_fee else 0}")
    # Add the consultation fee to the response
    # Fetch payment methods for this doctor
    payment_methods = PaymentMethod.objects.filter(doctor=doctor)
    payment_buttons = []
    for payment in payment_methods:
        payment_buttons.append({
            'payment_type': payment.get_payment_type_display(),
            'payment_url': get_payment_url(payment.payment_type),  # You can define this function to return the correct URL
        })
    context={
            'available_slots': available_slots,
            'consultation_fee': doctor.consultation_fee if doctor.consultation_fee else 0,
            'payment_methods': payment_buttons 
        }

    return JsonResponse(context)

@login_required
def appointment_view(request):
    user = request.user
    app_active = []
    app_upcoming = []
    app_completed = []

    if user.is_patient():
        appointments = Appointment.objects.filter(patient__user=user).select_related('doctor')
        print(f"Appointments fetched for patient {user}: {appointments}")
    elif user.is_doctor():
        appointments = Appointment.objects.filter(doctor__user=user).select_related('patient')
        print(f"Appointments fetched for doctor {user}: {appointments}")
    else:
        appointments = []
        print(f"No appointments fetched for user {user}.")

    # Categorize appointments
    now = timezone.now()
    current_time = now
    print(f"Current time: {current_time}")
    
    for appointment in appointments:
        print(f"Checking appointment: {appointment}")
        print(f"Status: {appointment.status}, Start Time: {appointment.appointment_start_datetime}, End Time: {appointment.appointment_end_datetime}")

        if appointment.status == 'completed':
            print(f"Appointment {appointment.id} categorized as completed.")
            app_completed.append(appointment)
        elif appointment.status in ['pending', 'confirmed'] and appointment.appointment_start_datetime <= current_time <= appointment.appointment_end_datetime:
            print(f"Appointment {appointment.id} categorized as active.")
            app_active.append(appointment)
        elif appointment.status in ['pending', 'confirmed'] and appointment.appointment_start_datetime > current_time:
            print(f"Appointment {appointment.id} categorized as upcoming.")
            app_upcoming.append(appointment)

    print(f"Active appointments: {app_active}")
    print(f"Upcoming appointments: {app_upcoming}")
    print(f"Completed appointments: {app_completed}")

    context = {
        'app_active': app_active,
        'app_upcoming': app_upcoming,
        'app_over': app_completed,
    }
    return render(request, 'appointments/appointment.html', context)

# @login_required
# def appointment_view(request):
#     user = request.user
#     app_active = []
#     app_upcoming = []
#     app_completed = []

#     if user.is_patient():
#         appointments = Appointment.objects.filter(patient__user=user).select_related('doctor')
#     elif user.is_doctor():
#         appointments = Appointment.objects.filter(doctor__user=user).select_related('patient')
#     else:
#         appointments = []

#     # Categorize appointments
#     for appointment in appointments:
#         if appointment.status == 'completed':
#             app_completed.append(appointment)
#         elif appointment.status in ['pending', 'confirmed'] and appointment.appointment_start_datetime <= now() <= appointment.appointment_end_datetime:
#             app_active.append(appointment)
#         elif appointment.status in ['pending', 'confirmed'] and appointment.appointment_start_datetime > now():
#             app_upcoming.append(appointment)

#     context = {
#         'app_active': app_active,
#         'app_upcomming': app_upcoming,
#         'app_over': app_completed,
#     }
#     return render(request, 'appointments/appointment.html', context)


@login_required
@csrf_exempt
def manage_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)

    if request.method == "POST":
        doctor_notes = request.POST.get("doctor_notes")
        prescription_file = request.FILES.get("prescription_file")

        prescription, created = Prescription.objects.get_or_create(appointment=appointment)
        prescription.doctor_notes = doctor_notes
        if prescription_file:
            prescription.prescription_file = prescription_file
        prescription.save()

        return JsonResponse({"message": "Prescription saved successfully."})

    elif request.method == "DELETE":
        prescription = get_object_or_404(Prescription, appointment=appointment)
        prescription.delete()
        return JsonResponse({"message": "Prescription deleted successfully."})

    return JsonResponse({"message": "Invalid request method."}, status=400)
#! payment 






def initiate_payment(request):
    """
    Initiates the payment process based on the selected payment method.
    Creates a Payment object in the database to track the transaction.
    """
    if request.method == 'POST':
        data = json.loads(request.body)

        # Extract relevant data from the request
        slot_id = data.get('slot_id')
        appointment = Appointment.objects.get(id=slot_id)
        amount = appointment.consultation_fee
        payment_method = data.get('payment_method')

        # Initialize payment response variables
        payment_url = None
        transaction_reference = None

        # Check the payment method and initiate the corresponding payment
        if payment_method == 'jazzcash':
            # JazzCash Payment Details
            payload = {
                'merchant_id': settings.JAZZCASH_MERCHANT_ID,
                'amount': str(amount),
                'slot_id': slot_id,
                'payment_method': payment_method,
                'callback_url': f"{settings.FRONTEND_URL}/payment/callback/",
                'notify_url': f"{settings.FRONTEND_URL}/payment/notify/",  # Optional for async
                'secret_key': settings.JAZZCASH_SECRET_KEY
            }
            # Send request to JazzCash API
            response = requests.post(settings.JAZZCASH_API_URL, data=payload, headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                response_data = response.json()
                payment_url = response_data.get('payment_url')
                transaction_reference = response_data.get('transaction_reference')

        elif payment_method == 'easypaisa':
            # Easypaisa Payment Details (Example)
            payload = {
                'merchant_id': settings.EASYPAY_MERCHANT_ID,
                'amount': str(amount),
                'slot_id': slot_id,
                'payment_method': payment_method,
                'callback_url': f"{settings.FRONTEND_URL}/payment/callback/",
                'notify_url': f"{settings.FRONTEND_URL}/payment/notify/",  # Optional for async
                'secret_key': settings.EASYPAY_SECRET_KEY
            }
            # Send request to Easypaisa API (Example)
            response = requests.post(settings.EASYPAY_API_URL, data=payload, headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                response_data = response.json()
                payment_url = response_data.get('payment_url')
                transaction_reference = response_data.get('transaction_reference')

        elif payment_method == 'bank_transfer':
            # Bank Transfer Payment Details (Manual handling)
            # In this case, the payment URL might not be required, but you can still create the payment record
            transaction_reference = f'BANK{slot_id}'  # Example reference for bank transfer
            payment_url = None  # No direct URL for bank transfer

        elif payment_method == 'credit_card':
            # Credit/Debit Card Payment Details (Integration with a payment gateway like Stripe or PayPal)
            payload = {
                'merchant_id': settings.CARD_PAYMENT_MERCHANT_ID,
                'amount': str(amount),
                'slot_id': slot_id,
                'payment_method': payment_method,
                'callback_url': f"{settings.FRONTEND_URL}/payment/callback/",
                'secret_key': settings.CARD_PAYMENT_SECRET_KEY
            }
            # Example API request to payment gateway
            response = requests.post(settings.CARD_PAYMENT_API_URL, data=payload, headers={'Content-Type': 'application/json'})
            if response.status_code == 200:
                response_data = response.json()
                payment_url = response_data.get('payment_url')
                transaction_reference = response_data.get('transaction_reference')

        # Handle the response and create the payment record
        if payment_url:
            # Create a Payment object in the database
            payment = Payment.objects.create(
                appointment=appointment,
                amount=amount,
                payment_method=payment_method,
                transaction_reference=transaction_reference,
                is_paid=False
            )
            return JsonResponse({'payment_url': payment_url})
        else:
            return JsonResponse({'error': 'Payment initiation failed'}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)

# @csrf_exempt
# def initiate_payment(request):
#     """
#     Initiates the payment process by sending a request to the JazzCash API.
#     Creates a Payment object in the database to track the transaction.
#     """
#     if request.method == 'POST':
#         data = json.loads(request.body)

#         # Extract relevant data from the request
#         slot_id = data.get('slot_id')
#         appointment = Appointment.objects.get(id=slot_id)
#         amount = appointment.consultation_fee
#         payment_method = data.get('payment_method')

#         # Prepare JazzCash Payment Details
#         payload = {
#             'merchant_id': settings.JAZZCASH_MERCHANT_ID,
#             'amount': str(amount),
#             'slot_id': slot_id,
#             'payment_method': payment_method,
#             'callback_url': f"{settings.FRONTEND_URL}/payment/callback/",
#             'notify_url': f"{settings.FRONTEND_URL}/payment/notify/",  # Optional for async
#             'secret_key': settings.JAZZCASH_SECRET_KEY
#         }

#         jazzcash_api_url = settings.JAZZCASH_API_URL
#         response = requests.post(jazzcash_api_url, data=payload, headers={'Content-Type': 'application/json'})

#         if response.status_code == 200:
#             response_data = response.json()
#             payment_url = response_data.get('payment_url')

#             if payment_url:
#                 # Create Payment object in the database
#                 payment = Payment.objects.create(
#                     appointment=appointment,
#                     amount=amount,
#                     payment_method=payment_method,
#                     transaction_reference=response_data.get('transaction_reference'),
#                     is_paid=False
#                 )

#                 return JsonResponse({'payment_url': payment_url})
#             else:
#                 return JsonResponse({'error': 'Payment initiation failed'}, status=400)

#         else:
#             return JsonResponse({'error': 'Failed to contact JazzCash API'}, status=500)

#     return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def payment_callback(request):
    """
    Callback to handle the response after the user completes the payment.
    Updates the Payment and Appointment statuses.
    """
    if request.method == 'POST':
        data = request.POST
        payment_status = data.get('payment_status')
        transaction_id = data.get('transaction_id')

        try:
            # Look up the payment by the transaction reference (transaction_id)
            payment = Payment.objects.get(transaction_reference=transaction_id)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)

        if payment_status == 'success':
            # Mark the payment as completed
            payment.is_paid = True
            payment.payment_status = 'Success'
            payment.payment_date = timezone.now()
            payment.save()

            # Update the appointment status if the payment is successful
            appointment = payment.appointment
            appointment.status = 'confirmed'
            appointment.save()

            return JsonResponse({'status': 'Payment successful'})
        else:
            # Mark the payment as failed
            payment.is_paid = False
            payment.payment_status = 'Failed'
            payment.save()

            return JsonResponse({'status': 'Payment failed'}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def payment_notify(request):
    """
    Notification endpoint to handle asynchronous notifications from JazzCash.
    Updates the Payment status if needed.
    """
    if request.method == 'POST':
        data = request.POST
        transaction_reference = data.get('transaction_reference')
        payment_status = data.get('payment_status')

        try:
            payment = Payment.objects.get(transaction_reference=transaction_reference)
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'Payment not found'}, status=404)

        # Update the Payment status based on the notification
        if payment_status == 'success':
            payment.is_paid = True
            payment.payment_status = 'Success'
            payment.save()

            # Optionally, you could also update the appointment status here if needed
            appointment = payment.appointment
            appointment.status = 'confirmed'
            appointment.save()

        return JsonResponse({'status': 'Received'})
    return JsonResponse({'error': 'Invalid method'}, status=405)


# @csrf_exempt
# def initiate_payment(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)

#         slot_id = data.get('slot_id')
#         amount = data.get('amount')
#         payment_method = data.get('payment_method')

#         # Prepare JazzCash Payment Details
#         payload = {
#             'merchant_id': settings.JAZZCASH_MERCHANT_ID,
#             'amount': amount,
#             'slot_id': slot_id,
#             'payment_method': payment_method,
#             'callback_url': f"{settings.FRONTEND_URL}/payment/callback/",  # Your callback URL
#             'secret_key': settings.JAZZCASH_SECRET_KEY  # Use secret key for security
#         }

#         # Call JazzCash API to initiate the payment (example: sandbox)
#         jazzcash_api_url = settings.JAZZCASH_API_URL  # Make sure this is the correct URL

#         response = requests.post(jazzcash_api_url, data=payload, headers={'Content-Type': 'application/json'})

#         if response.status_code == 200:
#             # Parse the response from JazzCash and redirect user to the payment page
#             response_data = response.json()
#             payment_url = response_data.get('payment_url')

#             if payment_url:
#                 return JsonResponse({'payment_url': payment_url})
#             else:
#                 return JsonResponse({'error': 'Payment initiation failed'}, status=400)

#         else:
#             return JsonResponse({'error': 'Failed to contact JazzCash API'}, status=500)

#     return JsonResponse({'error': 'Invalid method'}, status=405)



# # views.py (Handling payment callback)

# @csrf_exempt
# def payment_callback(request):
#     if request.method == 'POST':
#         data = request.POST

#         # Parse payment data from JazzCash's response
#         payment_status = data.get('payment_status')
#         transaction_id = data.get('transaction_id')

#         if payment_status == 'success':
#             # Update payment status in database
#             # Redirect user or show confirmation message
#             return JsonResponse({'status': 'Payment successful'})
#         else:
#             return JsonResponse({'status': 'Payment failed'}, status=400)

#     return JsonResponse({'error': 'Invalid method'}, status=405)





# def create_payment_request(request, appointment_id):
#     # Get the appointment details
#     appointment = Appointment.objects.get(id=appointment_id)
#     amount = appointment.consultation_fee

#     # Prepare the payload for JazzCash API
#     payload = {
#         'shortcode': settings.JAZZCASH_SHORTCODE,
#         'account_number': appointment.payment_method.account_number,
#         'amount': str(amount),
#         'currency': 'PKR',
#         'transaction_reference': f'APP{appointment.id}',  # Unique reference
#         'merchant_id': settings.JAZZCASH_MERCHANT_ID,
#         'password': settings.JAZZCASH_PASSWORD,
#         'return_url': 'https://your_website.com/payment/return/',  # JazzCash will redirect here after payment
#         'notify_url': 'https://your_website.com/payment/notify/',  # Optional
#     }

#     # Send request to JazzCash API (for example, using POST)
#     response = requests.post(settings.JAZZCASH_API_URL, data=payload)

#     # Check the response from JazzCash
#     if response.status_code == 200:
#         # Parse the response if successful
#         response_data = response.json()
#         if response_data['status'] == 'success':
#             # Create a Payment object with status as 'pending'
#             payment = Payment.objects.create(
#                 appointment=appointment,
#                 amount=amount,
#                 payment_method=appointment.payment_method,
#                 is_paid=False,
#                 transaction_reference=response_data['transaction_reference'],
#             )

#             # Redirect the user to the payment page (or display JazzCash's payment form)
#             return JsonResponse({
#                 'status': 'success',
#                 'payment_url': response_data['payment_url'],  # URL to JazzCash payment page
#             })
#         else:
#             return JsonResponse({'status': 'failed', 'message': 'Payment request failed.'})
#     else:
#         return JsonResponse({'status': 'failed', 'message': 'Error connecting to JazzCash API.'})
    



# def payment_return(request):
#     # Get the response parameters sent by JazzCash (e.g., status, transaction_reference, etc.)
#     transaction_reference = request.GET.get('transaction_reference')
#     status = request.GET.get('status')

#     # Look up the payment based on the transaction reference
#     try:
#         payment = Payment.objects.get(transaction_reference=transaction_reference)
#     except Payment.DoesNotExist:
#         return JsonResponse({'status': 'failed', 'message': 'Payment not found.'})

#     if status == 'success':
#         payment.is_paid = True
#         payment.payment_status = 'Success'
#         payment.save()

#         # Update the appointment status if payment is successful
#         appointment = payment.appointment
#         appointment.status = 'confirmed'
#         appointment.save()

#         return JsonResponse({'status': 'success', 'message': 'Payment successful.'})
#     else:
#         payment.is_paid = False
#         payment.payment_status = 'Failed'
#         payment.save()

#         return JsonResponse({'status': 'failed', 'message': 'Payment failed.'})



# def payment_notify(request):
#     # Handle JazzCash notifications here if required
#     transaction_reference = request.POST.get('transaction_reference')
#     payment_status = request.POST.get('status')

#     # Log or handle the status update accordingly
#     # You may need to update the Payment status here based on the notification

#     return JsonResponse({'status': 'received'})

# def check_availability(request):
#     doctor_name = request.GET.get('doctor_name')
#     selected_date = request.GET.get('date')

#     # Fetch the doctor
#     try:
#         doctor = Doctor.objects.get(user__username=doctor_name)
#     except Doctor.DoesNotExist:
#         return JsonResponse({'error': 'Doctor not found'}, status=404)

#     # Parse the selected date
#     try:
#         date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'error': 'Invalid date format'}, status=400)

#     # Determine the day of the week (0 = Monday, 6 = Sunday)
#     day_of_week = date_obj.weekday()

#     # Fetch all availability slots for the given doctor and day of the week
#     availability = DoctorAvailability.objects.filter(
#         doctor=doctor,
#         day_of_week=day_of_week
#     )

#     # Fetch all booked appointments for the selected date
#     booked_appointments = Appointment.objects.filter(
#         doctor=doctor,
#         appointment_start_datetime__date=date_obj
#     ).values_list('appointment_start_datetime', 'appointment_end_datetime')

#     # Convert booked appointments into a list of time ranges
#     booked_time_ranges = [
#         (appt[0].time(), appt[1].time()) for appt in booked_appointments
#     ]

#     # Filter out slots that overlap with booked appointments
#     available_slots = []
#     for slot in availability:
#         # Check if the slot overlaps with any booked time range
#         is_overlapping = any(
#             slot.start_time < booked_end and slot.start_time >= booked_start
#             for booked_start, booked_end in booked_time_ranges
#         )

#         # Only include slots that do not overlap
#         if not is_overlapping:
#             available_slots.append({
#                 'date': date_obj.strftime('%d-%m-%Y'),  # Include the selected date
#                 'start_time': slot.start_time.strftime('%H:%M'),  # Start time in 24-hour format
#             })

#     return JsonResponse({'available_slots': available_slots})
# def check_availability(request):
#     doctor_name = request.GET.get('doctor_name')
#     selected_date = request.GET.get('date')

#     # Fetch the doctor
#     try:
#         doctor = Doctor.objects.get(user__username=doctor_name)
#     except Doctor.DoesNotExist:
#         return JsonResponse({'error': 'Doctor not found'}, status=404)

#     # Parse the selected date
#     try:
#         date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'error': 'Invalid date format'}, status=400)

#     # Determine the day of the week (0 = Sunday, 6 = Saturday)
#     day_of_week = date_obj.weekday()

#     # Fetch all availability slots for the given doctor and day of the week
#     availability = DoctorAvailability.objects.filter(
#         doctor=doctor,
#         day_of_week=day_of_week
#     )
#     print(f"Availability slots for {doctor_name} on day {day_of_week}: {[{'start_time': slot.start_time, 'end_time': slot.end_time} for slot in availability]}")
#     # Fetch all booked appointments for the selected date
#     booked_appointments = Appointment.objects.filter(
#         doctor=doctor,
#         appointment_start_datetime__date=date_obj
#     ).values_list('appointment_start_datetime', 'appointment_end_datetime')

#     # Convert booked appointments into a list of time ranges
#     booked_time_ranges = [
#         (appt[0].time(), appt[1].time()) for appt in booked_appointments
#     ]

#     # Filter out slots that overlap with booked appointments
#     available_slots = []
#     for slot in availability:
#         # Check if the slot overlaps with any booked time range
#         is_overlapping = any(
#             slot.start_time < booked_end and slot.end_time > booked_start
#             for booked_start, booked_end in booked_time_ranges
#         )

#         # Only include slots that do not overlap
#         if not is_overlapping:
#             available_slots.append({
#                 'date': date_obj.strftime('%d-%m-%Y'),  # Include the selected date
#                 'start_time': slot.start_time.strftime('%H:%M'),  # Start time in 24-hour format
#                 'end_time': slot.end_time.strftime('%H:%M'),  # End time in 24-hour format
#             })

#     return JsonResponse({'available_slots': available_slots})

# def check_availability(request):
#     doctor_name = request.GET.get('doctor_name')
#     selected_date = request.GET.get('date')

#     try:
#         doctor = Doctor.objects.get(user__username=doctor_name)
#     except Doctor.DoesNotExist:
#         return JsonResponse({'error': 'Doctor not found'}, status=404)

#     # Parse the selected date
#     try:
#         date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'error': 'Invalid date format'}, status=400)

#     # Get the doctor's availability slots for the selected date
#     availability = DoctorAvailability.objects.filter(
#         doctor=doctor,
#         day_of_week=date_obj.weekday()
#     ).exclude(
#         Q(doctor__appointments__appointment_start_datetime__date=date_obj)  # Exclude slots already taken
#     )

#     if availability.exists():
#         available_slots = [
#             {
#                 'date': date_obj.strftime('%d-%m-%Y'),  # Include the selected date
#                 'start_time': slot.start_time.strftime('%H:%M'),  # Include start time in 24-hour format
#             }
#             for slot in availability
#         ]
#         return JsonResponse({'available_slots': available_slots})
#     else:
#         return JsonResponse({'available_slots': []})
# def check_availability(request):
#     doctor_name = request.GET.get('doctor_name')
#     selected_date = request.GET.get('date')

#     try:
#         doctor = Doctor.objects.get(user__username=doctor_name)
#     except Doctor.DoesNotExist:
#         return JsonResponse({'error': 'Doctor not found'}, status=404)

#     # Parse the selected date
#     try:
#         date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'error': 'Invalid date format'}, status=400)

#     # Get the doctor's availability slots for the selected date
#     availability = DoctorAvailability.objects.filter(
#         doctor=doctor,
#         day_of_week=date_obj.weekday()
#     ).exclude(
#         Q(doctor__appointments__appointment_start_datetime__date=date_obj)  # Exclude slots already taken
#     )

#     if availability.exists():
#         available_slots = [
#             {
#                 'start_time': slot.start_time.strftime('%H:%M'),
#                 'end_time': slot.end_time.strftime('%H:%M')
#             }
#             for slot in availability
#         ]
#         return JsonResponse({'available_slots': available_slots})
#     else:
#         return JsonResponse({'available_slots': []})
