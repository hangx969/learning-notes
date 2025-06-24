from django.shortcuts import render
from django.http import HttpResponse
from .models import Article
from django.shortcuts import redirect
from .forms import ArticleForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login

def home(request):
    articles = Article.objects.all()  # 从数据库中获取所有文章
    return render(request, 'home.html', {'articles': articles})  # 渲染模板并传递文章数据

def create_article(request):
    if request.method == 'POST':
        form=ArticleForm(request.POST)
        if form.is_valid():
            title=form.cleaned_data['title']
            content=form.cleaned_data['content']
            Article.objects.create(title=title,content=content)
            return redirect('home')
    else:
        form=ArticleForm()
    return render(request,'create_article.html',{'form':form})


def register(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=User.objects.create_user(username=username,password=password)
        return redirect('home')
    return render(request,'register.html')


def user_login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
    return render(request,'login.html')