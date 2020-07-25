from django.db import models
from datetime import datetime
import uuid


class User(models.Model):
    class UserRole(models.IntegerChoices):
        Admin = 0
        HR = 1
        Interviewer = 2

    email = models.EmailField(unique=True)
    pass_sha256 = models.CharField(max_length=64)  # INSECURE
    role = models.IntegerField(choices=UserRole.choices)

    def __str__(self):
        return f'User {self.id}'


class UserLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f'UserLogin {self.user.id}'


class Interviewer(models.Model):
    id = models.OneToOneField(User, models.CASCADE, primary_key=True)
    free_time = models.TextField()

    def __str__(self):
        return f'Interviewer {self.user.id}'


class Interviewee(models.Model):
    RESULTS = [
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    ]

    email = models.EmailField(primary_key=True)
    name = models.CharField(max_length=64)
    application_result = models.IntegerField(choices=RESULTS, default=0)

    def __str__(self):
        return f'Interviewee {self.name}'


class HRAssignInterviewer(models.Model):
    hr = models.ForeignKey(User, models.PROTECT)
    interviewer = models.ForeignKey(Interviewer, models.PROTECT)

    def __str__(self):
        return f'HR {self.hr.id} ↔ Interviewer {self.interviewer.id}'


class HRAssignInterviewee(models.Model):
    hr = models.ForeignKey(User, models.PROTECT)
    interviewee = models.ForeignKey(Interviewee, models.PROTECT)

    def __str__(self):
        return f'HR {self.hr.id} ↔ Interviewee {self.interviewee.id}'


class Interview(models.Model):
    STATUSES = [
        ('upcoming', 'upcoming'),
        ('active', 'active'),
        ('ended', 'ended'),
    ]

    hr = models.ForeignKey(User, models.PROTECT)
    interviewer = models.ForeignKey(Interviewer, models.PROTECT)
    interviewee = models.ForeignKey(Interviewee, models.PROTECT)
    interviewer_token = models.UUIDField(default=uuid.uuid4, editable=False)
    interviewee_token = models.UUIDField(default=uuid.uuid4, editable=False)
    password = models.CharField(max_length=32)
    start_time = models.DateTimeField()
    length = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=10, choices=STATUSES, default='upcoming')

    def __str__(self):
        return f'Interview: interviewer {self.interviewer.id}, interviewee {self.interviewee.id}'


class InterviewComment(models.Model):
    RATES = [
        (0, 'S'),
        (1, 'A'),
        (2, 'B'),
        (3, 'C'),
        (4, 'D'),
    ]

    interview = models.OneToOneField(Interview, models.CASCADE, related_name='comment')
    rate = models.IntegerField(choices=RATES)
    comment = models.TextField()


class History(models.Model):
    TYPES = [
        ('chat', 'chat'),
        ('whiteboard', 'whiteboard'),
        ('code', 'code'),
    ]

    interview = models.ForeignKey(Interview, models.PROTECT)
    type = models.CharField(max_length=12, choices=TYPES)
    time = models.DateTimeField(default=datetime.utcnow)
    data = models.TextField()

    def __str__(self):
        return f'History: {self.interview}'
