# bbs
多人论坛
运行简单说明
自动安装所有依赖项：

pip install -r requirements.txt

先修改DATABASE，选择自己的数据库账号，
然后进行数据迁移：

python manage.py migrate

运行后端服务器：

python manage.py runserver
