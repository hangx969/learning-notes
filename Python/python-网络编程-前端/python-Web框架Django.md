# Django介绍

Django 是一个开源的 Python Web 框架，旨在帮助开发者快速创建高效、可扩展的 Web 应用。

特点：

1. 快速开发：通过内置功能减少开发时间。
2. 安全性：提供保护用户数据和避免常见安全漏洞的功能。
3. 可扩展性：可根据需要扩展应用功能。

安装：

~~~sh
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple django
~~~

# 初始化Django项目

~~~sh
# 打开terminal
django-admin startproject myproject
~~~

会创建两个同名的 myproject 文件夹。

- 第一个 myproject 文件夹是项目的根目录。

- 第二个 myproject 文件夹是项目的实际应用目录，它包含项目的配置和应用代码。

这是 Django 的默认项目结构设计，目的是将项目的代码与项目的外部管理文件（如版本控制文件、虚拟环境、其他工具的配置文件）分开。

下面是两层目录的具体作用：

1. 外层 myproject/（项目根目录）

  这是项目的根目录，用于存放管理项目的相关文件。这一层通常包含项目级别的内容，如 manage.py、虚拟环境、依赖库的 requirements.txt 或者 pyproject.toml 文件等。目录结构示例：

  myproject/

  ​    manage.py

  ​    myproject/ # 这个是内层目录

  1）manage.py

  作用：这是 Django 项目中的管理脚本。

  功能：通过这个脚本，你可以运行常用的 Django 命令，如启动开发服务器 (runserver)、数据库迁移 (migrate)、创建管理员账号(createsuperuser) 等。示例：python manage.py runserver

2. 内层 myproject/（项目应用目录）

  这个文件夹是项目的实际应用目录，它包含与 Django 框架相关的核心配置文件和代码（如settings.py、urls.py、asgi.py、wsgi.py、__init__.py）。目录结构示例：

  myproject/
      \__init\_\_.py
      asgi.py
      settings.py
      urls.py
      wsgi.py

  功能：这一层是项目代码的存放位置，Django 会在这里查找应用的配置、URL 路由和启动文件

  1. myproject/__init__.py

     作用：这是一个空文件，用来告诉 Python，myproject 目录应该被视为一个包（package）。

     功能：有了这个文件，Django 项目可以将 myproject 目录作为一个模块导入，Python 脚本可以引用其中的内容。

     2. myproject/settings.py

        作用：这是 Django 项目的核心配置文件。

        功能：定义项目的所有设置，如数据库连接、时区设置、已安装的应用（INSTALLED_APPS）等。

        常见配置：

        - 数据库设置 (DATABASES)

        - 已安装的应用 (INSTALLED_APPS)

        - 中间件 (MIDDLEWARE)

        - 模板路径 (TEMPLATES)

  3. myproject/urls.py

     作用：用于定义项目的 URL 路由。

     功能：它决定了用户访问某个 URL 时，应该调用哪个视图（view）。通过 urlpatterns 列表，Django 将不同的 URL 与相应的视图函数或类关联起来。

     示例：

     ~~~python
     from django.urls import path
     from . import views
     urlpatterns = [
     path('home/', views.home_view),
     ]
     ~~~

  4. myproject/asgi.py

     作用：用于 ASGI（Asynchronous Server Gateway Interface）服务器的入口文件。

     功能：ASGI 是 Django 的异步服务器接口，它支持 WebSocket 等异步操作。这个文件用于在使用 ASGI 服务器时，启动 Django 应用程序。

     使用场景：当你需要运行异步任务或 WebSocket 连接时，ASGI 比 WSGI 更合适。

  5. myproject/wsgi.py

     作用：用于 WSGI（Web Server Gateway Interface）服务器的入口文件。

     功能：WSGI 是 Django 项目在生产环境中常用的 Web 服务器接口。这个文件定义了项目的 WSGI 应用对象，Web 服务器通过这个文件来启动 Django 项目。

     使用场景：通常在部署 Django 项目时，使用 gunicorn、uWSGI 等服务器，都会通过这个文件来启动项目。

# 启动Django项目

~~~python
# 进入项目目录，启动web服务器
cd myproject
python manage.py runserver
~~~

# 创建Django应用

## 创建应用

