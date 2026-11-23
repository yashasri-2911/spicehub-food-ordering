from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# =========================================================
# DATA CLASSES
# =========================================================

class MenuItem:
    def __init__(self, item_id, name, price, category):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.category = category


class OrderItem:
    def __init__(self, menu_item, quantity):
        self.menu_item = menu_item
        self.quantity = quantity

    def subtotal(self):
        return self.menu_item.price * self.quantity


class Order:
    def __init__(self, order_id, customer, phone, address, payment):
        self.order_id = order_id
        self.customer = customer
        self.phone = phone
        self.address = address
        self.payment = payment
        self.items = []
        self.status = "Accepted"
        self.payment_status = "Pending"
        self.delivery_person = "Not Assigned"

    def add_item(self, item):
        self.items.append(item)

    def total(self):
        return sum(item.subtotal() for item in self.items)


class Restaurant:
    def __init__(self, name):
        self.name = name
        self.menu = []

    def add_menu_item(self, item):
        self.menu.append(item)


class Payment:
    def __init__(self, method):
        self.method = method

    def process_payment(self):
        if self.method == "UPI":
            return "Paid (Demo)"
        return "Pay on Delivery"


# =========================================================
# RESTAURANT
# =========================================================

restaurant = Restaurant("Spice Hub")

restaurant.add_menu_item(
    MenuItem(1, "Chicken Biryani", 180, "Main Course")
)

restaurant.add_menu_item(
    MenuItem(2, "Chicken 65", 120, "Starter")
)

restaurant.add_menu_item(
    MenuItem(3, "Chicken Fried Rice", 150, "Main Course")
)

restaurant.add_menu_item(
    MenuItem(4, "Paneer Butter Masala", 160, "Main Course")
)

restaurant.add_menu_item(
    MenuItem(5, "Veg Fried Rice", 130, "Main Course")
)

orders = {}
next_order_id = 501


# =========================================================
# WEBSITE
# =========================================================

