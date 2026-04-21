from .models import Cart

def cart_count(request):
    if not request.session.session_key:
        request.session.create()
    count = Cart.objects.filter(session_key=request.session.session_key).count()
    return {'cart_count': count}