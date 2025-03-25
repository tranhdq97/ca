from app import db
from datetime import datetime
from sqlalchemy import UniqueConstraint


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    category = db.relationship("Category", backref="menu_items")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Add a unique constraint on the combination of name and category_id
    __table_args__ = (UniqueConstraint("name", "category_id", name="uq_name_category"),)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "description": self.description,
            "category_id": self.category_id,
            "category_name": self.category.name,
        }