1. 在终端中，确保你在项目目录下，输入以下命令创建一个新的应用：

   ~~~sh
   python manage.py startapp myapp
   ~~~

   myapp 是你的应用名称，是 Django 项目中的一个子模块，通常负责处理某一类功能或逻辑（例如博客、用户管理、商品管理）。每个应用是相对独立的，但会与项目的 settings.py 配置结合在一起。settings.py 是整个项目级别的配置文件，settings.py 只存在于整个项目的配置中，而不是每个应用中。

2. 在项目配置目录下的 settings.py 文件中，将新创建的应用添加到 INSTALLED_APPS 中：

   ~~~python
   INSTALLED_APPS = [
   'django.contrib.admin',
   'django.contrib.auth',
   'django.contrib.contenttypes',
   'django.contrib.sessions',
   'django.contrib.messages',
   'django.contrib.staticfiles',
   'myapp', # 添加你的应用名称
   ]
   ~~~

## 创建视图

在 myapp/views.py 文件中，定义一个简单的视图函数：

~~~python
from django.shortcuts import render
from django.http import HttpResponse

# 视图函数
def home(request):
	return HttpResponse("Hello, Django!")
~~~

1. from django.http import HttpResponse

   作用：从 Django 的 http 模块中导入 HttpResponse 类。

   功能：HttpResponse 是 Django 中用来生成 HTTP 响应对象的类。通过它，服务器可以返回 HTTP 响应给客户端（例如浏览器）。在这个例子中，HttpResponse 用于返回一个包含文本的响应。

2. 定义视图函数 home(request)

   作用：定义了一个名为 home 的视图函数。

   request 参数：request 是 Django 自动传递给视图函数的参数。它是一个包含所有请求信息的对象。当用户在浏览器中访问某个 URL 时，Django 就会创建一个 request 对象，里面包含了很多信息，比如：

   - URL：用户访问的网页地址。
   - GET/POST 参数：如果用户通过表单提交数据，这些数据会包含在 request 中
   - 用户信息：如果用户已登录，request 对象中会包含用户的相关信息。

   通过 request 参数，视图函数可以知道用户访问了哪个页面，提交了哪些数据，并基于这些信息做出相应的处理。

3. return HttpResponse("Hello, Django!")

   作用：返回一个 HttpResponse 对象，内容是 "Hello, Django!"。

   功能：这表示服务器会把 "Hello, Django!" 这个字符串返回给客户端（例如浏览器），浏览器就会在网页上显示这个内容。

视图函数的功能：这个函数的目的是处理一个客户端的 HTTP 请求，并返回一个响应。在这里，它简单地返回一个包含字符串 "Hello, Django!" 的 HTTP 响应。

## 配置URL路由

在 myapp 目录下创建一个新的文件 urls.py，并添加以下内容：

~~~python
from django.urls import path
from .views import home
urlpatterns = [
	path('', home, name='home'), # 根路径对应 home 视图
]
~~~

代码解释：

这段代码是 Django 项目中用于定义 URL 路由的部分。它将用户访问的 URL 路径映射到相应的视图函数。

在 Django 中，path 函数用于定义 URL 和视图函数之间的关系，也就是路由。它告诉 Django，当用户访问某个特定的 URL 时，应该调用哪个视图函数来处理这个请求。

1. 第一个参数 '' 是空字符串，它表示网站的根 URL。也就是说，path('', home, name='home') 匹配的是你网站的根路径，例如 http://localhost:8000/。
2. 第二个参数 home 是你之前定义的视图函数。它告诉 Django，当用户访问根 URL 时（例如 http://localhost:8000/），需要调用 home 视图函数来处理这个请求。
3. 第三个参数 name='home' 给这个路由起了一个名字。这是可选的，但很有用。通过给路由命名，可以在 Django 项目的其他地方方便地引用这个 URL。比如在 Django 的模板中，你可以使用 {% url 'home' %} 生成指向这个视图的链接。这比手动写死 URL 更灵活，因为如果 URL 以后发生变化，只需要修改路由，而不需要修改模板中的链接。

## 配置admin后台

【可选】在项目的主 urls.py 文件中（通常在 myproject/urls.py），添加 myapp 的 URL 配置：
~~~python
from django.contrib import admin
from django.urls import path, include # 引入 include
urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('myapp.urls')), # 包含 myapp 的 URL
]
~~~

