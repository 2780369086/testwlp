from django.conf.urls import url
from books import views

urlpatterns = [
    url(r'^$', views.index, name='index'), # 首页

#     详情页
    url(r'books/(?P<books_id>\d+)/$', views.detail, name='detail'),

#     列表页
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)/$', views.list, name='list'),
]