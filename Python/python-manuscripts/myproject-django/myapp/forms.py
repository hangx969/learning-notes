from django import forms

class ArticleForm(forms.Form):
    title=forms.CharField(label='Title',max_length=100)
    content=forms.CharField(label='Content',widget=forms.Textarea)

