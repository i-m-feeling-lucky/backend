from django.views.decorators.http import require_GET, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import F
from app.models import *
from app.utils import send_email
from hashlib import sha256
from http import HTTPStatus
import json
import uuid
import random
import string
import datetime
from datetime import timezone, timedelta


@require_http_methods(['GET', 'POST'])
def interview(req):
    if req.method == 'GET':
        return interview_infos(req)
    elif req.method == 'POST':
        return add_interview(req)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def interview_infos(req):
    # GET /interview
    try:
        token = req.META.get("HTTP_X_TOKEN")

        if UserLogin.objects.filter(token=token).exists():
            role = UserLogin.objects.get(token=token).user.role
            data = Interview.objects.values("id", "hr", "interviewer", "interviewee",
                                            "interviewer_token", "start_time", "length", "actual_length", "status")

            for item in data:
                interview = Interview.objects.get(id=item["id"])

                item["start_time"] = int(item["start_time"].replace(tzinfo=timezone.utc).timestamp())
                if role != 2:
                    item["interviewer_token"] = ""

                try:
                    comment = InterviewComment.objects.get(interview=interview)
                    item['rate'] = comment.rate
                    item["comment"] = comment.comment
                except:
                    item['rate'] = -1
                    item["comment"] = ""
            return JsonResponse(list(data), safe=False)

        else:
            res = {"message": "token 信息无效"}
            return JsonResponse(res, status=HTTPStatus.UNAUTHORIZED)

    except Exception as e:
        res = {"message": str(e)}
        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)


def add_interview(req):
    # POST /interview
    try:
        token = req.META.get("HTTP_X_TOKEN")

        if UserLogin.objects.filter(token=token).exists():

            data = json.loads(req.body.decode())
            hr = data['hr']
            interviewer = data['interviewer']
            interviewee = data['interviewee']
            start_time = datetime.datetime.utcfromtimestamp(data['start_time'])
            length = data['length']
            interviewer_token = str(uuid.uuid4()).replace('-', '')
            interviewee_token = str(uuid.uuid4()).replace('-', '')
            password = ''.join(random.sample(string.ascii_letters+string.digits, 8))

            # current_user.id == hr
            current_user = UserLogin.objects.filter(token=token).first().user
            if current_user.id != hr:
                res = {"message": "Current user is not the HR"}
                return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)

            # (current_user, interviewer) in HRAssignInterviewer
            if not HRAssignInterviewer.objects.filter(hr=hr, interviewer=interviewer).exists():
                res = {"message": "Current HR does not assign the interviewer"}
                return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)
            else:
                obj_interviewer = HRAssignInterviewer.objects.filter(hr=hr, interviewer=interviewer).first().interviewer

            # (current_user, interviewee) in HRAssignInterviewee
            if not HRAssignInterviewee.objects.filter(hr=hr, interviewee=interviewee).exists():
                res = {"message": "Current HR does not assign the interviewee"}
                return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)
            else:
                obj_interviewee = HRAssignInterviewee.objects.filter(hr=hr, interviewee=interviewee).first().interviewee

            # interviewer time zone available availability check
            new_start_time = data['start_time'] # int type
            new_end_time = data['start_time'] + data['length'] * 60 # int type
            free_times = json.loads(obj_interviewer.free_time)
            for free_time in free_times:
                dt = datetime.datetime(int(free_time[0][0:4]), int(free_time[0][5:7]), int(free_time[0][8:10]), 
                    int(free_time[0][11:13]), int(free_time[0][14:16]))
                free_start_time = int(dt.replace(tzinfo=timezone.utc).timestamp())
                dt = datetime.datetime(int(free_time[1][0:4]), int(free_time[1][5:7]), int(free_time[1][8:10]), 
                    int(free_time[1][11:13]), int(free_time[1][14:16]))
                free_end_time = int(dt.replace(tzinfo=timezone.utc).timestamp())
                if not (new_start_time >= free_start_time and new_end_time <= free_end_time):
                    res = {"message": "面试时间未完全包含在面试官空闲时间内"}
                    return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)
                existed_interviews = Interview.objects.filter(interviewer=obj_interviewer).values("start_time", "length", "status", "actual_length")
                for existed_interview in existed_interviews:
                    existed_start_time = int(existed_interview["start_time"].replace(tzinfo=timezone.utc).timestamp())
                    if existed_interview["status"] == "ended":
                        existed_end_time = existed_start_time + existed_interview["actual_length"] * 60    
                    else:
                        existed_end_time = existed_start_time + existed_interview["length"] * 60
                    if not (new_end_time <= existed_start_time or new_start_time >= existed_end_time):
                        res = {"message": "面试时间与已有面试重叠"}
                        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)
                    elif not (new_end_time <= existed_start_time - 600 or new_start_time >= existed_end_time + 600):
                        res = {"message": "面试时间间隔少于10分钟"}
                        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)

            interview = Interview(hr=current_user, interviewer=obj_interviewer, interviewee=obj_interviewee,
                                  interviewer_token=interviewer_token, interviewee_token=interviewee_token,
                                  password=password, start_time=start_time, length=length)
            interview.save()

            start = start_time.replace(tzinfo=timezone.utc) \
                .astimezone(timezone(timedelta(hours=8)))   \
                .replace(tzinfo=None)
            link = f'{settings.WEB_ROOT}/interview/{interview.id}?token={interviewee_token}'
            send_email(obj_interviewee.email, '面试时间通知',
                       f'''面试者 {obj_interviewee.name} 你好，你的面试将于北京时间 {start} 开始，\
持续时间 {length} 分钟，面试链接为 {link}''')

            return HttpResponse(status=HTTPStatus.OK)

        else:
            res = {"message": "token 信息无效"}
            return JsonResponse(res, status=HTTPStatus.UNAUTHORIZED)

    except Exception as e:
        res = {"message": str(e)}
        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)


