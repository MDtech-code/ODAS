
from django.db import models
from django.contrib.auth.models import AbstractUser,Group
from app.common.models import TimeStampedModel
from app.account.utils.specialities import SPECIALITIES
import phonenumbers
from phonenumbers import phonenumberutil
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model extending AbstractUser. Provides user type differentiation
    and integrates with Django's permissions system using groups.
    """

    PATIENT = 'patient'
    DOCTOR = 'doctor'
    ADMIN = 'admin'

    USER_TYPES = (
        (PATIENT, 'Patient'),
        (DOCTOR, 'Doctor'),
        (ADMIN, 'Admin'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPES, default=PATIENT)
    email = models.EmailField(unique=True)

    def is_patient(self):
        """Checks if the user is a patient."""
        return self.user_type == self.PATIENT

    def is_doctor(self):
        """Checks if the user is a doctor."""
        return self.user_type == self.DOCTOR

    def is_admin(self):
        """Checks if the user is an admin."""
        return self.user_type == self.ADMIN

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically add users to appropriate groups
        upon creation.
        """
        created = self._state.adding  # Check if it's a new object
        super().save(*args, **kwargs) # call super save method first
        if created:
            if self.is_patient():
                group, created = Group.objects.get_or_create(name='Patients')
                self.groups.add(group)
            elif self.is_doctor():
                group, created = Group.objects.get_or_create(name='Doctors')
                self.groups.add(group)
            elif self.is_admin():
                group, created = Group.objects.get_or_create(name='Admins')
                self.groups.add(group)

    def __str__(self):
        return self.username



class Profile(models.Model):
    """
    Abstract base model for user profiles.
    """

    MALE = 'Male'
    FEMALE = 'Female'
    OTHER = 'Other' # Add other option

    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES, blank=True, null=True) # add blank and null
    phone_number = models.CharField(max_length=20, blank=True, null=True) # increased max length and add blank and null
    date_of_birth = models.DateField(blank=True, null=True) # add blank and null

    class Meta:
        abstract = True

class Patient(Profile,TimeStampedModel):
    """
    Represents a patient in the system. Extends the base Profile model
    and includes patient-specific information such as medical history,
    address, and medical conditions. Inherits timestamp fields for tracking
    creation and update times.
    """
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True)
    medical_history = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)


    def clean(self):
        if self.phone_number:
            try:
                parsed_number = phonenumbers.parse(self.phone_number)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValidationError({'phone_number': "Invalid phone number."})
                self.phone_number = phonenumberutil.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            except phonenumbers.phonenumberutil.NumberParseException:
                raise ValidationError({'phone_number': "Invalid phone number format."})
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Patients"

class Report(TimeStampedModel):
    """
    Represents a report uploaded by a patient, with metadata like the name and file.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="reports")
    name = models.CharField(max_length=100, verbose_name="Report Name")
    file = models.FileField(upload_to="patient_reports/", blank=True, null=True, verbose_name="Report File")

    class Meta:
        verbose_name = "Patient Report"
        verbose_name_plural = "Patient Reports"
        ordering = ["-created_at"]  # Latest reports first

    def __str__(self):
        return f"{self.name} ({self.patient.user.username})"

class Speciality(TimeStampedModel):
    """
    Represents a medical specialty (e.g., Cardiology, Pediatrics).
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Specialities" 



class Doctor(Profile,TimeStampedModel):
    """
    Represents a doctor in the system. Extends the Profile model and includes
    doctor-specific information.
    """
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True)
    # speciality = models.CharField(max_length=100, choices=SPECIALITIES, blank=True, null=True)
    speciality = models.ForeignKey(
        'Speciality',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors'
    )
    bio = models.TextField(max_length=800, blank=True, null=True)
    years_of_experience = models.IntegerField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to="doctor_images/", blank=True, null=True)
    certificate = models.FileField(upload_to="doctor_certificates/")
    is_verified = models.BooleanField(default=False) # Verification status
    class Meta:
        verbose_name_plural = "Doctors"
    def clean(self):
        super().clean()
        if self.gender not in [self.MALE, self.FEMALE]:
            raise ValidationError({'gender': "Doctors can only be Male or Female."})
        if self.phone_number:
            try:
                parsed_number = phonenumbers.parse(self.phone_number)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValidationError({'phone_number': "Invalid phone number."})
                self.phone_number = phonenumberutil.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            except phonenumbers.phonenumberutil.NumberParseException:
                raise ValidationError({'phone_number': "Invalid phone number format."})
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username



class DoctorAvailability(TimeStampedModel):
    """
    Represents a specific time slot when a doctor is available.
    """
    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE,
        related_name='availability'
    )
    day_of_week = models.IntegerField(
        choices=[
            (0, 'Sunday'),
            (1, 'Monday'),
            (2, 'Tuesday'),
            (3, 'Wednesday'),
            (4, 'Thursday'),
            (5, 'Friday'),
            (6, 'Saturday')
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'day_of_week', 'start_time', 'end_time'],
                name='unique_time_slot_per_doctor'
            )
        ]
        ordering = ['day_of_week', 'start_time']

    def clean(self):
        """
        Ensure there are no overlapping time slots for the same doctor and day.
        """
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be earlier than end time.")

        overlapping_slot = DoctorAvailability.objects.filter(
            doctor=self.doctor,
            day_of_week=self.day_of_week
        ).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if overlapping_slot.exists():
            raise ValidationError("This time slot overlaps with an existing availability.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    # """
    # Represents a specific time slot when a doctor is available.
    # """
    # doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='availability')
    # day_of_week = models.IntegerField(choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')])
    # start_time = models.TimeField()
    # end_time = models.TimeField()

    # class Meta:
    #     unique_together = ('doctor', 'day_of_week')
    #     ordering = ['day_of_week', 'start_time']  # Order availability by day and time

    def __str__(self):
        return f"{self.doctor.user.username} - {self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"



class PaymentMethod(TimeStampedModel):
    """
    Represents a payment method accepted by a doctor.
    """
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='payment_methods')
    PAYMENT_TYPES = (
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'EasyPaisa'),
        ('bank_account', 'Bank Account'),
        ('credit_card', 'Credit/Debit Card'),
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    iban = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True) # Store last 4 or token
    card_expiry = models.CharField(max_length=7, blank=True, null=True) # MM/YYYY
    card_holder_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.doctor.user.username} - {self.get_payment_type_display()}"

    class Meta:
        verbose_name_plural = "Payment Methods"



