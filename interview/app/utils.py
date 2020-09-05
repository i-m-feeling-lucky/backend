from http import HTTPStatus
from django.http import HttpResponse
from django.conf import settings

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header


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


def send_email(send_to, subject, content):
    """发送邮件
    send_email('sendto_addr@example.com', '主题', '纯文本正文')
    """
    sender = settings.EMAIL_SENDER
    from_addr = sender['from_addr']
    if from_addr == '__nosend':
        return
    host = sender['host']
    password = sender['password']

    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8').encode()
    msg['From'] = formataddr((Header('在线面试系统', 'utf-8').encode(), from_addr))
    msg['To'] = send_to

    with smtplib.SMTP_SSL(host) as server:
        server.login(from_addr, password)
        server.sendmail(from_addr, [send_to], msg.as_string())
