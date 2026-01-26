from typing import Dict, List, Optional
from dataclasses import dataclass
from .databases.character_db import Character
from .data_manager import dm


@dataclass
class RichPlayer:
    user_id: int
    name: str
    yen: int
    flesh_particles: int
    total_wealth: int
    rank: str


class EconomyAnalyzer:
    """Анализатор экономики - отдельный класс для расчета статистики"""
    
    @staticmethod
    def get_top_yen_players(top_n: int = 10) -> List[dict]:
        """Топ-N игроков по йенам"""
        characters = dm.characters_db.characters
        if not characters:
            return []
    
        yen_list = []
        for char in characters.values():
            yen_list.append({
                'user_id': char.user_id,
                'name': char.name,
                'yen': char.yen,
                'flesh_particles': char.flesh_particles,
                'rank': char.rank
            })
    
        return sorted(yen_list, key=lambda x: x['yen'], reverse=True)[:top_n]


    @staticmethod
    def get_top_flesh_players(top_n: int = 10) -> List[dict]:
        """Топ-N игроков по частицам плоти"""
        characters = dm.characters_db.characters
        if not characters:
            return []
    
        flesh_list = []
        for char in characters.values():
            flesh_list.append({
                'user_id': char.user_id,
                'name': char.name,
                'yen': char.yen,
                'flesh_particles': char.flesh_particles,
                'rank': char.rank
            })
    
        return sorted(flesh_list, key=lambda x: x['flesh_particles'], reverse=True)[:top_n]
    
ecm = EconomyAnalyzer()    
