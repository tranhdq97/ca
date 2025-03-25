from flask import Blueprint, request, jsonify
from app.services.menu import MenuService
from app.utils.auth import token_required
from app.utils.common import CommonUtils

menu = Blueprint("menu", __name__)


@menu.route("/", methods=["GET"])
def get_menu():
    """Get all menu items"""
    menu_items = MenuService.get_all_menu_items()
    return jsonify({"success": True, "menu_items": menu_items}), 200


@menu.route("/search", methods=["GET"])
def search_menu():
    """Search menu items by name or category"""
    params = request.args.to_dict()
    name = params.get("name", "").strip()
    category_id = CommonUtils.safe_int(params.get("category_id", ""))

    if not (name and category_id):
        return (
            jsonify({"success": False, "message": "Provide category_id and name"}),
            400,
        )

    menu_items = MenuService.search_menu_items(name=name, category_id=category_id)
    return jsonify({"success": True, "menu_items": menu_items}), 200


@menu.route("/", methods=["POST"])
@token_required
def add_menu_item():
    """Add a new menu item"""
    data = request.json

    # Validate input data
    required_fields = ["name", "category_id", "price"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Missing fields: {', '.join(missing_fields)}",
                }
            ),
            400,
        )

    name = data.get("name") or ""
    category_id = CommonUtils.safe_int(data.get("category_id"))
    price = CommonUtils.safe_int(data.get("price"))
    description = data.get("description") or ""

    result = MenuService.add_menu_item(
        name=name,
        category_id=category_id,
        price=price,
        description=description,
    )
    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result), 201


@menu.route("/<int:menu_id>", methods=["DELETE"])
@token_required
def delete_menu_item(menu_id):
    """Delete a menu item"""
    result = MenuService.delete_menu_item(menu_id)
    if not result["success"]:
        return jsonify(result), 404
    return jsonify(result), 200


@menu.route("/<int:menu_id>/add-quantity", methods=["PUT"])
@token_required
def add_quantity(menu_id):
    """Add more quantity to a menu item"""
    data = request.json
    quantity = CommonUtils.safe_int(data.get("quantity"))

    if quantity is None or quantity <= 0:
        return jsonify({"success": False, "message": "Invalid quantity"}), 400

    result = MenuService.add_quantity(menu_id, quantity)
    if not result["success"]:
        return jsonify(result), 404
    return jsonify(result), 200


@menu.route("/<int:menu_id>/reduce-quantity", methods=["PUT"])
@token_required
def reduce_quantity(menu_id):
    """Reduce quantity of a menu item"""
    data = request.json
    quantity = CommonUtils.safe_int(data.get("quantity"))

    if quantity is None or quantity <= 0:
        return jsonify({"success": False, "message": "Invalid quantity"}), 400

    result = MenuService.reduce_quantity(menu_id, quantity)
    if not result["success"]:
        return jsonify(result), 400
    return jsonify(result), 200


@menu.route("/<int:menu_id>/update-description", methods=["PUT"])
@token_required
def update_description(menu_id):
    """Update the description of a menu item"""
    data = request.json
    description = data.get("description") or ""

    if not description:
        return (
            jsonify({"success": False, "message": "Description cannot be empty"}),
            400,
        )

    result = MenuService.update_description(menu_id, description)
    if not result["success"]:
        return jsonify(result), 404
    return jsonify(result), 200
