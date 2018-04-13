from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
import re
from users.models import Passport
from django.http import JsonResponse
from order.models import OrderInfo,OrderGoods
from users.models import Address
from utils.decorators import login_required
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from users.tasks import send_active_email
from django.core.mail import send_mail
from django.http import HttpResponse
from django_redis import get_redis_connection
from books.models import Books

# Create your views here.

# 用户注册处理
def register_handle(requst):
	username = requst.POST.get('user_name')
	password = requst.POST.get('pwd')
	email = requst.POST.get('email')

	if not all([username,password,email]):
		return render(requst,'users/register.html',{'errmsg':'参数不能为空'})

	if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
		return render(requst,'users/register.html',{'errmsg':'邮箱不合法'})

	p = Passport.objects.check_passport(username=username)

	if p:
		return render(requst,'users/register.html',{'errmsg':'用户名已存在'})

	passport = Passport.objects.add_one_passport(username=username,password=password,email=email)
	serializer = Serializer(settings.SECRET_KEY, 3600)
	token = serializer.dumps({'confirm': passport.id})  # 返回bytes
	token = token.decode()

	# send_active_email.delay(token, username, email)

	# send_mail('尚硅谷书城用户激活','','settings.EMAIL_FROM',[email],html_message='<a href="http://127.0.0.:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token)
	send_mail('尚硅谷书城用户激活', '', settings.EMAIL_FROM, [email],html_message='<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token)


	return redirect(reverse('books:index'))

# 用户中心地址页
@login_required
def address(request):
	# 获取登录用户的id
	passport_id = request.session.get('passport_id')

	if request.method == 'GET':
		# 显示地址页面
		# 查询用户的默认地址
		addr = Address.objects.get_default_address(passport_id=passport_id)
		return render(request,'users/user_center_site.html',{'addr':addr,'page':'address'})

	else:
		# 添加收货地址
		# 接收数据
		recipient_name = request.POST.get('username')
		recipient_addr = request.POST.get('addr')
		zip_code = request.POST.get('zip_code')
		recipient_phone = request.POST.get('phone')
		#进行校验
		if not all([recipient_name,recipient_addr,zip_code,recipient_phone]):
			return render(request,'users/user_center_site.html',{'errmsg':'参数不必为空'})
		# 添加收货地址
		Address.objects.add_one_address(passport_id=passport_id,
										recipient_name=recipient_name,
										recipient_addr=recipient_addr,
										zip_code=zip_code,
										recipient_phone=recipient_phone)
		#返回应答
		return redirect(reverse('user:address'))

@login_required
# 用户中心信息页
def user(request):
	passport_id = request.session.get('passport_id')
	addr = Address.objects.get_default_address(passport_id=passport_id)
	con = get_redis_connection('default')
	key = 'history_%d' % passport_id

	books_li = []

	for id in books_li:
		books = Books.objects.get_books_by_id(books_id=id)
		books_li.append(books)


	return render(request,'users/user_center_info.html',{
		'addr':addr,
        'page':'user',
        'books_li':books_li
	})


def logout(request):
	request.session.flush()
	return redirect(reverse('books:index'))



def login_check(request):
	# 用户登录校验
	#  获取数据
	username = request.POST.get('username')
	password = request.POST.get('password')
	remember = request.POST.get('remember')
	# veriycode = request.POST.get('veriycode')
	verifycode = request.POST.get('verifycode')
	#     数据校验
	if not all([username,password,remember,veriycode]):
		print(111)
		print(username)
		print(password)
		print(remember)
		print(veriycode)
		return JsonResponse({'res':2})

	if verifycode.upper() != request.session['verifycode']:
		return JsonResponse({'res': 2})

	passport = Passport.objects.get_one_passport(username=username,password=password)

	if passport:
		next_url =reverse('books:index')
		jres = JsonResponse({'res':1,'next_url':next_url})

		if remember == 'true':
			jres.set_cookie('username',username,max_age=7*24*3600)

		else:
			jres.delete_cookie('username')

		request.session['islogin'] = True
		request.session['username'] = username
		request.session['passport_id'] = passport.id
		return jres

	else:
		return JsonResponse({'res':0})

def login(request):
	# 显示登录页面
	username = ''
	checked = ''
	context = {
        'username':username,
        'checked':checked,
	}

	return render(request,'users/login.html',context)

def register(request):
	# 显示用户注册页面
	return render(request, 'users/register.html')



# 用户中心订单页
@login_required
def order(request):
	passport_id = request.session.get('passport_id')
	order_li = OrderInfo.objects.filter(passport_id=passport_id)
	for order in order_li:
		order_id = order.order_id
		order_books_li = OrderGoods.objects.filter(order_id=order_id)
		for order_books in order_books_li:
			count = order_books.count
			price = order_books.price
			amount = count * price
			order_books.amount = amount

		order.order_books_li = order_books_li

	context = {
        'order_li':order_li,
        'page':'order'
	}
	return render(request, 'users/user_center_order.html', context)




# 登录验证码
def veriycode(request):
	from PIL import Image,ImageDraw,ImageFont
	import random
	bgcolor = (random.randrange(20,100),random.randrange(
		20,100
	),255)
	width = 100
	height = 25
	im = Image.new('RGB',(width,height),bgcolor)
	draw = ImageDraw.Draw(im)
	for i in range(0,100):
		xy = (random.randrange(0,width),random.randrange(0,height))
		fill = (random.randrange(0,255),255,random.randrange(0,255))
		draw.point(xy,fill=fill)

	str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
	rand_str = ''
	for i in range(0,4):
		rand_str += str1[random.randrange(0,len(str1))]

	font = ImageFont.truetype('/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',15)
	fontcolor = (255,random.randrange(0,255),random.randrange(0,255))

	draw.text((5,2),rand_str[0],font=font,fill=fontcolor)
	draw.text((25,2),rand_str[1],font=font,fill=fontcolor)
	draw.text((50,2),rand_str[2],font=font,fill=fontcolor)
	draw.text((75,2),rand_str[3],font=font,fill=fontcolor)

	del draw

	request.session['verifycode'] = rand_str

	import io
	buf = io.BytesIO()
	im.save(buf,'png')

	return HttpResponse(buf.getvalue(),'image/png')

# 用户激活功能的实现
def register_active(request, token):
	'''用户账户激活'''
	serializer = Serializer(settings.SECRET_KEY, 3600)
	try:
		info = serializer.loads(token)
		passport_id = info['confirm']
		passport = Passport.objects.get(id=passport_id)
		passport.is_active = True
		passport.save()

		return redirect(reverse('user:login'))

	except SignatureExpired:
		return HttpResponse('激活链接已过期')