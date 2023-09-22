from cart_app.cart import Cart


def cart(request):
    return {"cart": Cart(request)}
