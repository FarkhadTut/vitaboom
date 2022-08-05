from django.db import models
from datetime import datetime





class Authentication(models.Model):
    USER_TYPES = (
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    )
    password = models.CharField(max_length=512, null=True, blank=True) 
    user_type = models.CharField(max_length=512, choices=USER_TYPES, null=True, blank=True)

    def __str__(self) -> str:
        return self.user_type



class User(models.Model):
    telegram_id = models.IntegerField(null=False, blank=False)
    telegram_num = models.IntegerField(null=False, blank=False)
    name = models.CharField(max_length=512, null=False, blank=False)
    surname = models.CharField(max_length=512, null=False, blank=False)
    password = models.ForeignKey(to=Authentication, on_delete=models.PROTECT)
    confirmed = models.BooleanField(blank=False, null=False)
    date_submitted = models.DateTimeField(default=datetime.now(),blank=False, null=False)
    date_confirmed = models.DateTimeField(default=datetime.now(), blank=True, null=True)    
    image = models.CharField(max_length=512, null=False, blank=False)
    user_type = models.CharField(max_length=512, null=False, blank=False)