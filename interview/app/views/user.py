from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from app.models import User, UserLogin

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
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
    passw = sha256(passw.encode()).hexdigest()
    try:
        user = User.objects.get(email=email, pass_sha256=passw)
    except ObjectDoesNotExist:
        return HttpResponse('{"message": "账号或密码错误"}', status=HTTPStatus.UNAUTHORIZED)
    user_login = UserLogin(user=user)
    user_login.save()
    res = {
        'role': user.role,
        'token': str(user_login.token),
    }
    return HttpResponse(json.dumps(res))


@require_POST
def logout(req):
    try:
        token = req.META['HTTP_X_TOKEN']
        UserLogin.objects.filter(token=token).delete()
    except Exception:
        pass
    return HttpResponse('')


@require_http_methods(['GET', 'POST'])
def user(req):
    if req.method == 'GET':
        return user_infos(req)
    elif req.method == 'POST':
        return add_user(req)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def user_infos(req):
    # TODO: GET /user
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


def add_user(req):
    # TODO: POST /user
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


@require_GET
def user_info(req, id):
    # TODO: GET /user/{id}
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


@require_http_methods(['PUT'])
def put_password(req, id):
    # TODO: PUT /user/{id}/pasword
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


@require_http_methods(['PUT'])
def put_free_time(req, id):
    # TODO: PUT /user/{id}/free_time
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


@require_http_methods(['PUT'])
def put_application_result(req, id):
    # TODO: PUT /user/{id}/application_result
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


@require_POST
def add_assignment(req, id):
    # TODO: POST /user/assignment
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)
