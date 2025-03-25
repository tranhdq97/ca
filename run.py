import time

from flask import Response
from app import create_app, db
from app.models.user import User
from app.models.menu import MenuItem
from app.models.order import Order, OrderItem
from flask_migrate import Migrate

from app.services.auth import AuthService

app = create_app()
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    """Add database models to shell context for easy testing"""
    return {
        "db": db,
        "User": User,
        "MenuItem": MenuItem,
        "Order": Order,
        "OrderItem": OrderItem,
    }


@app.cli.command("create-admin")
def create_admin():
    """Command to create an admin user"""
    import getpass

    phone = input("Enter admin phone number: ")
    password = getpass.getpass("Enter admin password: ")

    AuthService.add_user(phone=phone, is_staff=True, password=password)
    print(f"Admin user created with phone: {phone}")


if __name__ == "__main__":
    app.run(debug=True)
