from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    name = models.CharField(null=True, max_length=200)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default='avatar.svg')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return str(self.name)


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return str(self.body[0:49])
