from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import Carousel, New_Arrivals, Best_Sellers, Cart, Order, Fiction, Non_Fiction, Nepali
from django.views.decorators.csrf import csrf_exempt
import uuid
import hmac
import hashlib
import base64
import json


# ─── Auth Views ───────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if not request.POST.get('remember'):
                request.session.set_expiry(0)

            next_url = request.GET.get('next') or request.POST.get('next')
            return redirect(next_url if next_url else 'index')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Welcome, {user.username}! Your account was created.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# ─── Core Views ───────────────────────────────────────────────

def index(request):
    if not request.session.session_key:
        request.session.create()

    new_arrivals = New_Arrivals.objects.all()
    best_sellers = Best_Sellers.objects.all()
    carousels = Carousel.objects.all()

    context = {
        'carousels': carousels,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        messages.success(request, f"Thanks {name}! We'll get back to you soon.")
        return redirect('contact')
    return render(request, 'core/contact.html')


# ─── Category Views ───────────────────────────────────────────

def fiction_books(request):
    books = Fiction.objects.all()
    return render(request, 'core/books.html', {
        'books': books,
        'category': 'Fiction',
        'product_type': 'fiction',
    })


def non_fiction_books(request):
    books = Non_Fiction.objects.all()
    return render(request, 'core/books.html', {
        'books': books,
        'category': 'Non-Fiction',
        'product_type': 'non_fiction',
    })


def nepali_books(request):
    books = Nepali.objects.all()
    return render(request, 'core/books.html', {
        'books': books,
        'category': 'Nepali Literature',
        'product_type': 'nepali',
    })


# ─── Product Detail ───────────────────────────────────────────

def product_detail(request, product_type, pk):
    if product_type == 'new_arrival':
        product = get_object_or_404(New_Arrivals, pk=pk)
    elif product_type == 'best_seller':
        product = get_object_or_404(Best_Sellers, pk=pk)
    elif product_type == 'fiction':
        product = get_object_or_404(Fiction, pk=pk)
    elif product_type == 'non_fiction':
        product = get_object_or_404(Non_Fiction, pk=pk)
    elif product_type == 'nepali':
        product = get_object_or_404(Nepali, pk=pk)
    else:
        product = get_object_or_404(Carousel, pk=pk)

    return render(request, 'core/product_detail.html', {
        'product': product,
        'product_type': product_type,
    })


# ─── Cart Views ───────────────────────────────────────────────

@csrf_exempt
def add_to_cart(request, product_type, pk):
    if request.method == 'POST':
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        if product_type == 'new_arrival':
            product = get_object_or_404(New_Arrivals, pk=pk)
            price = product.marked_price
        elif product_type == 'best_seller':
            product = get_object_or_404(Best_Sellers, pk=pk)
            price = product.marked_price
        elif product_type == 'fiction':
            product = get_object_or_404(Fiction, pk=pk)
            price = product.marked_price
        elif product_type == 'non_fiction':
            product = get_object_or_404(Non_Fiction, pk=pk)
            price = product.marked_price
        elif product_type == 'nepali':
            product = get_object_or_404(Nepali, pk=pk)
            price = product.marked_price
        else:
            product = get_object_or_404(Carousel, pk=pk)
            price = int(product.price)

        cart_item, created = Cart.objects.get_or_create(
            session_key=session_key,
            product_id=pk,
            product_type=product_type,
            defaults={
                'title': product.title,
                'image': product.image.url,
                'price': price,
                'quantity': 1,
            }
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        cart_count = Cart.objects.filter(session_key=session_key).count()
        return JsonResponse({'success': True, 'cart_count': cart_count})

    return JsonResponse({'success': False}, status=400)


def cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart_items = Cart.objects.filter(session_key=session_key)
    total = sum(item.price * item.quantity for item in cart_items)
    return render(request, 'core/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


@csrf_exempt
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=item_id)
        cart_item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


# ─── Payment Views ────────────────────────────────────────────

def initiate_esewa(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to complete your purchase.')
            return redirect('login')  # ✅ Added missing return redirect

        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        cart_items = Cart.objects.filter(session_key=session_key)
        if not cart_items.exists():
            return redirect('cart')

        total = sum(item.price * item.quantity for item in cart_items)
        total_str = "{:.2f}".format(float(total))
        transaction_uuid = str(uuid.uuid4())

        # ✅ Moved inside try/except and use get_or_create to avoid duplicate orders
        order, created = Order.objects.get_or_create(
            session_key=session_key,
            status='pending',
            defaults={
                'total_amount': total,
                'transaction_id': transaction_uuid,
            }
        )

        merchant_code = "EPAYTEST"
        secret_key = "8gBm/:&EnhH.1/q"
        message = f"total_amount={total_str},transaction_uuid={order.transaction_id},product_code={merchant_code}"

        # ✅ Fixed: hmac.new() → hmac.new() is correct but ensure import is `import hmac`
        signature = base64.b64encode(
            hmac.new(
                secret_key.encode(),
                msg=message.encode(),
                digestmod=hashlib.sha256
            ).digest()
        ).decode()

        context = {
            'amount': total_str,
            'total_amount': total_str,
            'transaction_uuid': order.transaction_id,  # ✅ Use order's UUID, not a new one
            'product_code': merchant_code,
            'signature': signature,
            'success_url': request.build_absolute_uri('/esewa/success/'),
            'failure_url': request.build_absolute_uri('/esewa/failure/'),
        }
        return render(request, 'core/esewa_payment.html', context)

    return redirect('cart')


@csrf_exempt
def esewa_success(request):
    data = request.GET.get('data') or request.POST.get('data')
    if not data:
        messages.error(request, 'Payment verification failed.')
        return redirect('cart')

    try:
        decoded = base64.b64decode(data).decode('utf-8')
        payment_data = json.loads(decoded)

        transaction_uuid = payment_data.get('transaction_uuid')
        status = payment_data.get('status')

        if status == 'COMPLETE':
            order = Order.objects.get(transaction_id=transaction_uuid)
            order.status = 'completed'
            order.save()

            Cart.objects.filter(session_key=order.session_key).delete()

            messages.success(request, 'Payment successful! Your order has been placed.')
            return render(request, 'core/esewa_success.html', {'order': order})
        else:
            messages.error(request, 'Payment was not completed.')
            return redirect('cart')

    except Exception as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('cart')


def esewa_failure(request):
    return render(request, 'core/esewa_failure.html')


# ─── Orders ───────────────────────────────────────────────────

def orders(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    all_orders = Order.objects.filter(session_key=session_key).order_by('-id')
    completed_count = all_orders.filter(status='completed').count()
    pending_count = all_orders.filter(status='pending').count()
    total_spent = sum(o.total_amount for o in all_orders.filter(status='completed'))

    return render(request, 'core/orders.html', {
        'orders': all_orders,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'total_spent': total_spent,
    })