HTML = """
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Spice Hub | Food Ordering</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f6f1eb;
    color: #29221f;
}

header {
    background: linear-gradient(135deg, #3a2118, #8b452c);
    color: white;
    padding: 45px 20px;
    text-align: center;
}

header h1 {
    margin: 0;
    font-size: 45px;
}

header p {
    margin-top: 10px;
    font-size: 18px;
}

.container {
    max-width: 1000px;
    margin: 30px auto;
    padding: 0 18px;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 25px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
}

h2 {
    color: #8b452c;
    margin-top: 0;
}

.food {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding: 18px 0;
    border-bottom: 1px solid #eee;
}

.food:last-child {
    border-bottom: none;
}

.food-info {
    flex: 1;
}

.food h3 {
    margin: 0 0 6px;
    font-size: 20px;
}

.category {
    color: #777;
    font-size: 14px;
    margin-bottom: 8px;
}

.price {
    font-size: 18px;
    font-weight: bold;
    color: #8b452c;
}

.quantity {
    width: 80px !important;
    margin: 0 !important;
    text-align: center;
}

label {
    display: block;
    font-weight: bold;
    margin-top: 12px;
}

input,
select {
    width: 100%;
    padding: 13px;
    margin-top: 7px;
    margin-bottom: 12px;
    border: 1px solid #d6d0ca;
    border-radius: 8px;
    font-size: 15px;
}

button {
    background: #8b452c;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 13px 22px;
    font-size: 15px;
    cursor: pointer;
}

button:hover {
    background: #642f20;
}

.place-order {
    width: 100%;
    margin-top: 15px;
    font-size: 17px;
}

.cancel {
    background: #b33a3a;
}

.cancel:hover {
    background: #8d2929;
}

.update {
    background: #4b6f8a;
}

.update:hover {
    background: #34546c;
}

.message {
    background: #e6f6e6;
    border-left: 5px solid #4d8b4d;
    padding: 15px;
    border-radius: 8px;
}

.order {
    border: 1px solid #e4ddd7;
    border-radius: 12px;
    padding: 20px;
    margin-top: 18px;
}

.order-id {
    color: #8b452c;
}

.status {
    background: #f3e7dc;
    padding: 12px;
    border-radius: 8px;
    font-weight: bold;
}

.total {
    font-size: 22px;
    font-weight: bold;
    color: #8b452c;
}

.empty {
    text-align: center;
    color: #777;
}

.footer {
    text-align: center;
    color: #777;
    padding: 25px;
}

@media (max-width: 600px) {

    header h1 {
        font-size: 32px;
    }

    .food {
        align-items: flex-start;
    }

    .quantity {
        width: 65px !important;
    }

}

</style>

</head>

<body>

<header>

    <h1>🍴 Spice Hub</h1>

    <p>Online Food Ordering & Delivery System</p>

</header>


<div class="container">


<!-- MENU -->

<div class="card">

<h2>🍽️ Our Menu</h2>

<form action="/place_order" method="POST">


{% for item in menu %}

<div class="food">

    <div class="food-info">

        <h3>{{ item.name }}</h3>

        <div class="category">
            {{ item.category }}
        </div>

        <div class="price">
            ₹{{ item.price }}
        </div>

    </div>

    <input
        class="quantity"
        type="number"
        name="qty_{{ item.item_id }}"
        min="0"
        max="20"
        value="0"
    >

</div>

{% endfor %}


<h2 style="margin-top:30px;">👤 Customer Details</h2>


<label>Full Name</label>

<input
    type="text"
    name="customer"
    placeholder="Enter your full name"
    required
>


<label>Phone Number</label>

<input
    type="tel"
    name="phone"
    placeholder="Enter 10-digit phone number"
    pattern="[0-9]{10}"
    maxlength="10"
    required
>


<label>Delivery Address</label>

<input
    type="text"
    name="address"
    placeholder="Enter your delivery address"
    required
>


<label>Payment Method</label>

<select name="payment">

    <option value="UPI">
        UPI - Demo Payment
    </option>

    <option value="Cash on Delivery">
        Cash on Delivery
    </option>

</select>


<button class="place-order" type="submit">

    🛒 Place My Order

</button>

</form>

</div>


<!-- MESSAGE -->

{% if message %}

<div class="card">

    <div class="message">

        <h3>{{ message }}</h3>

    </div>

</div>

{% endif %}


<!-- ORDERS -->

<div class="card">

<h2>📦 Order History & Tracking</h2>


{% if orders %}

    {% for order in orders %}

    <div class="order">

        <h3 class="order-id">
            Order #{{ order.order_id }}
        </h3>


        <p>
            <b>Customer:</b>
            {{ order.customer }}
        </p>


        <p>
            <b>Phone:</b>
            {{ order.phone }}
        </p>


        <p>
            <b>Delivery Address:</b>
            {{ order.address }}
        </p>


        <h4>Ordered Items</h4>

        {% for item in order.items %}

        <p>
            {{ item.menu_item.name }}
            × {{ item.quantity }}
            — ₹{{ item.subtotal() }}
        </p>

        {% endfor %}


        <p class="total">
            Total: ₹{{ order.total() }}
        </p>


        <p>
            <b>Payment:</b>
            {{ order.payment }}
        </p>


        <p>
            <b>Payment Status:</b>
            {{ order.payment_status }}
        </p>


        <div class="status">

            Order Status:
            {{ order.status }}

        </div>


        <p>

            <b>Delivery Partner:</b>
            {{ order.delivery_person }}

        </p>


        {% if order.status not in
        ["Delivered", "Cancelled", "Rejected"] %}


        <form
            action="/cancel/{{ order.order_id }}"
            method="POST">

            <button
                class="cancel"
                type="submit">

                Cancel Order

            </button>

        </form>


        <form
            action="/update/{{ order.order_id }}"
            method="POST"
            style="margin-top:15px;">

            <label>
                Update Order Status
            </label>

            <select name="status">

                <option value="Accepted">
                    Accepted
                </option>

                <option value="Preparing">
                    Preparing
                </option>

                <option value="Ready">
                    Ready
                </option>

                <option value="Picked Up">
                    Picked Up
                </option>

                <option value="Delivered">
                    Delivered
                </option>

                <option value="Rejected">
                    Rejected
                </option>

            </select>

            <button
                class="update"
                type="submit">

                Update Status

            </button>

        </form>

        {% endif %}

    </div>

    {% endfor %}

{% else %}

    <p class="empty">
        No orders yet.
    </p>

{% endif %}

</div>


</div>


<div class="footer">

    © 2026 Spice Hub | Food Ordering System

</div>


</body>

</html>
"""


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template_string(
        HTML,
        menu=restaurant.menu,
        orders=list(orders.values()),
        message=request.args.get("message")
    )


