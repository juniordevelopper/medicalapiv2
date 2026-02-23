from django.db import models
from accounts.models import CustomUser

# ----------------------------
# Application
# ----------------------------
class Application(models.Model):
    ACTIVE_CHOICES = (
        (0, "unseen"),
        (1, "in_progress"),
        (2, "approved"),
    )

    STATUS_CHOICES = (
        (0, "complaint"),
        (1, "reception"),
        (2, "doctor"),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    body = models.TextField()
    screenshot = models.ImageField(
        upload_to='applications/',
        null=True,
        blank=True
    )
    active = models.IntegerField(choices=ACTIVE_CHOICES, default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username