path('admin/', admin.site.urls)，解释：

1. 第一个参数 'admin/'：表示匹配 URL 路径 http://localhost:8000/admin/。
2. 第二个参数 admin.site.urls：表示当用户访问这个路径时，调用 Django 的内置管理后台的路由配置。

# 使用ORM模型与数据库交互

ORM是对象关系映射模型，是 Django 框架中用于与数据库进行交互的模型。它允许使用 Python 类来定义数据库表，并通过 Python 代码执行 SQL 操作，如查询、插入、更新和删除数据。

Django 中的每个模型（类）通常对应数据库中的一个表，模型的每个属性对应表中的一列。

## 创建模型

在 myapp/models.py 文件中定义类（模型）：

~~~python
from django.db import models

class Article(models.Model):
	title = models.CharField(max_length=100) # 文章标题
	content = models.TextField() # 文章内容
	created_at = models.DateTimeField(auto_now_add=True) # 创建时间
	def __str__(self):
		return self.title # 返回文章标题作为字符串表示
    # __str__ 方法的作用：__str__ 是 Python 中的一个特殊方法。它的目的是告诉 Python，当你试图打印一个对象时，应该返回什么内容。
    # 为什么需要 __str__ 方法？默认输出不友好：如果没有定义 __str__ 方法，当你打印一个模型的实例时，Python 会返回类似Article object (1) 的内容。这种输出不容易理解，因为它只是告诉你这是一个 Article 对象，并给了你一个内部的 ID，但没有提供有用的信息。
~~~

在 Django 中，models.Model 是用于定义数据模型的基类。

- 基类：models.Model 是所有模型类的父类。你创建的每个模型类都必须继承父类，这样 Django 才能知道该类与数据库中的哪个表相对应。

- 数据库表映射：当你定义一个类（模型）时，Django 会自动将这个类映射到数据库中的一张表。例如，如果你创建了一个名为 Article的模型类，Django 会在数据库中创建一个名为 Article的表。

## 数据库迁移

在 Django 中，迁移（migrations）是管理数据库模式变化的一种机制。每当你对模型类（即 Django 中的 models.Model 子类）进行更改时，例如添加、删除字段或更改字段类型，Django 会生成迁移文件，以便将这些更改应用到数据库中。

### 创建数据库迁移文件

~~~sh
python manage.py makemigrations
~~~

1. makemigrations 的作用

   创建迁移文件：当你运行 python manage.py makemigrations 时，Django 会检查你在模型类中所做的更改，并生成相应的迁移文件。这些文件包含了需要在数据库中执行的操作，比如创建表、添加字段等。执行后，Django 会生成一个新的迁移文件，通常位于你的应用程序的 migrations 目录下，文件名可能类似于 0001_initial.py。这个文件中会记录你对 Article 模型所做的更改

### 应用迁移到数据库

~~~sh
python manage.py migrate
# 这个命令会根据之前生成的迁移文件更新数据库结构，确保数据库与模型类的定义保持一致。
# 例如，它会创建一个 Article 表，并添加 title、content 和 created_at 这三列数据。
~~~

### 添加数据

在 Django shell 中添加数据。首先打开shell终端

~~~sh
python manage.py shell
# 这个命令让你可以在 Django 项目环境中直接使用 Python 进行交互式编程。启动这个 shell 后，你可以访问 Django 项目的所有组件，例如模型、数据库、配置等。
~~~

添加一篇文章：

~~~sh
# 导入模型
>>>from myapp.models import Article
# 创建一个文章对象
>>>article = Article(title="My First Article", content="This is the content of my first article.")
# 保存到数据库
>>>article.save()
# 这段代码创建了一个新的 Article 对象，标题为 "My First Article"，内容为 "This is the content of my first article."。然后使用 save() 方法将这篇文章保存到数据库中。
>>> article = Article(title="My Second Article", content="This is the content of my second article.")
>>> article.save()
~~~

### 查询数据

查询并打印所有文章：

~~~sh
# 获取数据库中所有文章
articles = Article.objects.all()
# 打印每篇文章的标题
for article in articles:
	print(article.title)
~~~

这段代码会从数据库中获取所有的 Article，并循环遍历每篇文章，将它们的标题打印出来。

