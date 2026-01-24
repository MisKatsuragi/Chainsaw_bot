from pathlib import Path
from typing import Dict, Set
import json

class RolesDatabase:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.admins: Set[int] = set()
        self.god: Set[int] = set()
        self.load()

    def load(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.admins = set(data.get('admins', []))
                self.god = set(data.get('god', []))
            except:
                pass

    def save(self):
        data = {
            'admins': list(self.admins),
            'god': list(self.god)
        }
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_admin(self, user_id: int):
        self.admins.add(user_id)
        self.save()

    def remove_admin(self, user_id: int):
        self.admins.discard(user_id)
        self.save()

    def add_god(self, user_id: int):
        self.god.add(user_id)
        self.save()

    def remove_god(self, user_id: int):
        self.god.discard(user_id)
        self.save()

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admins or user_id in self.god

    def is_god(self, user_id: int) -> bool:
        return user_id in self.god