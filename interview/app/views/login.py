from django.views.decorators.http import require_POST
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
