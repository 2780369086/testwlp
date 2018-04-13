from django.db import models

# 抽象出一个BaseModel，一个基本模型，因为数据表有共同的字段，我们就可以把它抽象出来
class BaseModel(models.Model):
    # 模型抽象为基类
    # is_delete（软删除）
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')
    # create_at（创建时间）
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # update_at（更新时间）
    update_time = models.DateTimeField(auto_now=TabError, verbose_name='更新时间')

    class Meta:
        abstract = True