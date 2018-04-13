from django.contrib import admin

from books.models import Books

# Register your models here.


# 在admin中添加关于商品添加的功能
admin.site.register(Books)
