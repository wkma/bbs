# bbs
多人论坛

运行说明
自动安装所有依赖项：

1.pip install -r requirements.txt

2.先修改DATABASE，
选择自己的数据库账号，
然后进行数据迁移：
python manage.py migrate

运行后端服务器：

3.python manage.py runserver
