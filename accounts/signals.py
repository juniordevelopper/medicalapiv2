from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomUser, Director, Doctor, Reception

@receiver(post_save, sender=CustomUser)
def manage_user_profile(sender, instance, created, **kwargs):
    if instance.status == 3:
        Director.objects.get_or_create(user=instance)
    elif instance.status == 2:
        Doctor.objects.get_or_create(user=instance)
    elif instance.status == 1:
        Reception.objects.get_or_create(user=instance)

@receiver(post_delete, sender=Director)
def reset_status_on_director_delete(sender, instance, **kwargs):
    user = instance.user
    if user.status == 3:
        user.status = 0
        user.save()

@receiver(post_delete, sender=Doctor)
def reset_status_on_doctor_delete(sender, instance, **kwargs):
    user = instance.user
    if user.status == 2:
        user.status = 0
        user.save()

@receiver(post_delete, sender=Reception)
def reset_status_on_reception_delete(sender, instance, **kwargs):
    user = instance.user
    if user.status == 1:
        user.status = 0
        user.save()

@receiver(post_save, sender=CustomUser)
def create_director_profile(sender, instance, created, **kwargs):
    if instance.status == 3:
        Director.objects.get_or_create(user=instance)

    elif instance.status != 3:
       Director.objects.filter(user=instance).delete()