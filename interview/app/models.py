from django.db import models


class User(models.Model):
    class UserRole(models.IntegerChoices):
        Admin = 0
        HR = 1
        Interviewer = 2
        Interviewee = 3

    email = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)
    pass_sha256 = models.CharField(max_length=64)
    role = models.IntegerField(choices=UserRole.choices)

    def __str__(self):
        return f'User {self.name}'


class UserLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=36)

    def __str__(self):
        return f'UserLogin {self.user}'
