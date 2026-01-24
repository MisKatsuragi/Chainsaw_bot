from pathlib import Path
from typing import Dict, List, Set, Optional
import json
from dataclasses import dataclass, asdict, field

@dataclass
class Item:
    identifier: str  # Артикул
    name: str
    category: str  # Холодное оружие, Огнестрельное оружие, Вспомогательное снаряжение
    cost: int
    damage: int = 0
    penetration: int = 0
    protection: int = 0
    damage_reduction: int = 0
    recovery: int = 0
    overflow: int = 0  # Переполнение
    used_player_stats: Set[str] = field(default_factory=set)  # Используемые характеристики
    is_consumable: bool = False
    max_player_stats: Dict[str, int] = field(default_factory=dict)  # Max значения

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        item = cls(**{k: v for k, v in data.items() if k != 'used_player_stats' and k != 'max_player_stats'})
        item.used_player_stats = set(data.get('used_player_stats', []))
        item.max_player_stats = data.get('max_player_stats', {})
        return item

class ItemsDatabase:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.items: Dict[str, Item] = {}
        self.load()

    def load(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.items = {id: Item.from_dict(item_data) for id, item_data in data.items()}
            except:
                self.items = {}

    def save(self):
        data = {identifier: item.to_dict() for identifier, item in self.items.items()}
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_item(self, item: Item) -> bool:
        if item.identifier in self.items:
            return False
        self.items[item.identifier] = item
        self.save()
        return True

    def get_item(self, identifier: str) -> Optional[Item]:
        return self.items.get(identifier)

    def get_items_by_category(self, category: str) -> List[Item]:
        return [item for item in self.items.values() if item.category == category]

    def get_all_items(self) -> List[Item]:
        return list(self.items.values())