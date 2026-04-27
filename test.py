from app.models.menu_item import Category, MenuItem
from instance.data_db import db_session

def add_data_to_db():
    # Создаём сессию для работы с БД
    session = db_session.create_session()

    # Добавляем категории
    categories_data = [
        {"name": "Пицца"},
        {"name": "Салаты"},
        {"name": "Напитки"},
        {"name": "Десерты"}
    ]

    # Словарь для хранения созданных объектов категорий (по имени)
    categories = {}

    for cat_data in categories_data:
        # Проверяем, есть ли уже категория с таким именем (опционально)
        existing = session.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category()
            category.name = cat_data["name"]
            session.add(category)
            categories[cat_data["name"]] = category
        else:
            categories[cat_data["name"]] = existing

    # Добавляем пункты меню
    menu_items_data = [
        {"name": "Маргарита", "description": "Томатный соус, моцарелла, базилик", "price": 450.0,
         "image_url": "images/margherita.jpg", "is_available": True, "category_name": "Пицца"},
        {"name": "Пепперони", "description": "Томатный соус, моцарелла, пепперони", "price": 520.0,
         "image_url": "images/pepperoni.jpg", "is_available": True, "category_name": "Пицца"},
        {"name": "Цезарь", "description": "Курица, пармезан, соус Цезарь, гренки", "price": 380.0,
         "image_url": "images/caesar.jpg", "is_available": True, "category_name": "Салаты"},
        {"name": "Греческий", "description": "Огурцы, помидоры, фета, маслины", "price": 340.0,
         "image_url": "images/greek.jpg", "is_available": True, "category_name": "Салаты"},
        {"name": "Кола", "description": "Газированный напиток", "price": 120.0,
         "image_url": "images/cola.jpg", "is_available": True, "category_name": "Напитки"},
        {"name": "Тирамису", "description": "Кофейный десерт с маскарпоне", "price": 290.0,
         "image_url": "images/tiramisu.jpg", "is_available": True, "category_name": "Десерты"},
    ]

    for item_data in menu_items_data:
        # Находим категорию по имени
        category = categories.get(item_data["category_name"])
        if not category:
            print(f"Категория '{item_data['category_name']}' не найдена, пропускаем {item_data['name']}")
            continue

        # Проверяем, нет ли уже такого же блюда (по имени) – опционально
        existing_item = session.query(MenuItem).filter(MenuItem.name == item_data["name"]).first()
        if existing_item:
            print(f"Блюдо '{item_data['name']}' уже существует, пропускаем")
            continue

        menu_item = MenuItem()
        menu_item.name = item_data["name"]
        menu_item.description = item_data["description"]
        menu_item.price = item_data["price"]
        menu_item.image_url = item_data["image_url"]
        menu_item.is_available = item_data["is_available"]
        menu_item.category = category  # присваиваем объект категории, SQLAlchemy сам проставит category_id

        session.add(menu_item)

    # Сохраняем все изменения в БД
    session.commit()
    print("Данные успешно добавлены в базу данных.")

if __name__ == "__main__":
    add_data_to_db()