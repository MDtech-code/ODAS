from django.shortcuts import render

# Create your views here.
# notifications/views.py

# from django.shortcuts import render
# from app.notification.models import Notification

# def notifications_list(request):
#     notifications = request.user.notifications.filter(is_read=False)
#     return render(request, 'notifications/notifications_list.html', {'notifications': notifications})



#! how to use it 

# # appointment/views.py

# from notifications.utils import send_notification

# def book_appointment(request):
#     # Booking logic here...
#     appointment = Appointment.objects.create(
#         patient=patient,
#         doctor=doctor,
#         appointment_start_datetime=datetime_value,
#     )
#     # Send notification to doctor
#     send_notification(
#         user=doctor.user,
#         notification_type='appointment',
#         message=f"You have a new appointment request from {patient.user.username}.",
#         link=f"/appointments/{appointment.id}/"
#     )

# #appointment/template 
# {% for notification in notifications %}
#     <div class="p-4 border-b">
#         <p>{{ notification.message }}</p>
#         {% if notification.link %}
#             <a href="{{ notification.link }}">View Details</a>
#         {% endif %}
#         <small>{{ notification.created_at }}</small>
#     </div>
# {% empty %}
#     <p>No new notifications</p>
# {% endfor %}
