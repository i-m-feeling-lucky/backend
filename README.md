# Online Interview Backend

在线面试平台后端部分。

## 构建

    pipenv install

在文件 `./interview/my.cnf` 中设置 MySQL，示例如下

```ini
[client]
user = username
password = p@ssw0rd
```

## 在生产环境中运行

    cd interview
    pipenv run gunicorn interview.wsgi
