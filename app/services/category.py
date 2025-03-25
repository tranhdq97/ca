from typing import List, Optional
from app.models.category import Category
from app import db


class CategoryService:
    @classmethod
    def add_category(cls, name: str) -> Category:
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return category

    @classmethod
    def get_all_categories(cls) -> List[Category]:
        return Category.query.all()

    @classmethod
    def get_category_by_id(cls, category_id: str) -> Optional[Category]:
        return Category.query.filter_by(id=category_id).first()
