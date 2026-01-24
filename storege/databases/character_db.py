from pathlib import Path
from typing import Dict, Set, Optional
import json
from dataclasses import dataclass, asdict, field
from .items_db import Item

@dataclass
class Character:
    user_id: int  # Идентификатор
    name: str
    rank: str
    level: int = 1
    faction: str = ""
    char_class: str = ""
    profile_link: str = ""
    
    # Характеристики
    toughness: int = 10
    strength: int = 10
    reflexes: int = 10
    perception: int = 10
    intellect: int = 10
    charisma: int = 10
    luck: int = 10
    
    # Инвентарь
    inventory_items: Set[str] = field(default_factory=set)  # Артикулы предметов
    inventory_contracts: Set[str] = field(default_factory=set)  # ID контрактов
    
    yen: int = 0
    flesh_particles: int = 0
    total_flesh_particles: int = 0
    self_description: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data['inventory_items'] = list(self.inventory_items)
        data['inventory_contracts'] = list(self.inventory_contracts)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Character':
        char = cls(**data)
        char.inventory_items = set(data.get('inventory_items', []))
        char.inventory_contracts = set(data.get('inventory_contracts', []))
        return char

class CharactersDatabase:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.characters: Dict[int, Character] = {}
        self.load()

    def load(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.characters = {int(uid): Character.from_dict(cdata) for uid, cdata in data.items()}
            except:
                self.characters = {}

    def save(self):
        data = {str(char.user_id): char.to_dict() for char in self.characters.values()}
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_character(self, user_id: int) -> Optional[Character]:
        return self.characters.get(user_id)

    def create_or_get_character(self, user_id: int, name: str) -> Character:
        if user_id not in self.characters:
            self.characters[user_id] = Character(user_id=user_id, name=name)
            self.save()
        return self.characters[user_id]

    def save_character(self, character: Character):
        self.characters[character.user_id] = character
        self.save()