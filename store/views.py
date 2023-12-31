from django.shortcuts import render
from . models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder

# Create your views here.

def store(request):

	data = cookieCart(request)
	cartItems = data['cartItems']

	products = Product.objects.all()
	context = {'products' : products, 'cartItems' : cartItems} #{2} Remove cartItems
	return render(request, 'store/store.html', context)

def cart(request):

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items # {2} Added
	else:
		cookieData = cookieCart(request)
		cartItems = cookieData['cartItems']
		order = cookieData['order']
		items = cookieData['items']

	products = Product.objects.all()
	context = {'items' : items, 'order' : order, 'cartItems' : cartItems} #{2} Remove cartItems
	return render(request, 'store/cart.html', context)


def checkout(request):
	# Empty cart for Logged-out users
	data = cookieCart(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items' : items, 'order' : order, 'cartItems' : cartItems} #{2} Remove cartItems
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']

	print('Action', action)
	print('productId', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
def processOrder(request):
	transiction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)


	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transiction_id = transiction_id

	if total == order.get_cart_total:
		order.complete =True
	order.save()
	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city = data['shipping']['city'],
		state = data['shipping']['state'],
		zipcode = data['shipping']['zipcode'],
		)
	return JsonResponse('Payment complete!', safe=False)
