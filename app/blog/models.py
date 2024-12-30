from django.db import models
from app.common.models import TimeStampedModel

# Create your models here.
class Article(TimeStampedModel):
    """
    Represents a blog article written by a doctor.
    """
    doctor = models.ForeignKey('account.Doctor', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to="article_images/", blank=True, null=True)

    def __str__(self):
        return self.title

class Comment(TimeStampedModel):
    """
    Represents a comment left by a patient on an article.
    """
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')
    patient = models.ForeignKey('account.Patient', on_delete=models.CASCADE)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.patient.user.username} on {self.article.title}"
