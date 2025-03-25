from app import db
from datetime import datetime


class OrderStatus:
    ESTABLISHED = "Order established"
    PROCESSING = "Order processing"
    FINISHED = "Order finish"
    DELIVERED = "Order delivered"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default=OrderStatus.ESTABLISHED)
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
            "status": self.status,
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
