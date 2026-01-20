import json
import threading
import time
import atexit
import os
import shutil
from typing import Dict, List, Optional
from database import Database, Item, UserData, UserStats

class DataManager:
    def __init__(self, json_path: str = "database.json"):
        self.json_path = json_path
        self._dirty = False
        self.auto_save_thread = None
        
        # ✅ Инициализируем и загружаем данные
        self.db = Database(json_path)
        self.load_from_file()
        
        if not self.db.market_items:
            self.db.init_market()
            
        self.start_auto_save()
        atexit.register(self.save_to_file)

    def mark_dirty(self):
        self._dirty = True

    def save_to_file(self):
        if not self._dirty:
            return False
        
        data = self.db.to_dict()
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self._dirty = False
        return True

    def load_from_file(self):
        if not os.path.exists(self.json_path):
            return False
        
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # ✅ Полная переинициализация БД из данных
            self.db = Database.from_dict(data, self.json_path)
            self._dirty = False
            return True
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return False

    def reload_from_file(self):
        backup = f"{self.json_path}.backup"
        shutil.copy2(self.json_path, backup)
        return self.load_from_file()

    def start_auto_save(self):
        def auto_save_loop():
            while True:
                time.sleep(1800)  # 30 минут
                self.save_to_file()
        
        self.auto_save_thread = threading.Thread(target=auto_save_loop, daemon=True)
        self.auto_save_thread.start()

    def get_stats(self) -> Dict:
        stats = self.db.get_stats()
        rich_users = sorted(self.db.users.items(), 
                          key=lambda x: x[1].coins, reverse=True)[:10]
        stats['rich_users'] = rich_users
        return stats
    
    def get_forbes_message(self) -> dict:
        rich_users = sorted(self.db.users.items(), 
                          key=lambda x: x[1].coins, reverse=True)[:10]
        return rich_users

    # Прокси-методы для удобства
    def get_user(self, user_id: int):
        user = self.db.get_user(user_id)
        self.mark_dirty()
        return user

    def buy_item(self, user_id: int, identifier: str) -> str:
        result = self.db.buy_item(user_id, identifier)
        self.mark_dirty()
        return result

    def sell_item(self, user_id: int, identifier: str) -> str:
        result = self.db.sell_item(user_id, identifier)
        self.mark_dirty()
        return result

    def add_market_item(self, name: str, cost: int, description: str) -> int:
        result = self.db.add_market_item(name, cost, description)
        self.mark_dirty()
        return result

    def set_user_position(self, user_id: int, position: str):
        self.db.set_user_position(user_id, position)
        self.mark_dirty()

    @property
    def market_items(self) -> List:
        return self.db.market_items

    @property
    def users(self) -> Dict:
        return self.db.users
    
    @property
    def admins(self) -> set:
        return self.db.admins

    @property
    def god(self) -> set:
        return self.db.god

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.db.admins or user_id in self.db.god

    def is_god(self, user_id: int) -> bool:
        return user_id in self.db.god
    
# ✅ ГЛОБАЛЬНЫЙ ОБЪЕКТ dm создаётся при импорте модуля
dm = DataManager("database.json")