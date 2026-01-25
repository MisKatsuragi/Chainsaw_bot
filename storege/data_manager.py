import json
import threading
import time
import atexit
from pathlib import Path
from typing import Optional, Set
from .databases.items_db import ItemsDatabase, Item 
from .databases.character_db import CharactersDatabase, Character 
from .databases.contracts_db import ContractsDatabase, Contract
from .databases.roles_db import RolesDatabase


class DataManager:
    def __init__(self, databases_dir: str = "databases"):
        self.databases_dir = Path(databases_dir)
        self.databases_dir.mkdir(exist_ok=True)
        
        # ✅ Обычные атрибуты - БЕЗ @property!
        self.items_db = ItemsDatabase(str(self.databases_dir / "items.json"))
        self.characters_db = CharactersDatabase(str(self.databases_dir / "characters.json"))
        self.contracts_db = ContractsDatabase(str(self.databases_dir / "contracts.json"))
        self.roles_db = RolesDatabase(str(self.databases_dir / "roles.json"))
        
        self._dirty = {'items': False, 'characters': False, 'contracts': False, 'roles': False}
        self.start_auto_save()
        atexit.register(self.save_all)

    @property
    def admins(self) -> Set[int]:
        return self.roles_db.admins 

    @property
    def god(self) -> Set[int]:
        return self.roles_db.god 

    def mark_dirty(self, db_type: str):
        if db_type in self._dirty:
            self._dirty[db_type] = True

    def save_all(self):
        if self._dirty['items']:
            self.items_db.save()
            self._dirty['items'] = False
        if self._dirty['characters']:
            self.characters_db.save()
            self._dirty['characters'] = False
        if self._dirty['contracts']:
            self.contracts_db.save()
            self._dirty['contracts'] = False
        if self._dirty['roles']:
            self.roles_db.save()
            self._dirty['roles'] = False

    def start_auto_save(self):
        def auto_save_loop():
            while True:
                time.sleep(3600)
                self.save_all()
        self.auto_save_thread = threading.Thread(target=auto_save_loop, daemon=True)
        self.auto_save_thread.start()

    def get_character(self, user_id: int) -> Optional[Character]:
        return self.characters_db.get_character(user_id)

    def get_or_create_character(self, user_id: int, name: str) -> Character:
        char = self.characters_db.create_or_get_character(user_id, name)
        self.mark_dirty('characters')
        return char

    def get_item(self, identifier: str) -> Optional[Item]:
        return self.items_db.get_item(identifier)

    def get_items_by_category(self, category: str) -> list:
        return self.items_db.get_items_by_category(category)

    def is_admin(self, user_id: int) -> bool:
        return self.roles_db.is_admin(user_id)

    def is_god(self, user_id: int) -> bool:
        return self.roles_db.is_god(user_id)

    def add_market_item(self, item: Item) -> bool:
        if self.items_db.add_item(item):
            self.mark_dirty('items')
            return True
        return False

    def get_stats(self):
        return {
            'users_count': len(getattr(self.characters_db, 'characters', {})),
            'total_items': len(self.items_db.items),
            'total_received': 0,
            'total_spent': 0,
            'rich_users': []
        }


dm = DataManager()