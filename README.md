# 仅展示用，提供部分代码，切勿转载使用！！！
## svp可视化平台
> 技术栈

>> 后端
* Django
* djangorestframework
* channels
* MySQL
* redis
>> 前端
* Layui
* Django template

> 目录结构

![目录结构](https://github.com/FrankDC/svp/blob/master/static/image/svp/directory_structure.png)

## 服务安装、启动
> vim /etc/supervisord.d/svp-daphne.ini
```
command = /data/.virtualenvs/svp/bin/daphne -b 127.0.0.1 -p 8055 --proxy-headers small_platform.asgi:application
directory = /data/.virtualenvs/svp/small_platform
user = root
autostart = true
autorestart = true
stopwaitsecs = 5
redirect_stderr = true
stdout_logfile = /var/log/supervisor/svp-daphne.log
stdout_logfile_maxbytes = 10MB
stdout_logfile_backups = 10
```
```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
mkdir /.small_platform/static/ -p
python manage.py collectstatic
sh uwsgi.sh start
sh celeryd_svp start
supervisorctl svp-daphne start
```

## 首页
![首页](https://github.com/FrankDC/svp/blob/master/static/image/svp/home.png)

## 资产库
![资产库](https://github.com/FrankDC/svp/blob/master/static/image/svp/hosts.png)

## 资产组
![资产组](https://github.com/FrankDC/svp/blob/master/static/image/svp/host_group.png)
> 发布系统、日志录入部署到机器都是从资产组获取机器IP

## 物理环境发布系统
![物理发布系统](https://github.com/FrankDC/svp/blob/master/static/image/svp/release_one.png)
![物理发布系统](https://github.com/FrankDC/svp/blob/master/static/image/svp/release_two.png)

* 发布项目管理
![项目管理](https://github.com/FrankDC/svp/blob/master/static/image/svp/release_project1.png)
![项目管理](https://github.com/FrankDC/svp/blob/master/static/image/svp/release_project2.png)

* 节假日控制发布权限 [系统]->[发布系统权限]
![发布系统权限控制，以及svp后台管理](https://github.com/FrankDC/svp/blob/master/static/image/svp/admin.png)

## 容器环境发布系统
![容器发布系统](https://github.com/FrankDC/svp/blob/master/static/image/svp/container_release.png)
> 涉及的APIs：
* gitlab
* jenkins
* blueocean[jenkins的插件]
* k8s
* daphne[supervisor守护进程，名称svp-daphne]

## DNS线路分类启停
![DNS切换](https://github.com/FrankDC/svp/blob/master/static/image/svp/dns_switch.png)
> 万网、dnspod上更新线路，需要在后台先删除再新增

## 数据库主从切换
![数据库切换](https://github.com/FrankDC/svp/blob/master/static/image/svp/db_switch.png)
> 切换前后主从关系在后台配置好，支持调用外部脚本

## felk日志录入
![日志录入](https://github.com/FrankDC/svp/blob/master/static/image/svp/felk.png)
> 支持行日志和json类型日志

## end
