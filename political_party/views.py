from django.shortcuts import render
from .models import News


def index(request):
    news_list = News.objects.all().order_by('-published_at')
    return render(request, 'political_party/index.html', {'news_list': news_list})
