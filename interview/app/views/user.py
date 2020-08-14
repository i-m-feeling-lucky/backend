from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
#import sys
#sys.path.append("..")
from app.models import *

from hashlib import sha256
from http import HTTPStatus
import json


@require_POST
def login(req):
    try:
        data = json.loads(req.body.decode())
        email = data['email']
        passw = data['password']
    except (json.JSONDecodeError, KeyError):
        # return HttpResponse('status=HTTPStatus.BAD_REQUEST')
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    passw = sha256(passw.encode()).hexdigest()
    try:
        # return HttpResponse(str(passw))
        user = User.objects.get(email=email, pass_sha256=passw)
    except ObjectDoesNotExist:
    # except:
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
        data = json.loads(req.body.decode())
        token = data['token']
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
        print(ids)
        for i in ids:
            single_info = User.objects.get(id=i[0])
            res.append({"id":i[0],"email":single_info.__dict__["email"],"role":single_info.__dict__["role"]})
            print(res)
        return HttpResponse(res, status=HTTPStatus.OK)
    except:
        return JsonResponse({"message":'failed in getting infos'},status=HTTPStatus.EXPECTATION_FAILED)


def add_user(req):
    try:
        data = json.loads(req.body.decode())
        email = data['email']
        passw = data['password']
        role = data['role']
        print('check data')
        """
        print("before if1")
        if len(passw) > 64:
            print("length err\n")
            raise
        print("before if2")
        if role not in [0,1,2,3]:
            print("role err\n")
            raise
        print("before if3")
        if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',email):
            print("check reg\n")
            raise
        """
        print("before passw")
        passw = sha256(passw.encode()).hexdigest()
        print("create before")
        User.objects.create(email=email, pass_sha256=passw, role=role)
        print("create after")
        print(role)
        if(role == 2):
            user = User.objects.get(email=email)
            print(user)
            Interviewer.objects.create(id=user, free_time='')
            viewer = Interviewer.objects.get(id=user)
            print('check interviewer create')
            print(viewer.id)
        elif(role == 3):
            print('role3')
            name = data['name']
            if(not name or len(name) > 64):
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
    # TODO: PUT /user/{id}/pasword
    if req.method != 'PUT':
        return JsonResponse({'message':'wrong method'},status=HTTPStatus.METHOD_NOT_ALLOWED)
    
    data = json.loads(req.body.decode())
    oldpassword = data['old_password']
    newpassword = data['new_password'] 
    print(oldpassword, newpassword)
    print('id', id)
    user = User.objects.get(id=id)
    print('check id')
    print(user.email, user.pass_sha256, user.role, user.id)
    oldpassword = sha256(oldpassword.encode()).hexdigest()
    #print(sha256(oldpassword.encode()).hexdigest())
    if(user.pass_sha256 != oldpassword):
        return JsonResponse({'message':'wrong password'},status=HTTPStatus.METHOD_NOT_ALLOWED)
    print('check passw')
    user.pass_sha256 = sha256(newpassword.encode()).hexdigest()
    user.save()
    print('check save')
    return HttpResponse({'message':'password has been changed'}, status=HTTPStatus.OK)
'''
@require_http_methods(['PUT'])
def put_free_time(req, id):
    # TODO: PUT /user/{id}/free_time
    if req.method != 'PUT':
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)
    email = req.PUT.get('id')
    free_time = request.PUT.get('free_time')
    user = User.objects.get(email=email)
    if user.role != 2: 
        return HttpResponse('requirement not from 面试官', status=HTTPStatus.METHOD_NOT_ALLOWED)
    viewer = Interviewer.objects.get(user=user)
    viewer.free_time += ',' + free_time  #设计 空闲时间格式 "14:00-16:00,19:00-21:00" 或者 "1-2,3-4"
    viewer.save()
    return HttpResponse(status=HTTPStatus.OK)
'''

@require_http_methods(['PUT'])
def put_free_time(req, id):
    # TODO: PUT /user/{id}/free_time
    if req.method != 'PUT':
        return HttpResponse({'message':'wrong method'},status=HTTPStatus.METHOD_NOT_ALLOWED)
    print('check free_time')
    data = json.loads(req.body.decode())
    token = data['HTTP_X_TOKEN']
    free_time = data['free_time']
    print('check data')
    userlogin = UserLogin.objects.get(token = token)
    if(userlogin.user.role != 2):
        return HttpResponse({'message':'wrong method'},status=HTTPStatus.METHOD_NOT_ALLOWED)

    user = User.objects.get(id=id)
    print(user)
    ids = list(Interviewer.objects.all().values_list('id'))
    print(ids)
    user.interviewer.free_time = free_time
    print('check viewer')
    user.interviewer.save()
    print(user.interviewer.free_time)
    return HttpResponse('succeeded in changing time',status=HTTPStatus.OK)

'''
@require_http_methods(['PUT'])
def put_application_result(req):
    # TODO: PUT /user/application_result
    if req.method != 'PUT':
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)
    email = req.PUT.get('id')
    app_result = request.PUT.get('application_result')
    user = User.objects.get(email=email)
    if user.role != 3:  #确认是给被面试者赋值
        return HttpResponse('change not for interviewee', status=HTTPStatus.METHOD_NOT_ALLOWED)
    viewee = Interviewee.objects.get(user=user)
    viewee.application_result = app_result
    viewee.save()
    return HttpResponse(status=HTTPStatus.OK)
'''

@require_http_methods(['PUT'])
def put_application_result(req):
    # TODO: PUT /user/application_result
    print('start res')
    if req.method != 'PUT':
        return HttpResponse({'message':'wrong method'},status=HTTPStatus.METHOD_NOT_ALLOWED)#确认合法方式
    #token = req.META['HTTP_X_TOKEN']
    data = json.loads(req.body.decode())
    token = data['HTTP_X_TOKEN']
    userlogin = UserLogin.objects.get(token = token)
    print('check login')
    if(userlogin.user.role != 1):
        return HttpResponse({'message':'wrong requirement'}, status=HTTPStatus.METHOD_NOT_ALLOWED)#确认HR身份
    email = data['interviewee']
    result = data['application_result']
    itee = Interviewee.objects.get(email=email)
    print('check itee')
    try:
        HRAssignInterviewee.objects.get(hr=userlogin.user,interviewee=itee)
        itee.application_result = result
        itee.save()
        print('check save')
        return HttpResponse({'message':'result set'},status=HTTPStatus.OK)
    except:
        return HttpResponse({'message':'fail operations'},status=HTTPStatus.OK)


@require_POST
def assign_interviewer(req):
    # TODO: POST /user/assign/interviewer
    if req.method != 'POST':
        return HttpResponse({'message':'wrong method'},status=HTTPStatus.METHOD_NOT_ALLOWED)#确认合法方式
    data = json.loads(req.body.decode())
    token = data['HTTP_X_TOKEN']
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
    # TODO: POST /user/assign/interviewer
    if req.method != 'POST':
        return HttpResponse({'message':'wrong method'},status=HTTPStatus.METHOD_NOT_ALLOWED)#确认合法方式
    data = json.loads(req.body.decode())
    token = data['HTTP_X_TOKEN']
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