# =========================================================
# PLACE ORDER
# =========================================================

@app.route("/place_order", methods=["POST"])
def place_order():

    global next_order_id

    customer = request.form.get(
        "customer", ""
    ).strip()

    phone = request.form.get(
        "phone", ""
    ).strip()

    address = request.form.get(
        "address", ""
    ).strip()

    payment_method = request.form.get(
        "payment", "UPI"
    )


    if not customer:
        return redirect(
            url_for(
                "home",
                message="Please enter your name."
            )
        )


    if not phone.isdigit() or len(phone) != 10:
        return redirect(
            url_for(
                "home",
                message="Please enter a valid 10-digit phone number."
            )
        )


    if not address:
        return redirect(
            url_for(
                "home",
                message="Please enter your delivery address."
            )
        )


    if payment_method not in [
        "UPI",
        "Cash on Delivery"
    ]:

        return redirect(
            url_for(
                "home",
                message="Invalid payment method."
            )
        )


    order = Order(
        next_order_id,
        customer,
        phone,
        address,
        payment_method
    )


    for item in restaurant.menu:

        quantity_text = request.form.get(
            f"qty_{item.item_id}",
            "0"
        )


        try:
            quantity = int(quantity_text)

        except ValueError:

            return redirect(
                url_for(
                    "home",
                    message="Invalid quantity."
                )
            )


        if quantity < 0 or quantity > 20:

            return redirect(
                url_for(
                    "home",
                    message="Quantity must be between 0 and 20."
                )
            )


        if quantity > 0:

            order.add_item(
                OrderItem(item, quantity)
            )


    if not order.items:

        return redirect(
            url_for(
                "home",
                message="Please select at least one food item."
            )
        )


    payment = Payment(payment_method)

    order.payment_status = payment.process_payment()

    order.delivery_person = "Rahul"

    orders[next_order_id] = order

    next_order_id += 1


    return redirect(
        url_for(
            "home",
            message=f"Order placed successfully! Your Order ID is #{order.order_id}"
        )
    )


# =========================================================
# UPDATE ORDER
# =========================================================

@app.route(
    "/update/<int:order_id>",
    methods=["POST"]
)
def update_order(order_id):

    order = orders.get(order_id)

    if order is None:

        return redirect(
            url_for(
                "home",
                message="Order not found."
            )
        )


    new_status = request.form.get(
        "status",
        ""
    )


    valid_statuses = [
        "Accepted",
        "Preparing",
        "Ready",
        "Picked Up",
        "Delivered",
        "Rejected"
    ]


    if new_status not in valid_statuses:

        return redirect(
            url_for(
                "home",
                message="Invalid order status."
            )
        )


    if order.status in [
        "Delivered",
        "Cancelled",
        "Rejected"
    ]:

        return redirect(
            url_for(
                "home",
                message="This order is already closed."
            )
        )


    order.status = new_status


    if new_status == "Accepted":

        order.delivery_person = "Rahul"


    if new_status == "Delivered":

        if order.payment == "Cash on Delivery":

            order.payment_status = "Paid"


    return redirect(
        url_for(
            "home",
            message=f"Order #{order_id} status updated to {new_status}."
        )
    )


# =========================================================
# CANCEL ORDER
# =========================================================

@app.route(
    "/cancel/<int:order_id>",
    methods=["POST"]
)
def cancel_order(order_id):

    order = orders.get(order_id)


    if order is None:

        return redirect(
            url_for(
                "home",
                message="Order not found."
            )
        )


    if order.status in [
        "Delivered",
        "Cancelled",
        "Rejected"
    ]:

        return redirect(
            url_for(
                "home",
                message="This order cannot be cancelled."
            )
        )


    order.status = "Cancelled"


    return redirect(
        url_for(
            "home",
            message=f"Order #{order_id} has been cancelled."
        )
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
