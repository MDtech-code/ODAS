from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.account.models import User, Patient, Doctor, Speciality, DoctorAvailability, PaymentMethod,Report


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the User model.
    """
    model = User
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_staff', 'is_active')}
        ),
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """
    Admin interface for the Patient model.
    """
    list_display = ('user', 'gender', 'phone_number', 'date_of_birth', 'address')
    search_fields = ('user__username', 'phone_number', 'address')
    list_filter = ('gender',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """
    Admin interface for the Doctor model.
    """
    list_display = ('user', 'gender', 'phone_number', 'date_of_birth', 'speciality', 'years_of_experience', 'consultation_fee', 'is_verified')
    search_fields = ('user__username', 'speciality__name')
    list_filter = ('speciality', 'is_verified')
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Personal Info', {'fields': ('speciality', 'bio', 'years_of_experience', 'consultation_fee', 'image', 'certificate')}),
        ('Verification', {'fields': ('is_verified',)}),
    )



@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    """
    Admin interface for the Speciality model.
    """
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    """
    Admin interface for the DoctorAvailability model.
    """
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week',)
    search_fields = ('doctor__user__username',)
    ordering = ('day_of_week', 'start_time')


# @admin.register(PaymentMethod)
# class PaymentMethodAdmin(admin.ModelAdmin):
#     """
#     Admin interface for the PaymentMethod model.
#     """
#     list_display = ('doctor', 'payment_type', 'account_number', 'bank_name')
#     list_filter = ('payment_type',)
#     search_fields = ('doctor__user__username', 'account_number', 'bank_name')




class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'patient')
    search_fields = ('name', 'patient__user__username')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('patient__user')

    def patient(self, obj):
        return obj.patient.user.username

    patient.admin_order_field = 'patient__user__username'  # Allows column order sorting
    patient.short_description = 'Patient Username'  # Renames column head

admin.site.register(Report, ReportAdmin)
