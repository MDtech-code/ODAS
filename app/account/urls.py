from django.urls import path
from django.contrib.auth.views import  PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from app.account.views import PatientRegistrationView, PatientEditProfileView,PatientProfileView, CustomLoginView, PasswordResetView,custom_logout,DoctorRegisterView,ReportView,DoctorProfileView,DoctorEditProfileView,doctor_availability_api,payment_methods_api
urlpatterns = [
    path('register/patient/', PatientRegistrationView.as_view(), name='register_patient'),
    path('doctor/register/', DoctorRegisterView.as_view(), name='register_doctor'),
    path('logout/', custom_logout, name='logout'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),

    path('patient/edit_profile/', PatientEditProfileView.as_view(), name='edit_patient_profile'),
    path('patient/profile/', PatientProfileView.as_view(), name='patient_profile'),
    path('upload_report/', ReportView.as_view(), name='upload_report'),
    path('update_report/<int:report_id>/', ReportView.as_view(), name='update_report'),
    path('delete_report/<int:report_id>/', ReportView.as_view(), name='delete_report'),
    #path('upload_report/', UploadReportView.as_view(), name='upload_report'),
    #path('upload_report/<int:report_id>/', UploadReportView.as_view(), name='update_report'),
    path('doctor/profile/', DoctorProfileView.as_view(), name='doctor-profile'),
    path('doctor/edit_profile/', DoctorEditProfileView.as_view(), name='edit_doctor_profile'),
    path("api/doctor/availability/", doctor_availability_api, name="doctor_availability_api"),
    path("api/doctor/payment-methods/", payment_methods_api, name="payment_methods_api"),
    #path('doctor/availability/delete/<int:pk>/', doctor_availability_api, name='delete_availability'),
    # path('doctor/payment-method/delete/<int:pk>/', delete_payment_method, name='delete_payment_method'),
    
    

]