# 模板与视图结合：动态渲染HTML文档

## 创建模板

在 myapp 目录下创建一个名为 templates 的文件夹，然后在 templates 中创建home.html 文件：

~~~html
<!DOCTYPE html>
<html>
<head>
  <title>My Articles</title>
</head>
<body>
  <h1>Articles</h1>
  <ul>
    {% for article in articles %}
      <li>{{ article.title }}</li>
    {% endfor %}
  </ul>
</body>
</html>
~~~

- {% for article in articles %}: 这是 Django 模板语言，表示一个循环。它会遍历 articles 变量中的每一个元素，article 是当前迭代的元素。articles 是 Django 视图函数中传递给模板的数据，在视图函数中我们获取了数据库中的所有文章 :(Article.objects.all())。

- \<li>{{ article.title }}\</li>:这是列表项 (\<li> 标签)。


- {{ article.title }} 是 Django 模板中的变量表达式，用来获取 article 对象的 title 字段（文章标题），并将其插入到 HTML 中。这表示每篇文章的标题会被显示在页面上。

## 修改视图以使用模板

修改 myapp/views.py 文件中的 home 视图函数，以渲染模板：

~~~python
from django.shortcuts import render
from django.http import HttpResponse
from .models import Article

def home(request):
    articles = Article.objects.all() # 从数据库中获取所有文章
    return render(request, 'home.html', {'articles': articles}) # 渲染模板并传递文章数据
~~~

1. 用户访问 home 页面时，Django 会调用这个 home 视图函数。
2. 视图函数从数据库中获取所有 Article（文章）对象。
3. 然后，它通过 render() 函数，将文章数据传递给模板 'home.html' 进行渲染。
4. 最终，渲染后的 HTML 页面作为响应返回给用户，用户的浏览器将看到所有文章的列表。

运行程序：

~~~sh
python manage.py runserver
~~~

# 表单创建与数据处理

前端是HTML，后端是Django，Django渲染HTML页面。

## 创建表单

在 myapp/forms.py 文件中，创建一个表单类：

~~~python
from django import forms # 用于创建和处理 HTML 表单。
class ArticleForm(forms.Form): 
# 定义一个表单类：这里定义了一个名为 ArticleForm 的类，它继承自 forms.Form。这个类用来创建一个表单，表单里有两个字段：title 和 content。
    title = forms.CharField(label='Title', max_length=100) # forms.CharField() 创建一个输入框（HTML 的 <input type="text">），用来填写文章的标题。
    content = forms.CharField(label='Content', widget=forms.Textarea) # 将默认的文本输入框（即 <input>）替换为多行文本框（即 <textarea>）
~~~

通过 ArticleForm 类，Django 将自动为我们生成一个 HTML 表单，包括两个字段：

1. 标题字段 (title)：一个文本输入框，最多可以输入 100 个字符。
2. 内容字段 (content)：一个多行文本框，用来输入文章的内容。

## 处理表单提交

在 myapp/views.py 中添加一个处理表单的视图：

~~~python
from django.shortcuts import render
from django.http import HttpResponse
from .models import Article
from django.shortcuts import redirect
from .forms import ArticleForm

def home(request):
    articles = Article.objects.all() # 从数据库中获取所有文章
    return render(request, 'home.html', {'articles': articles}) # 渲染模板并传递文章数据

def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            Article.objects.create(title=title, content=content) # 创建文章
            return redirect('home') # 重定向到首页
    else:
        form = ArticleForm()
    return render(request, 'create_article.html', {'form': form}) # 渲染表单
~~~

## 添加URL路由

在 myapp/urls.py 中添加新的 URL 路由：

~~~python
from django.urls import path
from .views import home
from django.shortcuts import redirect
from .views import home,create_article

urlpatterns = [
    path('', home, name='home'),
    path('create/', create_article, name='create_article'), # 创建文章
]
~~~

## 添加表单html页面

在 templates 文件夹中创建 create_article.html：

~~~html
<!DOCTYPE html>
<html>
<head>
    <title>Create Article</title>
</head>
<body>
    <h1>Create New Article</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Submit</button>
    </form>
</body>
</html>
~~~

## 访问创建文章页面

~~~sh
python manage.py runserver
# http://127.0.0.1:8000/create
~~~

