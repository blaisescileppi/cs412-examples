# restaurant/views.py
# view functions to handle URL requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
import random
from decimal import Decimal
from datetime import datetime, timedelta
import random


BREADS = [
   "Strawberry Dark Chocolate Sourdough",
   "Jalepeno Cheddar Sourdough",
   "Garlic Rosemary Focaccia",
   "Fougasse",
   "Pain de Mie",
   "German Rye",
]

SPREADS = [
   "Tzatziki",
   "Olive Tempanade",
   "Bruchetta",
   "Sundried Tomato Olive Oil Spread",
]

BAKED_GOODS = [
   "Blueberry Chocolate Muffin",
   "Mixed Berry Crumble",
   "Maple Walnut Scone",
   "Plain Croissant",
   "Salted Sourdough Pretzle Bites",
]

DRINKS = [
   "Cappuchino",
   "Macchiato",
   "Americano",
   "Latte",
   "Drip Coffee",
   "Red-Eye",
]

SPECIALS = [
    "French Onion Guyere Bread Rolls",
    "Pull-Apart Sourdough Cinnamon Roll Bites",
    "Caramelized Pecan Cinnamon Rolls",
]

PRICES = {
    # breads
    "Strawberry Dark Chocolate Sourdough": Decimal("9.00"),
    "Jalepeno Cheddar Sourdough": Decimal("8.00"),
    "Garlic Rosemary Focaccia": Decimal("7.00"),
    "Fougasse": Decimal("7.50"),
    "Pain de Mie": Decimal("6.50"),
    "German Rye": Decimal("7.00"),

    # spreads
    "Tzatziki": Decimal("2.50"),
    "Olive Tempanade": Decimal("3.00"),
    "Bruchetta": Decimal("2.75"),
    "Sundried Tomato Olive Oil Spread": Decimal("3.25"),

    # baked goods
    "Blueberry Chocolate Muffin": Decimal("3.75"),
    "Mixed Berry Crumble": Decimal("5.50"),
    "Maple Walnut Scone": Decimal("3.50"),
    "Plain Croissant": Decimal("3.25"),
    "Salted Sourdough Pretzle Bites": Decimal("4.00"),

    # drinks
    "Cappuchino": Decimal("4.50"),
    "Macchiato": Decimal("4.25"),
    "Americano": Decimal("3.50"),
    "Latte": Decimal("4.75"),
    "Drip Coffee": Decimal("2.75"),
    "Red-Eye": Decimal("4.00"),

    # specials
    "French Onion Guyere Bread Rolls": Decimal("6.00"),
    "Pull-Apart Sourdough Cinnamon Roll Bites": Decimal("4.50"),
    "Caramelized Pecan Cinnamon Rolls": Decimal("4.00"),
}

IMAGES = [
    "https://images.stockcake.com/public/b/3/6/b365fd39-1896-4b64-a952-87e22bd4578c_large/bakery-window-display-stockcake.jpg",
    "https://thumbs.dreamstime.com/b/elegant-parisian-patisserie-luxurious-interior-fresh-pastries-charming-chandelier-freshly-baked-shop-entrance-367350138.jpg",
]

# Create your views here.
def main(request):
   '''Display the main page'''
   
   template_name = "restaurant/main.html"
   context = {
    "image": random.choice(IMAGES),
    }
   return render(request, template_name=template_name, context=context)

def orders(request):
    """Show the order form page (GET). Random special changes every refresh."""
    template_name = "restaurant/order.html"

    daily_special = random.choice(SPECIALS)
    name = request.POST.get("name", "").strip()

    context = {
    "breads": [(item, PRICES[item]) for item in BREADS],
    "spreads": [(item, PRICES[item]) for item in SPREADS],
    "baked_goods": [(item, PRICES[item]) for item in BAKED_GOODS],
    "drinks": [(item, PRICES[item]) for item in DRINKS],
    "daily_special": (daily_special, PRICES[daily_special]),
    "name": name,
    }
    return render(request, template_name=template_name, context=context)


def confirmation(request):
    """Process the submitted form (POST) and render confirmation page."""
    print(request.POST)

    template_name = "restaurant/confirmation.html"

    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        selected_items = []
        selected_items += request.POST.getlist("breads")
        selected_items += request.POST.getlist("spreads")
        selected_items += request.POST.getlist("baked_goods")
        selected_items += request.POST.getlist("drinks")

        got_special = request.POST.get("special")  # single checkbox
        if got_special:
            selected_items.append(got_special)

        total = sum((PRICES.get(item, Decimal("0.00")) for item in selected_items), Decimal("0.00"))
        
        # generate random ready time between 30–60 min
        minutes = random.randint(30, 60)
        now = datetime.now()
        ready_time = now + timedelta(minutes=minutes)
        
        # format nicely (ex: 3:45 PM)
        ready_time_str = ready_time.strftime("%I:%M %p")
  
        selected_with_prices = [(item, PRICES[item]) for item in selected_items]
        
        context = {
            "name": name,
            "selected_items": selected_items,
            "total": total,
            "s" : selected_with_prices,
            "ready_time": ready_time_str,
            }

        return render(request, template_name, context)

    # If someone visits /confirmation/ with GET, just show empty confirmation or redirect.
    return render(request, template_name, {"name": "", "selected_items": [], "total": Decimal("0.00"), "prices": PRICES})
