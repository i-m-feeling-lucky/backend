from django.urls import path

from .views import user, interview

urlpatterns = [
    path('login', user.login),
    path('logout', user.logout),
    path('user', user.user),
    path('user/<int:id>', user.user_info),
    path('user/<int:id>/password', user.put_password),
    path('user/<int:id>/free_time', user.put_free_time),
    path('user/application_result', user.put_application_result),
    path('user/assign/interviewer', user.assign_interviewer),
    path('user/assign/interviewee', user.assign_interviewee),
    path('interview', interview.interview),
    path('interview/<int:id>', interview.interview_info),
    path('interview/<int:id>/verify', interview.interview_verify),
    path('interview/<int:id>/evaluation', interview.add_evaluation),
    path('interview/<int:id>/history/<ty>', interview.history),
]