# 用户注册与登录

## 用户注册功能

首先，我们需要实现用户的注册功能。在 Django 中，User 模型（从 django.contrib.auth.models 导入）提供了内置的用户管理功能。为了实现注册功能，我们将创建一个视图 register，通过它用户可以输入用户名和密码来创建一个新账户。

### 创建视图

myapp/views.py代码，新增如下内容：

~~~python
from django.contrib.auth.models import User # 导入用户模型
from django.contrib.auth import authenticate, login # 导入认证和登录函数
from django.shortcuts import redirect, render # 导入重定向和渲染函数

def register(request):
    if request.method == 'POST': # 检查请求方法是否为 POST，表单提交时为 POST 请求
        username = request.POST['username'] # 从表单中获取用户名
        password = request.POST['password'] # 从表单中获取密码
        user = User.objects.create_user(username=username, password=password) # 创建新用户
        return redirect('home') # 注册成功后重定向到主页
    return render(request, 'register.html') # 如果不是 POST 请求，渲染注册页面
~~~

### 添加URL路由

在 myapp/urls.py 文件中，为 register 视图创建路由，使用户可以通过特定的 URL 访问注册页面。

~~~python
from django.urls import path
from .views import register # 导入 register 视图

urlpatterns = [
    path('register/', register, name='register'), # 注册页面的 URL 路由
]
~~~

### 创建注册页面html

注册页面前端是通过 HTML 模板呈现的，它包含一个表单，让用户输入用户名和密码。在 templates 文件夹中创建 register.html：

~~~html
<!DOCTYPE html>
<html>
<head>
  <title>Register</title>
</head>
<body>
  <h1>Register</h1>
  <form method="post"> <!-- 表单使用 POST 方法提交数据 -->
    {% csrf_token %} <!-- Django 的安全机制，防止跨站请求伪造攻击 -->
    <label for="username">Username:</label>
    <input type="text" name="username" required> <!-- 用户名输入框 -->
    <label for="password">Password:</label>
    <input type="password" name="password" required> <!-- 密码输入框 -->
    <button type="submit">Register</button> <!-- 提交按钮 -->
  </form>
</body>
</html>
~~~

### 访问注册页面

~~~sh
http://127.0.0.1:8000/register
~~~

## 用户登录功能

### 创建登录视图

登录视图允许用户通过输入用户名和密码来验证其身份，并登录系统。我们使用 Django 内置的 authenticate 和 login 函数来处理用户认证和登录。myapp/views.py代码，新增如下内容：

~~~python
from django.contrib.auth import authenticate, login # 导入认证和登录函数
from django.shortcuts import redirect, render # 导入重定向和渲染函数

def user_login(request):
    if request.method == 'POST': # 检查请求方法是否为 POST
        username = request.POST['username'] # 获取提交的用户名
        password = request.POST['password'] # 获取提交的密码
        user = authenticate(request, username=username, password=password) # 验证用户身份
        if user is not None: # 如果验证通过
            login(request, user) # 登录用户
            return redirect('home') # 重定向到主页
    return render(request, 'login.html') # 如果请求不是 POST，渲染登录页面
~~~

### 添加URL路由

同样，我们需要在 myapp/urls.py 文件中为 user_login 视图添加一个路由。

~~~python
from django.urls import path
from .views import user_login # 导入 user_login 视图

urlpatterns = [
    path('login/', user_login, name='login'), # 登录页面的 URL 路由
]
~~~

### 创建登录模板

登录页面是一个简单的 HTML 表单，用户输入用户名和密码以登录。在 templates 文件夹中创建 login.html：
~~~html
<!DOCTYPE html>
<html>
<head>
  <title>Login</title>
</head>
<body>
  <h1>Login</h1>
  <form method="post"> <!-- 表单使用 POST 方法提交数据 -->
    {% csrf_token %} <!-- Django 的安全机制，防止跨站请求伪造攻击 -->
    <label for="username">Username:</label>
    <input type="text" name="username" required> <!-- 用户名输入框 -->
    <label for="password">Password:</label>
    <input type="password" name="password" required> <!-- 密码输入框 -->
    <button type="submit">Login</button> <!-- 提交按钮 -->
  </form>
</body>
</html>
~~~

