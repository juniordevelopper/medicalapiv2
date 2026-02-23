from django.db import models
from accounts.models import CustomUser, Doctor, Reception

# ----------------------------
# Queue
# ----------------------------
class Queue(models.Model):
    STATUS_CHOICES = (
        (0, "waiting"),
        (1, "called"),
        (2, "done"),
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='queues'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='queues'
    )
    reception = models.ForeignKey(
        Reception,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_queues'
    )
    number = models.PositiveIntegerField()
    date = models.DateField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('doctor', 'date', 'number')

    def __str__(self):
        return self.doctor.user.username