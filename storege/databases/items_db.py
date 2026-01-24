# storege/databases/items_db.py
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
from dataclasses import dataclass, asdict, field
from typing import TYPE_CHECKING

# ✅ TYPE_CHECKING предотвращает циклические импорты
if TYPE_CHECKING:
    from .character_db import Character

@dataclass
class Item:
    identifier: str
    name: str
    category: str
    cost: int
    damage: int = 0
    penetration: int = 0
    protection: int = 0
    damage_reduction: int = 0
    recovery: int = 0
    overflow: int = 0
    used_player_stats: Set[str] = field(default_factory=set)
    usecondition: int = 0
    max_player_stats: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = asdict(self)
        data['used_player_stats'] = list(self.used_player_stats)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """✅ ИСПРАВЛЕНО: Игнорирует неизвестные поля типа 'type'"""
        # ✅ ФИЛЬТРУЕМ неизвестные поля (type, description, etc.)
        known_fields = {
            'identifier', 'name', 'category', 'cost', 'damage', 'penetration', 
            'protection', 'damage_reduction', 'recovery', 'overflow', 
            'used_player_stats', 'usecondition', 'max_player_stats'
        }
    
        # Берем ТОЛЬКО известные поля
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
    
        item = cls(**filtered_data)
        item.used_player_stats = set(data.get('used_player_stats', []))
        item.max_player_stats = data.get('max_player_stats', {})
        return item


class ItemsDatabase:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._items: Dict[str, Item] = {}  # ✅ ИСПРАВЛЕНО: _items вместо items
        self.load()

    def load(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._items = {identifier: Item.from_dict(item_data) 
                             for identifier, item_data in data.items()}
                print(f"✅ Загружено {len(self._items)} предметов")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки items_db: {e}")
                self._items = {}
        else:
            print("ℹ️ Файл items.json не найден")
            self._items = {}

    def save(self):
        try:
            data = {identifier: item.to_dict() for identifier, item in self._items.items()}
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 Сохранено {len(self._items)} предметов")
        except Exception as e:
            print(f"❌ Ошибка сохранения items_db: {e}")

    def add_item(self, item: Item) -> bool:
        if item.identifier in self._items:
            print(f"⚠️ Предмет {item.identifier} уже существует")
            return False
        self._items[item.identifier] = item
        self.save()
        print(f"✅ Добавлен: {item.name} [{item.identifier}]")
        return True

    def get_item(self, identifier: str) -> Optional[Item]:
        return self._items.get(identifier)

    def get_items_by_category(self, category: str) -> List[Item]:
        return [item for item in self._items.values() if item.category == category]

    def get_all_items(self) -> List[Item]:
        return list(self._items.values())

    @property
    def items(self) -> Dict[str, Item]:
        """✅ ТОЛЬКО ЧТЕНИЕ - для DataManager"""
        return self._items
