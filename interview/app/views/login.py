from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from app.models import User, UserLogin

from uuid import uuid4
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
        return HttpResponse('{}')
    tok = uuid4()
    user_login = UserLogin(user=user, token=tok)
    user_login.save()
    res = {
        'name': user.name,
        'role': user.role,
        'token': str(tok),
    }
    return HttpResponse(json.dumps(res))


@require_POST
def logout(req):
    try:
        data = json.loads(req.body.decode())
        email = data['email']
        token = data['token']
        user = User.objects.get(email=email)
        UserLogin.objects.get(user=user, token=token).delete()
    except Exception:
        pass
    return HttpResponse('')
