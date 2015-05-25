# Nginx + uWsgi + web.py 搭建LNMP(python)服务器

标签： Nginx uWsgi python web.py  

---

**`debian jessie` 中搭建基于LNMP(python)的博客平台**  
__于2014年10月19日21:39分__  
兼容ubuntu14.04  
这是本博客第一篇博文，也是本博客后台的运行程序的基本环境。  
本博客的源代码即将开源于[github](https://github.com/vanvig)  
部分引用自：[推酷](http://www.tuicool.com/articles/qEVrYn)  

## 安装Nginx ([官网](http://nginx.org/cn/))
```bash
$ sudo aptitude install nginx-full
$ #　手动编译需要PCRE-DEVEL支持
```
## 安装pip
```bash
$ sudo aptitude install python-pip # python的包管理器
```
## 安装uWsgi ([官网](http://projects.unbit.it/uwsgi/))
```bash
$ sudo pip install uwsgi
```
## 安装web.py ([官网](http://webpy.org/))
```bash
$ sudo pip install web.py
```
## 安装MySQL ([mysql-python](http://mysql-python.sourceforge.net/))
```bash
$ sudo aptitude install mysql-server
$ sudo pip install mysql-python
```
## 配置uWsgi
15-05-24折腾记录:  
  - ini配置文件的注释必须是以#为行开头，不支持行内注释  
  - vhost会使session混乱  
  - 涉及到utf8字符的打印等操作会使uwsgi出现问题  

```bash
$ cat /etc/uwsgi.ini
```
```ini
[uwsgi] 
#使用动态端口，启动后将端口号写入以下文件中
socket = /tmp/uwsgi_vhosts.sock
#也可以指定使用固定的端口
#socket=127.0.0.1:9031 
pidfile = /var/run/uwsgi.pid 
logdate = true
logto = /var/log/uwsgi.log

master = true 
vhost = true 
gid = www-data 
uid = www-data
    
chdir = /var/www/blog
# 程序所在目录
module = hello
# 主启动文件名称(不含.py,且需要有可执行权限)
    
#性能相关的一些参数，具体内容查看官网文档
workers = 50
# 启动时生成的进程数
max-requests = 5000 
limit-as = 512
```
更多可参考：[uwsgi官方文档](http://uwsgi-docs.readthedocs.org/en/latest/index.html)
## 配置Nginx

```nginx
    server { 
        listen  8080;   # Nginx监听端口 
        server_name  localhost; # 虚拟主机的域名
        root /var/www/blog;     # 程序根目录
        index index.html index.htm; 
        access_log /var/log/nginx/mysite_access.log; 
        error_log /var/log/nginx/mysite_error.log; 
        location / { 
            #使用动态端口
            # nginx需要有读取权限
            uwsgi_pass unix:///tmp/uwsgi_vhosts.sock;
            #uwsgi_pass 127.0.0.1:9031; 

            include uwsgi_params; 
            uwsgi_param UWSGI_SCRIPT index;   
            uwsgi_param UWSGI_PYHOME /var/www/blog; 
            uwsgi_param UWSGI_CHDIR /var/www/blog; 
        } 
    }
```

## 测试代码
```bash
$ sudo vim /var/www/blog/hello.py
```
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-  

import web

urls = (
        '/t', 'test', #测试
        '/', 'home'
)

app = web.application(urls, globals())
#返回wsgi接口
# 需要在main外面，uwsgi调用不会执行main
application = app.wsgifunc()


class test:
    '测试'	  
    def GET(self):
        # 开发测试用
        referer = web.ctx.env.get('HTTP_REFERER', 'http://google.com')
        client_ip = web.ctx.env.get('REMOTE_ADDR')
        host = web.ctx.env.get('host')
        fullpath = web.ctx.fullpath
        user_agent = web.ctx.env.get('HTTP_USER_AGENT')

        data = ""
        data += 'Client: %s<br/>\n' % client_ip
        data += 'User-agent: %s<br/>\n' % user_agent
        data += 'FullPath: %s<br/>\n' % fullpath
        data += 'Referer: %s<br/>\n' % referer

        return data

    def POST(self):
        pass

class home:
    '根目录请求的处理'		
    def GET(self):
        return "Hello Web.py"

    def POST(self):
        return self.GET()

if __name__ == "__main__":
    app.run()
```
```
$ sudo chmod +x /var/www/blog/hello.py   # 一定记得加权限
```

## 启动Nginx和uWsgi
```shell
$ sudo nginx
$ uwsgi /etc/uwsgi.ini &
```

## 浏览器中测试
<http://localhost:8080>  
<http://localhost:8080/t>  
