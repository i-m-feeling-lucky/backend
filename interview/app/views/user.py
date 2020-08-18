from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from app.models import *

from hashlib import sha256
from http import HTTPStatus
import json
import re


@require_POST
def login(req):
    try:
        data = json.loads(req.body.decode())
        email = data['email']
        passw = data['password']
    except (json.JSONDecodeError, KeyError):
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    passw = sha256(passw.encode()).hexdigest()
    try:
        user = User.objects.get(email=email, pass_sha256=passw)
    except ObjectDoesNotExist:
        return JsonResponse({"message": "账号或密码错误"}, status=HTTPStatus.UNAUTHORIZED)
    user_login = UserLogin(user=user)
    user_login.save()
    res = {
        'id': user.id,
        'role': user.role,
        'token': str(user_login.token),
    }
    return JsonResponse(res, status=HTTPStatus.OK)


@require_POST
def logout(req):
    try:
        token = req.META.get("HTTP_X_TOKEN")
        UserLogin.objects.filter(token=token).delete()
        return HttpResponse('logout success', status=HTTPStatus.OK)
    except Exception:
        pass
    return HttpResponse('', status=HTTPStatus.GATEWAY_TIMEOUT)


@require_http_methods(['GET', 'POST'])
def user(req):
    if req.method == 'GET':
        return user_infos(req)
    elif req.method == 'POST':
        return add_user(req)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)

@require_GET
def user_infos(req):   
    try:
        #data = json.loads(req.body.decode())
        #token = data['token']
        #user = UserLogin.objects.get(token = token)#token失效问题
        res = []
        ids = list(Interviewer.objects.all().values_list('id'))
        for i in ids:
            single_info = User.objects.get(id=i[0])
            res.append({"id":i[0],"email":single_info.__dict__["email"],"role":single_info.__dict__["role"]})
        return HttpResponse(res, status=HTTPStatus.OK)
    except:
        return JsonResponse({"message":'failed in getting infos'},status=HTTPStatus.EXPECTATION_FAILED)


def add_user(req):
    try:
        data = json.loads(req.body.decode())
        email = data['email']
        passw = data['password']
        role = data['role']
        if len(passw) > 64:
            raise
        if role not in [0,1,2,3]:
            raise
        if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',email):
            raise

        passw = sha256(passw.encode()).hexdigest()
        User.objects.create(email=email, pass_sha256=passw, role=role)
        if role == 2:
            user = User.objects.get(email=email)
            Interviewer.objects.create(id=user, free_time='')
            viewer = Interviewer.objects.get(id=user)
        elif role == 3:
            name = data['name']
            if not name or len(name) > 64:
                raise
            Interviewee.objects.create(email=email,name=name)
        return HttpResponse('create user success',status=HTTPStatus.OK)
    except:
        return HttpResponse('add user failed', status=HTTPStatus.METHOD_NOT_ALLOWED)


@require_GET
def user_info(req, id):
    try:
        data = json.loads(req.body.decode())
        email = data['email']
        user = User.objects.get(email=email)
        if user.role == 3: 
            useree = Interviewee.objects.get(email=email)
            #当角色是interviewee时,返回useree信息:账号,名字,录取状态
            res = {'email': useree.email, 'name':useree.name, 'application_result': useree.application_result}
        elif user.role == 2:
            userer = Interviewer.objects.get(user=user)
            #当角色是interviewer时,返回userer信息:id,空闲时间
            res = {'email': userer.id, 'role': userer.free_time}
        else:
            res = {'email':email, 'role':user.role}
        return JsonResponse(res, status=HTTPStatus.OK)
    except ObjectDoesNotExist:
        return JsonResponse("user does not exist", status=HTTPStatus.NOT_FOUND)


@require_http_methods(['PUT'])
def put_password(req, id): #修改密码
    # PUT /user/{id}/pasword
    data = json.loads(req.body.decode())
    oldpassword = data['old_password']
    newpassword = data['new_password'] 
    user = User.objects.get(id=id)
    oldpassword = sha256(oldpassword.encode()).hexdigest()
    if user.pass_sha256 != oldpassword:
        return JsonResponse({'message':'wrong password'},status=HTTPStatus.METHOD_NOT_ALLOWED)
    user.pass_sha256 = sha256(newpassword.encode()).hexdigest()
    user.save()
    return HttpResponse({'message':'password has been changed'}, status=HTTPStatus.OK)

@require_http_methods(['PUT'])
def put_free_time(req, id):
    # PUT /user/{id}/free_time
    data = json.loads(req.body.decode())
    token = req.META.get("HTTP_X_TOKEN")
    free_time = data['free_time']
    userlogin = UserLogin.objects.get(token = token)
    if userlogin.user.role != 2:
        return HttpResponse({'message':'wrong method'},status=HTTPStatus.METHOD_NOT_ALLOWED)

    user = User.objects.get(id=id)
    ids = list(Interviewer.objects.all().values_list('id'))
    user.interviewer.free_time = free_time
    user.interviewer.save()
    return HttpResponse('succeeded in changing time',status=HTTPStatus.OK)

@require_http_methods(['PUT'])
def put_application_result(req):
    # PUT /user/application_result
    data = json.loads(req.body.decode())
    token = req.META.get("HTTP_X_TOKEN")
    userlogin = UserLogin.objects.get(token = token)
    if userlogin.user.role != 1:
        return HttpResponse({'message':'wrong requirement'}, status=HTTPStatus.METHOD_NOT_ALLOWED)#确认HR身份
    email = data['interviewee']
    result = data['application_result']
    itee = Interviewee.objects.get(email=email)
    try:
        HRAssignInterviewee.objects.get(hr=userlogin.user,interviewee=itee)
        itee.application_result = result
        itee.save()
        return HttpResponse({'message':'result set'},status=HTTPStatus.OK)
    except:
        return HttpResponse({'message':'fail operations'},status=HTTPStatus.OK)


@require_POST
def assign_interviewer(req):
    # POST /user/assign/interviewer
    data = json.loads(req.body.decode())
    token = req.META.get("HTTP_X_TOKEN")
    userlogin = UserLogin.objects.get(token = token)
    if(userlogin.user.role != 0):
        return HttpResponse({'message':'wrong requirement'}, status=HTTPStatus.METHOD_NOT_ALLOWED)#admin身份
    hrid = data['hr']
    interviewerid = data['interviewer']
    try:
        hr = User.objects.get(id= hrid)
        intervieweru = User.objects.get(id= interviewerid)
        interviewer = interviewer.objects.get(id= intervieweru)
        HRAssignInterviewer.create(hr=hr, interviewer=interviewer)
        return HttpResponse(status=HTTPStatus.OK)
    except:
        return HttpResponse({'message':'wrong operations'},status=HTTPStatus.OK)

@require_POST
def assign_interviewee(req):
    # POST /user/assign/interviewer
    data = json.loads(req.body.decode())
    token = req.META.get("HTTP_X_TOKEN")
    userlogin = UserLogin.objects.get(token = token)
    if(userlogin.user.role != 0):
        return HttpResponse('wrong requirement', status=HTTPStatus.METHOD_NOT_ALLOWED)#admin身份
    hrid = data['hr']
    intervieweemail = data['interviewee']
    try:
        hr = User.objects.get(id= hrid)
        interviewee = Interviewee.objects.get(email= intervieweemail)
        HRAssignInterviewee.create(hr=hr, interviewer=interviewee)
        return HttpResponse(status=HTTPStatus.OK)
    except:
        return HttpResponse({'message':'wrong operations'},status=HTTPStatus.OK)
