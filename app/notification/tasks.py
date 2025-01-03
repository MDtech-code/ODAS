from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(queue='email')
def send_welcome_email(email, username):
    """
    Task to send a welcome email to the patient.
    """
    try:
        subject = 'Welcome to Our Platform'
        message = f"Hello {username},\n\nThank you for registering as a patient on our platform!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        print(subject,message,from_email,recipient_list)
        send_mail(subject, message, from_email, recipient_list)
        
        logger.info(f"Welcome email successfully sent to {email}")
        return "Email sent successfully"
    except Exception as e:
        logger.error(f"Error sending welcome email to {email}: {str(e)}")
        raise e
