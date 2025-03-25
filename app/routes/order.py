from flask import Blueprint, request, jsonify
from app.models.order import Order, OrderItem, OrderStatus
from app.models.menu import MenuItem
from app import db

order = Blueprint("order", __name__)


@order.route("/", methods=["POST"])
def create_order():
    """Create a new order"""
    data = request.get_json()

    if not data or not data.get("customer_phone") or not data.get("items"):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Create new order
    new_order = Order(
        customer_phone=data["customer_phone"], status=OrderStatus.ESTABLISHED
    )

    db.session.add(new_order)
    db.session.flush()  # Get the order ID

    total_price = 0

    # Add order items
    for item_data in data["items"]:
        menu_item_id = item_data.get("menu_item_id")
        quantity = item_data.get("quantity", 1)

        # Verify the menu item exists
        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            db.session.rollback()
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Menu item with id {menu_item_id} not found",
                    }
                ),
                404,
            )

        # Check if quantity is available
        if menu_item.quantity < quantity:
            db.session.rollback()
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Not enough quantity available for {menu_item.name}",
                    }
                ),
                400,
            )

        # Create order item
        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=menu_item_id,
            quantity=quantity,
            price=menu_item.price * quantity,
        )

        # Update total price
        total_price += order_item.price

        # Update menu item quantity
        menu_item.quantity -= quantity

        db.session.add(order_item)

    # Update order total price
    new_order.total_price = total_price

    db.session.commit()

    return jsonify({"success": True, "order": new_order.to_dict()}), 201


@order.route("/<int:order_id>", methods=["PUT"])
def update_order_status(order_id):
    """Update order status"""
    data = request.get_json()

    if not data or not data.get("status"):
        return jsonify({"success": False, "message": "Missing status field"}), 400

    # Check if status is valid
    new_status = data["status"]
    valid_statuses = [
        OrderStatus.ESTABLISHED,
        OrderStatus.PROCESSING,
        OrderStatus.FINISHED,
        OrderStatus.DELIVERED,
    ]

    if new_status not in valid_statuses:
        return jsonify({"success": False, "message": "Invalid status value"}), 400

    # Find the order
    order = Order.query.get(order_id)
    if not order:
        return (
            jsonify(
                {"success": False, "message": f"Order with id {order_id} not found"}
            ),
            404,
        )

    # Update the status
    order.status = new_status
    db.session.commit()

    return jsonify({"success": True, "order": order.to_dict()}), 200


@order.route("/", methods=["GET"])
def get_orders():
    """Get all orders with optional filtering by status"""
    status = request.args.get("status")
    phone = request.args.get("phone")

    query = Order.query

    if status:
        query = query.filter(Order.status == status)

    if phone:
        query = query.filter(Order.customer_phone == phone)

    orders = query.all()

    return (
        jsonify({"success": True, "orders": [order.to_dict() for order in orders]}),
        200,
    )


@order.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """Get a specific order by ID"""
    order = Order.query.get(order_id)

    if not order:
        return (
            jsonify(
                {"success": False, "message": f"Order with id {order_id} not found"}
            ),
            404,
        )

    return jsonify({"success": True, "order": order.to_dict()}), 200
