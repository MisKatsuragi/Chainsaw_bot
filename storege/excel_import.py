# storage/excel_import.py
import pandas as pd
from pathlib import Path
import re
from .data_manager import dm
from .databases.items_db import Item

class ExcelMarketImporter:
    def __init__(self, excel_path: str = "Market.xlsx"):
        self.excel_path = Path(excel_path)
        self.category_map = {
            "COLD": "Холодное оружие",
            "FIRE": "Огнестрельное оружие", 
            "HELPFUL": "Вспомогательное снаряжение",
            "cold": "Холодное оружие",
            "fire": "Огнестрельное оружие", 
            "helpful": "Вспомогательное снаряжение"
        }
    
    def import_market(self) -> str:
        print(f"🔍 Ищем файл: {self.excel_path.absolute()}")
        if not self.excel_path.exists():
            return f"❌ Файл не найден: {self.excel_path.absolute()}"
        
        try:
            df = pd.read_excel(self.excel_path, header=None)
            print(f"✅ Excel: {df.shape}")
            print("📊 Первые строки:")
            print(df.iloc[:10, :3].to_string())
            
            items_added = self._parse_excel(df)
            return f"✅ Импортировано {items_added} предметов!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def _parse_excel(self, df) -> int:
        items_added = 0
        row_idx = 0
        
        while row_idx < len(df):
            cell = str(df.iloc[row_idx, 0]).strip().upper()
            if cell in self.category_map:
                category = self.category_map[cell.lower()]
                print(f"\n🎯 КАТЕГОРИЯ: {category} (строка {row_idx})")
                items_added += self._parse_category(df, row_idx + 1, category)
            row_idx += 1
        return items_added

    def _parse_category(self, df, start_row: int, category: str) -> int:
        """Читает предметы ПО СТРОКАМ начиная со 2-го столбца"""
        items_added = 0
        
        for col_idx in range(1, len(df.columns)):  # со 2-го столбца
            item_data = self._read_item_row(df, start_row, col_idx, category)
            if item_data:
                item = self._create_item(item_data, category)
                if dm.add_market_item(item):
                    items_added += 1
                    print(f"✅ {item.name} #{item.identifier}")
        
        return items_added

    def _read_item_row(self, df, start_row: int, col_idx: int, category: str) -> dict:
        """ТОЧНЫЕ позиции Excel"""
        item_data = {'category': category}
        safe_int = lambda val: int(str(val).strip()) if str(val).strip().isdigit() else 0
    
        values = []
        for i in range(8):
            row = start_row + i
            if row >= len(df): break
            val = str(df.iloc[row, col_idx]).strip()
            if pd.isna(df.iloc[row, col_idx]) or val.lower() == 'nan':
                val = ""
            values.append(val)
    
        print(f"📦 col={col_idx}: {values}")
    
        name = values[0].strip()
        if not name or name.lower() == "final":
            return None
    
        # ТОЧНЫЕ позиции типов
        if category == "Холодное оружие":
            # 0.Название 1.Стоимость 2.Урон 3.Пробитие 4.Защита 5.Атрибуты 6.Тип 7.Описание
            item_type_pos = 6
            item_data.update({
                'cost': safe_int(values[1]),
                'damage': safe_int(values[2]),
                'penetration': safe_int(values[3]),
                'protection': safe_int(values[4]),
                'used_player_stats': values[5] or ""
            })
    
        elif category == "Огнестрельное оружие":
            # 0.Название 1.Стоимость 2.Урон 3.Пробитие 4.Атрибуты 5.Тип 6.Использование 7.Описание
            item_type_pos = 5  # ТИП на позиции 5!
            item_data.update({
                'cost': safe_int(values[1]),
                'damage': safe_int(values[2]),
                'penetration': safe_int(values[3]),
                'used_player_stats': values[4] or "",
                'usecondition': safe_int(values[6])
            })
    
        elif category == "Вспомогательное снаряжение":
            # 0.Название 1.Стоимость 2.Снижение 3.Ловкость 4.Лечение 5.Оверхил 6.Тип 7.Использование
            item_type_pos = 6
            item_data.update({
                'cost': safe_int(values[1]),
                'damage_reduction': safe_int(values[2]),
                'max_player_stats': {'Ловкость': safe_int(values[3])},
                'recovery': safe_int(values[4]),
                'overflow': safe_int(values[5]),
                'usecondition': safe_int(values[7]) if len(values) > 7 else 0
            })
    
        # ТИП ТОЧНО из ячейки
        item_type_raw = values[item_type_pos] if len(values) > item_type_pos else ""
        item_type = item_type_raw.strip()
    
        item_data.update({
            'name': name,  # ЧИСТОЕ название
            'type': item_type,  # ПОЛНЫЙ тип из Excel
            'description': values[7] if len(values) > 7 else ""
        })
    
        print(f"✅ RAW: '{name}' | ТИП:'{item_type}' (pos={item_type_pos})")
        return item_data


    def _create_item(self, data: dict, category: str) -> Item:
        """Item БЕЗ дублирования [Тип]"""
        name = data.get('name', 'Без названия').strip()
        item_type = data.get('type', '').strip()
    
        #  ID
        clean_name = re.sub(r'[^A-ZА-Я0-9]', '', name)[:4].upper()
        identifier = f"{clean_name}{len(dm.items_db.items) + 1:03d}"
    
        # Атрибуты
        attrs = data.get('used_player_stats', '')
        used_stats = set(re.split(r'[,\s;]+', str(attrs)) if attrs else [])
        used_stats = {s.strip() for s in used_stats if s.strip()}
    
        # НАЗВАНИЕ БЕЗ [Тип] + добавляем ТОЛЬКО если тип есть
        final_name = name
        if item_type:
            # Удаляем старые скобки если есть
            final_name = re.sub(r'\[.*?\]', '', name).strip()
            final_name = f"{final_name} [{item_type}]"
    
        item = Item(
            category=category,
            identifier=identifier,
            name=final_name,
            cost=data.get('cost', 0),
            damage=data.get('damage', 0),
            penetration=data.get('penetration', 0),
            protection=data.get('protection', 0),
            damage_reduction=data.get('damage_reduction', 0),
            recovery=data.get('recovery', 0),
            overflow=data.get('overflow', 0),
            description=data.get('description', ''),
            used_player_stats=used_stats,
            usecondition=data.get('usecondition', 0),
            max_player_stats=data.get('max_player_stats', {})
        )
    
        print(f"🎯 {item.identifier}: '{item.name}' [Тип:{item_type}]")
        return item

def import_market_from_excel(excel_path: str = "Market.xlsx") -> str:
    importer = ExcelMarketImporter(excel_path)
    return importer.import_market()
