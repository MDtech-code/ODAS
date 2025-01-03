from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from app.notification.tasks import send_welcome_email  # Celery task
from app.account.models import Patient
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(post_save, sender=Patient)
def send_welcome_email_signal(sender, instance, created, **kwargs):
    if created:  # Trigger only when a new Patient is created
        user = instance.user
        print(f"Signal triggered for user: {user.email}")
        logger.debug(f"Signal triggered for new patient: {user.email}")

        try:
            # Send email task to Celery
            send_welcome_email.delay(user.email, user.username)
            logger.debug(f"Welcome email task dispatched to Celery for {user.email}")
        except Exception as e:
            logger.error(f"Failed to dispatch Celery task for {user.email}: {str(e)}")
