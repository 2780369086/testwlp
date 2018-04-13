from django.conf.urls import url
from cart import views

urlpatterns = [
	# 添加购物车数据
	url(r'^add/$',views.cart_add,name='add'),

	# 获取用户购物车中商品的数量
	url(r'^count/$',views.cart_count,name='count'),

	# 显示购物车页面
	url(r'^$',views.cart_show,name='show'),

	# 购物车商品记录删除
	url(r'^del/$',views.cart_del,name='delete'),

]