@require_GET
def interview_info(req, id):
    # GET /interview/{id}
    try:
        token = req.META.get("HTTP_X_TOKEN")
        hr = Interview.objects.get(id=id).hr

        if ((UserLogin.objects.filter(token=token).exists() and
                UserLogin.objects.get(token=token).user.role == 0) or
                UserLogin.objects.filter(user=hr, token=token).exists() or
                Interview.objects.filter(id=id, interviewer_token=token).exists() or
                Interview.objects.filter(id=id, interviewee_token=token).exists()):
            data = Interview.objects.filter(id=id).values("id", "hr", "interviewer",
                                                          "interviewee", "start_time", "length",
                                                          "actual_length", "status").first()
            data['start_time'] = int(data['start_time'].replace(tzinfo=timezone.utc).timestamp())
            return JsonResponse(data)
        else:
            res = {"message": "token 信息无效"}
            return JsonResponse(res, status=HTTPStatus.UNAUTHORIZED)

    except Exception as e:
        res = {"message": str(e)}
        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)


@require_GET
def interview_verify(req, id):
    # GET /interview/{id}/verify
    try:
        token = req.META.get("HTTP_X_TOKEN")
        hr = Interview.objects.get(id=id).hr

        if (UserLogin.objects.filter(token=token).exists() and
                UserLogin.objects.get(token=token).user.role == 0):
            data = Interview.objects.filter(id=id).values('password').first()
            data['role'] = 0
            return JsonResponse(data)

        elif UserLogin.objects.filter(user=hr, token=token).exists():
            data = Interview.objects.filter(id=id).values('password').first()
            data['role'] = 1
            return JsonResponse(data)

        elif Interview.objects.filter(interviewer_token=token, id=id).exists():
            data = Interview.objects.filter(id=id).values('password').first()
            data['role'] = 2
            return JsonResponse(data)

        elif Interview.objects.filter(interviewee_token=token, id=id).exists():
            data = Interview.objects.filter(id=id).values('password').first()
            data['role'] = 3
            return JsonResponse(data)

        else:
            res = {"message": "token 信息无效"}
            return JsonResponse(res, status=HTTPStatus.UNAUTHORIZED)

    except Exception as e:
        res = {"message": str(e)}
        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)


