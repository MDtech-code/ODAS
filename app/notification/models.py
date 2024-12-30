from django.db import models

# Create your models here.
# notifications/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from app.common.models import TimeStampedModel

User = get_user_model()

class Notification(TimeStampedModel):
    """
    Represents a notification for a user.
    """

    NOTIFICATION_TYPES = (
        ('appointment_created', 'Appointment Created'),
        ('appointment_updated', 'Appointment Updated'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('payment_received', 'Payment Received'),
        ('payment_failed', 'Payment Failed'),
        ('report_uploaded', 'Report Uploaded'),
        ('prescription_created', 'Prescription Created'),
        ('verification_requested', 'Verification Requested'),
        ('verification_approved', 'Verification Approved'),
        ('comment_added', 'Comment Added'),
        ('announcement_published', 'Announcement Published'),
    )

    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='notifications', help_text="The user who receives the notification.")
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, help_text="The type of notification.")
    message = models.CharField(max_length=255, help_text="The notification message.")
    is_read = models.BooleanField(default=False, help_text="Indicates whether the notification has been read.")

    # Generic ForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null = True, blank = True, help_text="The content type of the related object.")
    object_id = models.PositiveIntegerField(null = True, blank = True, help_text="The ID of the related object.")
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.user.username} - {self.get_notification_type_display()}"



'''
# Create a notification linked to an appointment
from django.contrib.contenttypes.models import ContentType
from .models import Notification
from app.appointments.models import Appointment

appointment = Appointment.objects.get(pk=1)  # Get an existing appointment

notification = Notification.objects.create(
    user=appointment.patient.user,
    notification_type='appointment_created',
    message='Your appointment has been created.',
    content_object=appointment,  # Link to the appointment instance
)

# Access the related appointment
related_appointment = notification.content_object
print(related_appointment.appointment_start_datetime)
'''

#! key point about notifications 

# Notification Scenarios
# We will send notifications in the following events:

# Appointment Events

# Patient books an appointment.
# Doctor confirms or cancels an appointment.
# Appointment status changes (confirmed, cancelled, completed).
# Payment Events

# Patient makes a payment.
# Payment reminder (if unpaid).
# Report/Prescription Events

# Patient submits a medical report.
# Doctor uploads a prescription.
# Verification Events

# Doctor uploads a certificate for verification.
# Admin verifies or rejects the certificate.
# Blog Comments

# Patients post comments (requires approval).
# Admin approves/rejects comments.
# General Events

# System updates, reminders, or announcements.