from flask import Blueprint
from flask import request, jsonify
from app.services.auth import AuthService
from app.utils.common import CommonUtils


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["POST"])
def login():
    """Login for staff or client"""
    data = request.json or {}
    phone = data.get("phone") or ""
    password = data.get("password") or ""
    is_staff = CommonUtils.safe_bool(data.get("is_staff"))

    if not phone:
        return jsonify({"success": False, "message": "Phone number is required"}), 400
    if is_staff and not password:
        return jsonify({"success": False, "message": "Password is required"}), 400

    user = AuthService.get_user(filter_params=dict(phone=phone, is_staff=is_staff))

    # If user is not found, create a new client user
    if not user:
        if is_staff:
            return (
                jsonify({"success": False, "message": "Staff account not found"}),
                404,
            )
        new_user = AuthService.add_user(phone=phone, is_staff=False)
        return (
            jsonify(
                {
                    "success": True,
                    "user": {
                        "id": new_user.id,
                        "phone": new_user.phone,
                        "is_staff": new_user.is_staff,
                    },
                }
            ),
            201,
        )

    # If user is found, check if it is a valid staff user
    if user.is_staff:
        if not password or not user.check_password(password):
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        # Generate JWT token for staff user
        token = AuthService.generate_jwt_token(user)
        return (
            jsonify(
                {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "phone": user.phone,
                        "is_staff": user.is_staff,
                    },
                    "token": token,
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "success": True,
                "user": {"id": user.id, "phone": user.phone, "is_staff": user.is_staff},
            }
        ),
        200,
    )
