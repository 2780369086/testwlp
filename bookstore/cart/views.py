from django.shortcuts import render
from django.http import JsonResponse
from books.models import Books
from utils.decorators import login_required
from django_redis import get_redis_connection

# Create your views here.



# 向购物车添加商品
def cart_add(request):
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请先登录'})

	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')

	if not all([books_id,books_count]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})

	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		return JsonResponse({'res':2,'errmsg':'商品不存在'})

	try:
		count = int(books_count)

	except Exception as e:
		return JsonResponse({'res':3,'errmsg':'商品数量必须为数字'})
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' %request.session.get('passport_id')

	res = conn.hget(cart_key,books_id)
	if res is None:
		res = count

	else:
		res = int(res) + count

	if res > books.stock:
		return  JsonResponse({'res':4,'errmsg':'商品库存不足'})

	else:
		conn.hset(cart_key,books_id,res)

	return JsonResponse({'res':5})




# 渲染购物车页面
def cart_count(request):
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0})

	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')

	res = 0
	res_list = conn.hvals(cart_key)

	for i in res_list:
		res += int(i)

	return JsonResponse({'res':res})


# 展示购物车页面
@login_required
def cart_show(request):
	# 显示用户购物车页面
	passport_id = request.session.get('passport_id')
	# 获取用户购物车的记录
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % passport_id
	res_dict = conn.hgetall(cart_key)
	# 订单列表
	books_li = []

	# 保存所有商品的总数
	total_count = 0

	# 保存所有商品的总价
	total_price = 0

	# 遍历res_dict获取商品的数据
	for id,count in res_dict.items():
		# 根据id获取商品的信息
		books = Books.objects.get_books_by_id(books_id=id)
		# 保存商品的数目
		books.count = count
		# 保存商品的小计
		books.amount = int(count) * books.price
		books_li.append(books)

		total_count += int(count)
		total_price += int(count) * books.price

	# 定义模板上下文
	context = {
		# 订单列表
		'books_li':books_li,
		# 商品总数
		'total_count':total_count,
		# 商品总价
		'total_price':total_price,
	}
	# 					购物车订单列表页面
	return render(request, 'cart/cart.html', context)



# 购物车中删除商品的功能
def cart_del(request):

	# 判断用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请登录'})
	#接收数据
	books_id = request.POST.get('books_id')

	# 校验商品是否存放
	if not all([books_id]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})
	books = Books.objects.get_books_by_id(books_id=books_id)

	if books is None:
		return JsonResponse({'res':2,'errmsg':'商品不存放'})

	# 删除购物车信息
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')
	conn.hdel(cart_key,books_id)
	# 返回信息
	return JsonResponse({'res':3})


# 更新购物车的接口
def cart_update(request):
	# 判断用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({'res':0,'errmsg':'请登录'})

	# 接收数据
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')

	# 数据校验
	if not all([books_id,books_count]):
		return JsonResponse({'res':1,'errmsg':'数据不完整'})
	books = Books.objects.get_books_by_id(books_id=books_id)
	if books is None:
		return JsonResponse({'res':2,'errmsg':'商品不存在'})
	try:
		books_count = int(books_count)

	except Exception as e:
		return JsonResponse({'res':3,'errmsg':'商品数目必须为数字'})

	# 更新操作
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')

	# 判断商品库存
	if books_count > books.stock:
		return JsonResponse({'res':4,'errmsg':'商品库存不足'})
	conn.hset(cart_key,books_id,books_count)
	return JsonResponse({'res':5})