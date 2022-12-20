from django.db import models
from datetime import datetime

# Create your models here.

class SendMailCategory(models.Model):
    user_name = models.CharField(max_length=255),
    #date = models.DateField(default=datetime.now())