@require_http_methods(['PUT'])
def add_evaluation(req, id):
    # PUT /interview/{id}/evaluation
    try:
        token = req.META.get("HTTP_X_TOKEN")

        if Interview.objects.filter(interviewer_token=token, id=id).exists():
            interview = Interview.objects.get(id=id)
            data = json.loads(req.body.decode())
            if InterviewComment.objects.filter(interview=interview).exists():
                interviewer_comment = InterviewComment.objects.get(interview=interview)
                interviewer_comment.rate = data['rate']
                interviewer_comment.comment = data['comment']
            else:
                interviewer_comment = InterviewComment(interview=interview, rate=data['rate'], comment=data['comment'])
            interviewer_comment.save()
            return HttpResponse(status=HTTPStatus.OK)
        else:
            res = {"message": "token 信息无效"}
            return JsonResponse(res, status=HTTPStatus.UNAUTHORIZED)

    except Exception as e:
        res = {"message": str(e)}
        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)


def set_status(req, id):
    # PUT /interview/{id}/status
    try:
        token = req.META.get("HTTP_X_TOKEN")

        if Interview.objects.filter(interviewer_token=token, id=id).exists():
            data = json.loads(req.body.decode())
            interview = Interview.objects.get(id=id)
            interview.status = data['status']
            if data['status'] == 'ended':
                interview.actual_length = int(
                    datetime.datetime.utcnow().timestamp()) - int(
                        interview.start_time.timestamp())
            interview.save()
            return HttpResponse(status=HTTPStatus.OK)
        else:
            res = {"message": "token 信息无效"}
            return JsonResponse(res, status=HTTPStatus.UNAUTHORIZED)

    except Exception as e:
        res = {"message": str(e)}
        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)


@require_http_methods(['GET', 'POST'])
def history(req, id, ty):
    if req.method == 'GET':
        return get_history(req, id, ty)
    elif req.method == 'POST':
        return add_history(req, id, ty)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def get_history(req, id, ty):
    # GET /interview/{id}/history/{ty}
    try:
        token = req.META.get("HTTP_X_TOKEN")
        hr = Interview.objects.get(id=id).hr

        if (UserLogin.objects.filter(user=hr, token=token).exists() or
                Interview.objects.filter(id=id, interviewer_token=token).exists() or
                Interview.objects.filter(id=id, interviewee_token=token).exists()):
            scope = req.GET.get('scope')
            if not History.objects.filter(type=ty, interview__id=id).exists():
                data = []
                return JsonResponse(data, safe=False)
            elif scope == "all":
                data = History.objects.filter(type=ty, interview__id=id).values('time', 'data')
                for item in data:
                    item['time'] = int(item['time'].replace(tzinfo=timezone.utc).timestamp() * 1000)
                    item['data'] = json.loads(item['data'])
                return JsonResponse(list(data), safe=False)
            elif scope == "latest":
                data = History.objects.filter(type=ty, interview__id=id).order_by(
                    '-time').first()
                res = {}
                res['time'] = int(data.time.replace(tzinfo=timezone.utc).timestamp() * 1000)
                res['data'] = json.loads(data.data)
                return JsonResponse([res], safe=False)
            else:
                data = []
                return JsonResponse(data, safe=False)

            return JsonResponse(data)

        else:
            res = {"message": "token 信息无效"}
            return JsonResponse(res, status=HTTPStatus.UNAUTHORIZED)

    except Exception as e:
        res = {"message": str(e)}
        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)


def add_history(req, id, ty):
    # POST /interview/{id}/history/{ty}
    try:
        token = req.META.get("HTTP_X_TOKEN")

        if (Interview.objects.filter(id=id, interviewer_token=token).exists() or
                Interview.objects.filter(id=id, interviewee_token=token).exists()):
            interview = Interview.objects.filter(id=id).first()
            history = History(interview=interview, type=ty, time=str(
                datetime.datetime.utcnow()), data=req.body.decode())
            history.save()
            return HttpResponse(status=HTTPStatus.OK)

        else:
            res = {"message": "token 信息无效"}
            return JsonResponse(res, status=HTTPStatus.UNAUTHORIZED)

    except Exception as e:
        res = {"message": str(e)}
        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)
