from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass(frozen=True)
class Item:
    index: int
    name: str
    cost: int
    description: str

class UserData:
    def __init__(self):
        self.coins = 100
        self.items = {}  # {user_index: Item}

class Database:
    def __init__(self):
        self.users: Dict[int, UserData] = {}
        self.market_items: List[Item] = []
        self.market_index = 1
        self.user_next_index = {}
        self.init_market()
    
    def init_market(self):
        """Инициализация стартовых товаров"""
        self.add_market_item("Меч", 50, "Острый меч")
        self.add_market_item("Щит", 30, "Защищает от атак")
        self.add_market_item("Зелье", 15, "Лечение")
    
    def get_user(self, user_id: int) -> UserData:
        if user_id not in self.users:
            self.users[user_id] = UserData()
            self.user_next_index[user_id] = 1
        return self.users[user_id]
    
    def add_market_item(self, name: str, cost: int, description: str) -> int:
        index = self.market_index
        self.market_index += 1
        item = Item(index, name, cost, description)
        self.market_items.append(item)
        return index
    
    def get_market_items(self) -> List[Item]:
        return self.market_items.copy()
    
    def find_market_item(self, identifier: str) -> Optional[Item]:
        identifier = identifier.lower().strip()
        
        # Поиск по номеру
        try:
            index = int(identifier)
            return next((item for item in self.market_items if item.index == index), None)
        except ValueError:
            pass
        
        # Поиск по названию
        return next((item for item in self.market_items 
                    if identifier in item.name.lower()), None)
    
    def buy_item(self, user_id: int, identifier: str) -> str:
        user = self.get_user(user_id)
        item = self.find_market_item(identifier)
        
        if not item:
            return "❌ Товар не найден на рынке!"
        
        if user.coins < item.cost:
            return f"❌ Недостаточно монет! Нужно: {item.cost}"
        
        # Удаляем товар с рынка
        self.market_items[:] = [i for i in self.market_items if i.index != item.index]
        
        # Добавляем в инвентарь пользователя
        user_index = self.user_next_index[user_id]
        user.items[user_index] = item
        self.user_next_index[user_id] += 1
        user.coins -= item.cost
        
        return f"✅ Куплен {item.name} (#{item.index}) за {item.cost} монет!"
    
    def find_user_item(self, user_id: int, identifier: str) -> Optional[Item]:
        user = self.get_user(user_id)
        identifier = identifier.lower().strip()
        
        # Поиск по номеру инвентаря пользователя
        try:
            index = int(identifier)
            return user.items.get(index)
        except ValueError:
            pass
        
        # Поиск по названию
        return next((item for item in user.items.values() 
                    if identifier in item.name.lower()), None)
    
    def sell_item(self, user_id: int, identifier: str) -> str:
        user = self.get_user(user_id)
        item = self.find_user_item(user_id, identifier)
        
        if not item:
            return "❌ Предмет не найден в инвентаре!"
        
        # Удаляем из инвентаря первый найденный
        for user_index, user_item in list(user.items.items()):
            if user_item.name.lower() == item.name.lower():
                del user.items[user_index]
                break
        
        sell_price = item.cost // 2
        user.coins += sell_price
        
        # Возвращаем на рынок с новым индексом
        new_index = self.add_market_item(item.name, item.cost, item.description)
        return f"✅ Продан {item.name} за {sell_price} монет! (новый на рынке: #{new_index})"

db = Database()