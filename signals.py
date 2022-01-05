from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


from .models import *
from .services import sign_up_done, updated_profile


@receiver(profile_created)
def create_profile(instance: CustomUser, created: bool, **kwargs):
     if created:
         print('profile created!')
         Profile.objects.create(owner=instance)
         Subscriber.objects.create(user=instance)

         return None

def is_expired(notification) -> bool:
    expired_time = datetime.datetime.now().day - datetime.timedelta(days=3).days
    notification_time = notification.notific_time.date()
    if notification_time is None:
        return True

    if abs(notification_time.day) > expired_time:
        return False
    else:
        return True

@receiver(sign_up_done)
def sign_up_notify(instance: CustomUser, created: bool, **kwargs) -> None:
    if created:
        notification = Notification.objects.create()
        message = f'User {instance.username} was signed up at {notification.notific_time.strftime("%H:%M")}'

        notification.message = message
        notification.save()

        if is_expired(notification=notification):
            print('Notification deleted cuz expired')
            notification.delete()

@receiver(updated_profile)
def updated_profile_notify(request, instance, updated: bool, **kwargs) -> None:
    if updated:
        notification = Notification.objects.create()

        message = f'User {instance.username} has changed profile at {notification.notific_time.strftime("%H:%M")}'

        notification.message = message
        notification.save()

        if is_expired(notification=notification):
            print('Update Notification expired')
            notification.delete()