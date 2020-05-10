from http import HTTPStatus
from django.http import HttpResponse


def need_token(handler):
    """一个函数装饰器，用于需要 token 的 route 中
    示例：

    @need_token
    def secret(request, x_token):
        # request 是原来的 request
        # x_token 是提取出来的 header 中 X-Token 域
        pass
    """
    def inner(req, *args, **kwargs):
        try:
            token = req.META['HTTP_X_TOKEN']
        except KeyError:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)
        return handler(req, *args, **kwargs, x_token=token)
    return inner


def send_email(sender, to_list, subject, content):
    # TODO: send_email
    from_addr = sender['from_addr']
    host = sender['host']
    password = sender['password']
    pass
