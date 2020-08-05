from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class UserPaymentCard(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    card_user_key = models.CharField(max_length=32, null=True)
    card_token = models.CharField(max_length=32)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "User Payment Card"
        verbose_name_plural = "User Payment Cards"
