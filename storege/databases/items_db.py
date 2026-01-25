# storege/databases/items_db.py 
from pathlib import Path
from typing import Dict, List, Optional, Set
import json
from dataclasses import dataclass, asdict, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .character_db import Character

@dataclass
class Item:
    # Объязательные свойства
    category: str
    identifier: str
    name: str
    
    # Свойства с дефолтными значениями
    cost: int = 0
    damage: int = 0
    penetration: int = 0
    protection: int = 0
    damage_reduction: int = 0
    recovery: int = 0
    overflow: int = 0
    usecondition: int = 0
    description: str = ""
    used_player_stats: Set[str] = field(default_factory=set)
    max_player_stats: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = asdict(self)
        data['used_player_stats'] = list(self.used_player_stats)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        item_data = {
            'category': data.get('category', ''),
            'identifier': data.get('identifier', ''),
            'name': data.get('name', ''),
            'cost': int(data.get('cost', 0)),
            'damage': int(data.get('damage', 0)),
            'penetration': int(data.get('penetration', 0)),
            'protection': int(data.get('protection', 0)),
            'damage_reduction': int(data.get('damage_reduction', 0)),
            'recovery': int(data.get('recovery', 0)),
            'overflow': int(data.get('overflow', 0)),
            'usecondition': int(data.get('usecondition', 0)),
            'description': data.get('description', ''),
        }
        item_data['used_player_stats'] = set(data.get('used_player_stats', []))
        item_data['max_player_stats'] = data.get('max_player_stats', {})
        return cls(**item_data)
    
    def get_formatted_stats(self) -> list[str]:
        stats = []
        if self.damage: stats.append(f"+Урон:{self.damage}")
        if self.protection: stats.append(f"+Защита:{self.protection}")
        if self.recovery: stats.append(f"+Восст:{self.recovery}")
        if self.overflow: stats.append(f"+Оверхил:{self.overflow}")
        if self.damage_reduction: stats.append(f"-Снижение:{self.damage_reduction}")
        if self.penetration: stats.append(f"-Пробитие:{self.penetration}")
        return stats


class ItemsDatabase:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._items: Dict[str, Item] = {}
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
        return self._items
