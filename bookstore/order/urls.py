from django.conf.urls import url
from order import views

urlpatterns = [
# 	 提交订单页面
	url(r'^place/$',views.order_place,name='place'),

# 	生成订单
	url(r'^commit/$',views.order_commit,name='commit'),

# 订单支付
	url(r'^pay/$',views.order_pay,name='pay'),
# 	查询支付结果
	url(r'^check_pay/$',views.check_pay,name='check_pay')
]
