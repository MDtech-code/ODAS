from django.urls import path
from . import views

urlpatterns = [
    path('',views.appointment_view,name='appointment'),
    path('<int:appointment_id>/prescription/', views.manage_prescription, name='manage_prescription'),
    path('api/check-availability/', views.check_availability, name='check_availability'),
    # Endpoint for initiating payment (sending request to JazzCash)
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),

    # Endpoint for handling the callback from JazzCash after the user completes the payment
    path('payment/callback/', views.payment_callback, name='payment_callback'),

    # Endpoint for handling asynchronous notifications from JazzCash
    path('payment/notify/', views.payment_notify, name='payment_notify'),
    
]
