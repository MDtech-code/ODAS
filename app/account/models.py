
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Define roles
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.username



class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    contact = models.CharField(max_length=12)
    dob = models.DateField()

    def __str__(self):
        return f"Patient: {self.user.username}"


class Doctor(models.Model):
    SPECIALITIES = [
        ('Podiatrist', 'Podiatrist'),
        ('General', 'General'),
        ('Pediatrician', 'Pediatrician'),
        ('Endocrinologist', 'Endocrinologist'),
        ('Neurologist', 'Neurologist'),
        ('Rheumatologist', 'Rheumatologist'),
        ('Allergist', 'Allergist'),
        ('Psychiatrist', 'Psychiatrist'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    contact = models.CharField(max_length=12)
    dob = models.DateField()
    speciality = models.CharField(choices=SPECIALITIES, max_length=30)
    bio = models.TextField(max_length=800, blank=True)
    yoe = models.IntegerField()
    charge = models.DecimalField(decimal_places=2, max_digits=7)
    availability = models.JSONField(default=dict)  # Flexible availability schedule

    def __str__(self):
        return f"Doctor: {self.user.username}"
