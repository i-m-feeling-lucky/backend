# Online Interview Backend

在线面试平台后端部分。

## 构建

在文件 `./interview/my.cnf` 中设置 MySQL，示例如下

```ini
[client]
user = username
password = p@ssw0rd
```

创建 MySQL 数据库

```sql
create database interview character set utf8
```

在文件 `./interview/interview/secrets.py` 中设置用于发送邮件的用户

```python
EMAIL_SENDER = {
    'from_addr': 'from@example.com',
    'host': 'smtp.example.com',
    'password': 'p@ssw0rd',
}
```

将 `from_addr` 设置为 `__nosend` 以跳过发邮件的步骤。

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
WorkingDirectory=/path/to/backend/interview
ExecStart=/path/to/pipenv run gunicorn interview.wsgi
```
