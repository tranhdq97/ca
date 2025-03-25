from flask import Blueprint, request, jsonify
from app import db
from app.utils.auth import token_required
from app.services.category import CategoryService
from sqlalchemy.exc import IntegrityError

category = Blueprint("category", __name__)


@category.route("/", methods=["GET"])
def get_categories():
    """Get all categories"""
    categories = CategoryService.get_all_categories()
    return (
        jsonify(
            {
                "success": True,
                "categories": [{"id": c.id, "name": c.name} for c in categories],
            }
        ),
        200,
    )


@category.route("/", methods=["POST"])
@token_required
def add_category():
    """Add a new category"""
    data = request.json
    name = data.get("name") if data else None

    if not name:
        return jsonify({"success": False, "message": "Category name is required"}), 400

    try:
        category = CategoryService.add_category(name=name)
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "message": "Category already exists"}), 400

    return (
        jsonify(
            {
                "success": True,
                "category": {"id": category.id, "name": category.name},
            }
        ),
        201,
    )


@category.route("/<int:category_id>", methods=["PUT"])
@token_required
def update_category(category_id):
    """Update an existing category"""
    data = request.json
    name = data.get("name") if data else None

    if not name:
        return jsonify({"success": False, "message": "Category name is required"}), 400

    category = CategoryService.get_category_by_id(category_id)
    if not category:
        return jsonify({"success": False, "message": "Category not found"}), 404

    if category.name == name:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "New name is the same as the current name",
                }
            ),
            400,
        )

    if CategoryService.is_name_taken(name, exclude_id=category_id):
        return (
            jsonify({"success": False, "message": "Category name already exists"}),
            400,
        )

    category.name = name
    db.session.commit()

    return (
        jsonify(
            {
                "success": True,
                "category": {"id": category.id, "name": category.name},
            }
        ),
        200,
    )


@category.route("/<int:category_id>", methods=["DELETE"])
@token_required
def delete_category(category_id):
    """Delete a category"""
    category = CategoryService.get_category_by_id(category_id)
    if not category:
        return jsonify({"success": False, "message": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({"success": True, "message": "Category deleted successfully"}), 200
