from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=100)  # 文章标题
    content = models.TextField()  # 文章内容
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return self.title  # 返回文章标题作为字符串表示

