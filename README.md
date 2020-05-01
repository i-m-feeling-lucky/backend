# Online Interview Backend

在线面试平台后端部分。

## 构建

在文件 `./interview/my.cnf` 中设置 MySQL，示例如下

```ini
[client]
user = username
password = p@ssw0rd
```

运行命令

    pipenv install
    pipenv run ./interview/manage.py migrate

## 在生产环境中运行

    cd interview
    pipenv run gunicorn interview.wsgi

一个供参考的 systemd user unit:

```ini
# ~/.config/systemd/user/interview.service
[Unit]
Description=Online Interview Backend

[Service]
ExecStart=/bin/sh -c 'cd /path/to/backend/interview && pipenv run gunicorn interview.wsgi'
```
