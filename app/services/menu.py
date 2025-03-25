from typing import List, Dict, Union

from MySQLdb import IntegrityError

from app.models.menu import MenuItem
from app import db


class MenuService:
    @classmethod
    def get_all_menu_items(cls) -> List[Dict[str, Union[int, str, float, None]]]:
        """
        Retrieve all menu items.

        :return: A list of dictionaries representing menu items.
        """
        menu_items = MenuItem.query.all()
        return [item.to_dict() for item in menu_items]

    @classmethod
    def search_menu_items(
        cls, name: str, category_id: int
    ) -> List[Dict[str, Union[int, str, float, None]]]:
        """
        Search menu items by name and category ID.

        :param name: The name of the menu item to search for.
        :param category_id: The category ID to filter menu items by. Must be an integer.
        :return: A list of dictionaries representing the filtered menu items.
        """
        query = MenuItem.query.filter(
            MenuItem.name.ilike(f"%{name}%"), MenuItem.category_id == category_id
        )

        menu_items = query.all()
        return [item.to_dict() for item in menu_items]

    @classmethod
    def add_menu_item(
        cls,
        name: str,
        category_id: int,
        price: float,
        quantity: int = 0,
        description: str = "",
    ) -> Dict[str, Union[bool, Dict[str, Union[int, str, float, None]]]]:
        """
        Add a new menu item.

        :param name: The name of the menu item.
        :param category_id: The category ID of the menu item.
        :param price: The price of the menu item.
        :param quantity: The quantity of the menu item (default is 0).
        :param description: The description of the menu item (default is an empty string).
        :return: A dictionary indicating success or failure, and the created menu item if successful.
        """
        try:
            # Create and save the new menu item
            new_item = MenuItem(
                name=name,
                quantity=quantity,
                category_id=category_id,
                price=price,
                description=description,
            )

            db.session.add(new_item)
            db.session.commit()

            return {"success": True, "menu_item": new_item.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e._message)}

    @classmethod
    def delete_menu_item(cls, menu_id: int) -> dict:
        """Delete a menu item"""
        menu_item = MenuItem.query.get(menu_id)
        if not menu_item:
            return {"success": False, "message": "Menu item not found"}
        db.session.delete(menu_item)
        db.session.commit()
        return {"success": True, "message": "Menu item deleted successfully"}

    @classmethod
    def add_quantity(cls, menu_id: int, quantity: int) -> dict:
        """Add quantity to a menu item"""
        menu_item = MenuItem.query.get(menu_id)
        if not menu_item:
            return {"success": False, "message": "Menu item not found"}
        menu_item.quantity += quantity
        db.session.commit()
        return {"success": True, "menu_item": menu_item.to_dict()}

    @classmethod
    def reduce_quantity(cls, menu_id: int, quantity: int) -> dict:
        """Reduce quantity of a menu item"""
        menu_item = MenuItem.query.get(menu_id)
        if not menu_item:
            return {"success": False, "message": "Menu item not found"}
        if menu_item.quantity < quantity:
            return {"success": False, "message": "Insufficient quantity"}
        menu_item.quantity -= quantity
        db.session.commit()
        return {"success": True, "menu_item": menu_item.to_dict()}

    @classmethod
    def update_description(cls, menu_id: int, description: str) -> dict:
        """Update the description of a menu item"""
        menu_item = MenuItem.query.get(menu_id)
        if not menu_item:
            return {"success": False, "message": "Menu item not found"}
        menu_item.description = description
        db.session.commit()
        return {"success": True, "menu_item": menu_item.to_dict()}
