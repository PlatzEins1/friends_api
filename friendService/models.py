from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=255)

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    discarded = models.BooleanField(default=False)
