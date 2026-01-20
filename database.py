import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Item:
    index: int
    name: str
    cost: int
    description: str


@dataclass
class UserStats:
    total_received: int = 0
    total_spent: int = 0
    position: str = "user"  # "user", "admin", "god"


class UserData:
    def __init__(self):
        self.coins = 100
        self.items: Dict[int, Item] = {}
        self.stats = UserStats()


class Database:
    def __init__(self, json_path: str = "database.json"):
        self.users: Dict[int, UserData] = {}
        self.market_items: List[Item] = []
        self.market_index = 1  # Следующий индекс для новых товаров
        self.user_next_index: Dict[int, int] = {}
        self.admins: set = set()
        self.god: set = set()
        self.json_path = json_path

    def init_market(self):
        """Инициализация стартовых товаров с последовательной нумерацией"""
        self.market_items = []
        self.market_index = 1
        
        self.add_market_item("Меч", 50, "Острый меч")
        self.add_market_item("Щит", 30, "Защищает от атак")
        self.add_market_item("Зелье", 15, "Лечение")

    @classmethod
    def from_dict(cls, data: dict, json_path: str):
        """Полное восстановление из JSON с переиндексацией"""
        db = cls(json_path)
        
        # Восстанавливаем базовые данные
        db.market_index = max(data.get("market_index", 1), 1)
        db.user_next_index = data.get("user_next_index", {})
        db.admins = set(data.get("admins", []))
        db.god = set(data.get("god", []))
        
        # Восстанавливаем пользователей
        for user_id_str, user_info in data.get("users", {}).items():
            user_id = int(user_id_str)
            ud = UserData()
            ud.coins = user_info.get("coins", 100)
            
            # Восстанавливаем предметы пользователей (индексы инвентаря сохраняются)
            ud.items = {}
            for idx_str, item_data in user_info.get("items", {}).items():
                idx = int(idx_str)
                ud.items[idx] = Item(**item_data)
            
            ud.stats = UserStats(**user_info.get("stats", {}))
            db.users[user_id] = ud
        
        # Восстанавливаем рынок с переиндексацией (последовательные номера 1,2,3...)
        db.reindex_market_items(data.get("market_items", []))
        
        return db

    def reindex_market_items(self, items_data: List[dict]):
        """Переиндексирует предметы рынка с последовательными номерами 1,2,3..."""
        self.market_items = []
        self.market_index = 1
        
        for item_data in items_data:
            item = Item(
                self.market_index,
                item_data['name'],
                item_data['cost'],
                item_data['description']
            )
            self.market_items.append(item)
            self.market_index += 1

    def get_user(self, user_id: int) -> UserData:
        if user_id not in self.users:
            self.users[user_id] = UserData()
            self.user_next_index[user_id] = 1
        return self.users[user_id]

    def set_user_position(self, user_id: int, position: str):
        user = self.get_user(user_id)
        user.stats.position = position

    def add_market_item(self, name: str, cost: int, description: str) -> int:
        """Добавляет товар с следующим доступным индексом"""
        index = self.market_index
        item = Item(index, name, cost, description)
        self.market_items.append(item)
        self.market_index += 1
        return index

    def find_market_item(self, identifier: str) -> Optional[Item]:
        identifier = identifier.lower().strip()
        try:
            index = int(identifier)
            return next((item for item in self.market_items if item.index == index), None)
        except ValueError:
            pass
        return next((item for item in self.market_items 
                    if identifier in item.name.lower()), None)

    def buy_item(self, user_id: int, identifier: str) -> str:
        user = self.get_user(user_id)
        item = self.find_market_item(identifier)

        if not item:
            return "❌ Товар не найден на рынке!"

        if user.coins < item.cost:
            return f"❌ Недостаточно монет! Нужно: {item.cost}"

        # Удаляем товар по индексу из рынка
        self.market_items = [i for i in self.market_items if i.index != item.index]
        # НЕ переиндексируем рынок!

        # Добавляем в инвентарь с уникальным индексом пользователя
        user_index = self.user_next_index.get(user_id, 1)
        user.items[user_index] = item
        self.user_next_index[user_id] = user_index + 1
        
        user.coins -= item.cost
        user.stats.total_spent += item.cost

        return f"✅ Куплен {item.name} (#{item.index}) за {item.cost} монет!"

    def find_user_item(self, user_id: int, identifier: str) -> Optional[Item]:
        user = self.get_user(user_id)
        identifier = identifier.lower().strip()
        try:
            index = int(identifier)
            return user.items.get(index)
        except ValueError:
            pass
        return next((item for item in user.items.values() 
                    if identifier in item.name.lower()), None)

    def sell_item(self, user_id: int, identifier: str) -> str:
        user = self.get_user(user_id)
        item = self.find_user_item(user_id, identifier)

        if not item:
            return "❌ Предмет не найден в инвентаре!"

        # Удаляем предмет из инвентаря по индексу оригинального товара
        for user_index, user_item in list(user.items.items()):
            if user_item.index == item.index:
                del user.items[user_index]
                break

        sell_price = item.cost // 2
        user.coins += sell_price
        user.stats.total_spent -= sell_price  # Корректируем статистику

        # Добавляем на рынок с НОВЫМ индексом (перепродажа)
        new_index = self.add_market_item(item.name, item.cost, item.description)
        return f"✅ Продан {item.name} за {sell_price} монет! (новый на рынке: #{new_index})"

    def get_stats(self) -> Dict:
        """Расширенная статистика"""
        total_received = sum(u.stats.total_received for u in self.users.values())
        total_spent = sum(u.stats.total_spent for u in self.users.values())
        market_count = len(self.market_items)
        inventory_count = sum(len(u.items) for u in self.users.values())
        total_items = market_count + inventory_count
        
        return {
            "total_received": total_received,
            "total_spent": total_spent,
            "total_items": total_items,
            "users_count": len(self.users),
            "market_count": market_count,
            "inventory_count": inventory_count
        }

    def to_dict(self) -> dict:
        """Сериализация в словарь для сохранения в JSON"""
        return {
            "market_index": self.market_index,
            "market_items": [asdict(item) for item in self.market_items],
            "users": {
                str(user_id): {
                    "coins": user_data.coins,
                    "items": {str(idx): asdict(item) for idx, item in user_data.items.items()},
                    "stats": asdict(user_data.stats)
                }
                for user_id, user_data in self.users.items()
            },
            "user_next_index": self.user_next_index,
            "admins": list(self.admins),
            "god": list(self.god)
        }
    
# db = Database()