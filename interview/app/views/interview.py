from django.views.decorators.http import require_GET, require_http_methods
from django.http import HttpResponse
from http import HTTPStatus


@require_http_methods(['GET', 'POST'])
def interview(req):
    if req.method == 'GET':
        return interview_infos(req)
    elif req.method == 'POST':
        return add_interview(req)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def interview_infos(req):
    # TODO: GET /interview
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


def add_interview(req):
    # TODO: POST /interview
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


@require_GET
def interview_info(req, id):
    # TODO: GET /interview/{id}
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


@require_GET
def interview_verify(req, id):
    # TODO: GET /interview/{id}/verify
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


@require_http_methods(['PUT'])
def add_evaluation(req, id):
    # TODO: PUT /interview/{id}/evaluation
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


@require_http_methods(['GET', 'POST'])
def history(req, id, ty):
    if req.method == 'GET':
        return get_history(req, id, ty)
    elif req.method == 'POST':
        return add_history(req, id, ty)
    else:
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def get_history(req, id, ty):
    # TODO: GET /interview/{id}/history/{ty}
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)


def add_history(req, id, ty):
    # TODO: POST /interview/{id}/history/{ty}
    return HttpResponse(status=HTTPStatus.NOT_IMPLEMENTED)
