from django.conf import settings

from shop_app.models import Product, Sale


class Cart(object):
    """Объект корзины в сессии"""

    def __init__(self, request):
        """Инициализация корзины."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        """Перебор элементов в корзине и получение продуктов из базы данных."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            product_id = str(product.id)
            sales = Sale.objects.filter(product=product.id)
            if sales:
                sale = sales.get(product=product.id)
                last_price = sale.salePrice
            else:
                last_price = product.price

            cart[product_id]["product_id"] = product_id
            cart[product_id]["price"] = float(last_price)
            cart[product_id]["total_price"] = (
                cart[product_id]["price"] * cart[product_id]["quantity"]
            )

        sorted_cart = sorted(cart.values(), key=lambda item: item["product_id"])

        for item in sorted_cart:
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        """Добавление товара в корзину или обновление количества товара."""
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": float(product.price)}

        available_quantity = product.count
        if quantity <= available_quantity:
            if override_quantity:
                self.cart[product_id]["quantity"] = quantity
            else:
                self.cart[product_id]["quantity"] += quantity
            self.save()
            available_quantity -= quantity
        else:
            print("недостаточное количество товара")
            return self.cart

    def remove(self, product, quantity=1):
        """Удаление товара из корзины."""
        product_id = str(product.id)
        if product_id in self.cart:
            if quantity >= self.cart[product_id]["quantity"]:
                del self.cart[product_id]
            else:
                self.cart[product_id]["quantity"] -= quantity
            self.save()

    def get_total_price(self):
        """Подсчет стоимости товаров в корзине."""
        return sum(
            float(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def clear(self):
        """Удаление корзины из сессии."""
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def save(self):
        """Сохранение корзины."""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
