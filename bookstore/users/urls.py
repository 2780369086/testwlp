from django.conf.urls import url

from users import views

urlpatterns = [
	# 用户注册
	url(r'^register/$',views.register,name='register'),

	# 注册页面表单提交
	url(r'^register_handle/$', views.register_handle, name='register_handle'),

	# 显示登录页面
	url(r'^login/$',views.login,name='login'),

	#用户登录校验
	url(r'^login_check/$',views.login_check,name='login_check'),

# 	用户退出登录
	url(r'^logout/$',views.logout,name='logout'),

# 	用户中心订单页
	url(r'^order/$',views.order,name='order'),

	# 用户中心-信息页
	url(r'^$', views.user, name='user'),

# 	用户中心地址页
	url(r'^address/$',views.address,name='address'),

# 	验证码功能
	url(r'^verifycode/$',views.veriycode,name='verifycode'),
# 用户激活
	url(r'^active/(?P<token>.*)/$', views.register_active, name='active'),



]
