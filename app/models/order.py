from app import db
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    ESTABLISHED = 3
    PROCESSING = 2
    READY = 1
    DELIVERED = 4

    @classmethod
    def to_int(cls, status_name):
        return {
            "ESTABLISHED": cls.ESTABLISHED.value,
            "PROCESSING": cls.PROCESSING.value,
            "READY": cls.READY.value,
            "DELIVERED": cls.DELIVERED.value,
        }.get(status_name, None)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    status = db.Column(
        db.Integer, default=OrderStatus.ESTABLISHED.value
    )  # Store status as an integer
    total_price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship with order items
    items = db.relationship(
        "OrderItem", backref="order", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "customer_phone": self.customer_phone,
            "status": OrderStatus(self.status).name,  # Convert integer to status name
            "status_id": self.status,
            "total_price": self.total_price,
            "created_at": self.created_at.isoformat(),
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)

    # Relationship with menu item
    menu_item = db.relationship("MenuItem")

    def to_dict(self):
        return {
            "id": self.id,
            "menu_item": self.menu_item.to_dict(),
            "quantity": self.quantity,
            "price": self.price,
        }
