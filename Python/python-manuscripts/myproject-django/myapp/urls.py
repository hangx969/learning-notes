from django.urls import path
from .views import home,create_article
from .views import register
from .views import user_login
urlpatterns = [
    path('', home, name='home'),  # 根路径对应 home 视图
    path('create/',create_article,name='create_article'),
    path('register/',register,name='register'),
    path('login/',user_login,name='user_login'),
]
