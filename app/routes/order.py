from datetime import datetime
import json
import time
from flask import Blueprint, Response, request, jsonify
from app.models.order import Order, OrderItem, OrderStatus
from app.models.menu import MenuItem
from app import db

order = Blueprint("order", __name__)


@order.route("/", methods=["POST"])
def create_order():
    """Create a new order"""
    data = request.get_json()

    if (
        not data
        or not (menu_items := data.get("menu_items"))
        or not (phone := data.get("phone"))
    ):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Create new order
    new_order = Order(customer_phone=phone, status=OrderStatus.PROCESSING.value)

    db.session.add(new_order)
    db.session.flush()  # Get the order ID

    total_price = 0

    # Add order items
    for item_data in menu_items:
        menu_item_id = item_data.get("id")
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


@order.route("/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    """Update order status"""
    data = request.json

    if not data or not (new_status := data.get("status")):
        return jsonify({"success": False, "message": "Missing status field"}), 400

    # Check if status is valid
    valid_statuses = [
        OrderStatus.ESTABLISHED.name,
        OrderStatus.PROCESSING.name,
        OrderStatus.READY.name,
        OrderStatus.DELIVERED.name,
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
    order.status = OrderStatus.to_int(new_status)
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

    orders = query.order_by(Order.status).all()

    return (
        jsonify({"success": True, "orders": [order.to_dict() for order in orders]}),
        200,
    )


@order.route("/byphone", methods=["GET"])
def get_orders_by_phone():
    """Get all orders for a specific phone number"""
    phone = request.args.get("phone") or ""
    if phone:
        orders = (
            Order.query.filter(Order.customer_phone == phone)
            .order_by(Order.status)
            .all()
        )
    else:
        orders = []

    return (
        jsonify({"success": True, "orders": [order.to_dict() for order in orders]}),
        200,
    )


@order.route("/<int:order_id>/check", methods=["PUT"])
def check_my_order(order_id):
    """Check if the order exists"""
    data = request.json
    phone = data.get("phone")
    if not phone:
        return jsonify({"success": False, "message": "Missing phone field"}), 400
    order = Order.query.filter(
        Order.id == order_id,
        (Order.customer_phone == "" or Order.customer_phone.is_(None)),
    ).first()
    if not order:
        return (
            jsonify(
                {"success": False, "message": f"Order with id {order_id} not found"}
            ),
            404,
        )
    order.customer_phone = phone
    order.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"success": True, "order": order.to_dict()}), 200


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
