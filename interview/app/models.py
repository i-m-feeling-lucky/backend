from django.db import models
import uuid


class User(models.Model):
    class UserRole(models.IntegerChoices):
        Admin = 0
        HR = 1
        Interviewer = 2

    email = models.CharField(max_length=32, unique=True)
    pass_sha256 = models.CharField(max_length=64)  # INSECURE
    role = models.IntegerField(choices=UserRole.choices)

    def __str__(self):
        return f'User {self.id}'


class UserLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f'UserLogin {self.user}'
