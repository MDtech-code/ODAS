from django.db import models
from app.common.models import TimeStampedModel
from django.core.exceptions import ValidationError

from django.core.validators import MinValueValidator

# Create your models here.
class Appointment(TimeStampedModel):
    """
    Represents a scheduled appointment between a patient and a doctor.
    """
    patient = models.ForeignKey('account.Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('account.Doctor', on_delete=models.CASCADE, related_name='appointments')
    appointment_start_datetime = models.DateTimeField()  # Use DateTimeField for date and time
    appointment_end_datetime = models.DateTimeField(blank=True, null=True) #Add end time for appointment
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True) # Add notes to appointment
    payment_method = models.ForeignKey('account.PaymentMethod', on_delete=models.SET_NULL, null=True, blank=True) # Link to payment method
    

    def __str__(self):
        return f"Appointment for {self.patient.user.username} with {self.doctor.user.username}"
    
class Payment(TimeStampedModel):
    """
    Represents a payment made for an appointment.
    """
    appointment = models.OneToOneField('Appointment', on_delete=models.CASCADE)
    payment_method = models.ForeignKey('account.PaymentMethod', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(0.01)])
    is_paid = models.BooleanField(default=False)
    transaction_reference = models.CharField(max_length=255, blank=True, null=True)  # For JazzCash reference
    payment_status = models.CharField(max_length=50, blank=True, null=True)  # For JazzCash status
    payment_date = models.DateTimeField(blank=True, null=True)  # When the payment was completed

    def clean(self):
        super().clean()
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({'amount': "Amount must be greater than zero."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment for {self.appointment}"

class Prescription(TimeStampedModel):
    """
    Represents a medical prescription given by a doctor for an appointment.
    """
    appointment = models.OneToOneField('Appointment', on_delete=models.CASCADE)
    doctor_notes = models.TextField()
    prescription_file = models.FileField(upload_to="prescriptions/")  # Uploaded prescription PDF or file

    def __str__(self):
        return f"Prescription for {self.appointment.patient.user.username} by Dr. {self.appointment.doctor.user.username}"
