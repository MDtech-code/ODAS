from django.contrib import admin
from .models import Appointment, Payment, Prescription


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_start_datetime', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'appointment_start_datetime', 'created_at', 'updated_at')
    search_fields = ('patient', 'doctor')  # Simplified for the example
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Payment model.
    """
    list_display = ('appointment', 'amount', 'is_paid', 'created_at', 'updated_at')
    list_filter = ('is_paid', 'created_at', 'updated_at')
    search_fields = ('appointment__patient__user__username',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Prescription model.
    """
    list_display = ('appointment', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('appointment__patient__user__username', 'appointment__doctor__user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')