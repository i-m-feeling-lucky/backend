from django.views.decorators.http import require_GET, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.db.models import F
from app.models import *
from hashlib import sha256
from http import HTTPStatus
import json
import uuid
import random
import string
import datetime


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
            data = Interview.objects.values("id", "hr", "interviewer", "interviewee", "start_time", "length")
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
            start_time = data['start_time']
            length = data['length']
            interviewer_token = str(uuid.uuid4()).replace('-','')
            interviewee_token = str(uuid.uuid4()).replace('-','')
            password = ''.join(random.sample(string.ascii_letters+string.digits,8))
            
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

            interview = Interview(hr=current_user, interviewer=obj_interviewer, interviewee=obj_interviewee, interviewer_token=interviewer_token, interviewee_token=interviewee_token, password=password, start_time=start_time, length=length)
            interview.save()

            # TODO: Send emails
            
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
        
        if UserLogin.objects.filter(token=token).exists():
            data = Interview.objects.filter(id=id).values("id", "hr", "interviewer", "interviewee", "start_time", "length").first()
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
        
        if Interview.objects.filter(interviewer_token=token, id=id).exists():
            data = Interview.objects.filter(interviewer_token=token, id=id).values('password').first()
            data['role'] = 2
            return JsonResponse(data)
        
        elif Interview.objects.filter(interviewee_token=token, id=id).exists():
            data = Interview.objects.filter(interviewee_token=token, id=id).values('password').first()
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
        
        if UserLogin.objects.filter(token=token).exists():
            current_user = UserLogin.objects.filter(token=token).first().user
            interviewer = Interview.objects.filter(id=id).first().interviewer.id
            interview = Interview.objects.filter(id=id).first()
            
            if interviewer.id != current_user.id:
                res = {"message": "unauthorized user"}
                return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)
            else:
                data = json.loads(req.body.decode())
                interviewer_comment = InterviewComment(interview=interview, rate=data['rate'], comment=data['comment'])
                interviewer_comment.save()
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
        
        if UserLogin.objects.filter(token=token).exists():
            scope = req.GET.get('scope')
            
            if scope == "all":
                data = History.objects.filter(type=ty, interview__id=id).values('time', 'data')
                return JsonResponse(list(data), safe=False)
            elif scope == "latest":
                data = History.objects.filter(type=ty, interview__id=id).order_by('-time').first().values('time', 'data')
                return JsonResponse(list(data), safe=False)
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
        
        if UserLogin.objects.filter(token=token).exists():
            interview = Interview.objects.filter(id=id).first()
            history = History(interview=interview, type=ty, time=str(datetime.datetime.utcnow()), data=json.dumps(req.body.decode()))
            history.save()
            return HttpResponse(status=HTTPStatus.OK)
        
        else:
            res = {"message": "token 信息无效"}
            return JsonResponse(res, status=HTTPStatus.UNAUTHORIZED)
   
    except Exception as e:
        res = {"message": str(e)}
        return JsonResponse(res, status=HTTPStatus.UNPROCESSABLE_ENTITY)
