from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='user')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name