# storege/excel_import.py
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
        """Импорт с ПОЛНОЙ ОТЛАДКОЙ"""
        print(f"🔍 Ищем файл: {self.excel_path.absolute()}")
        
        if not self.excel_path.exists():
            return f"❌ Market.xlsx не найден по пути: {self.excel_path.absolute()}"
        
        try:
            print("📖 Читаем Excel...")
            df = pd.read_excel(self.excel_path, header=None)
            print(f"✅ Excel прочитан! Размер: {df.shape}")
            print("📊 Первые 10 ячеек:")
            print(df.iloc[:10, :5].to_string())
            
            items_added = self._parse_excel(df)
            return f"✅ Импортировано {items_added} предметов!"
            
        except Exception as e:
            return f"❌ Ошибка импорта: {str(e)}"

    def _parse_excel(self, df) -> int:
        """ГЛАВНЫЙ МЕТОД ПАРСЕРА"""
        items_added = 0
        row_idx = 0
        
        while row_idx < len(df):
            # Ищем заголовок категории (Cold, Fire, Helpful)
            cell_value = str(df.iloc[row_idx, 0]).strip().upper()
            
            if cell_value in self.category_map:
                category_key = cell_value.lower()
                category_name = self.category_map[category_key]
                print(f"\n🎯 НАЙДЕНА КАТЕГОРИЯ: {category_name} (строка {row_idx})")
                
                # Парсим предметы в этой категории (со след. строки, все столбцы)
                items_added += self._parse_category(df, row_idx + 1, category_name)
            
            row_idx += 1
        
        return items_added

    def _parse_category(self, df, start_row: int, category: str) -> int:
        """Парсит все предметы в категории (по столбцам)"""
        items_added = 0
        col_idx = 1  # Начинаем со 2-го столбца (0-й = название категории)
        
        print(f"🔍 Парсим категорию '{category}' с {start_row} строки...")
        
        while col_idx < len(df.columns):
            item_data = self._parse_item_column(df, start_row, col_idx, category)
            if item_data:
                item = self._create_item(item_data, category)
                if dm.add_market_item(item):  # ✅ Нужно добавить в DataManager
                    items_added += 1
                    print(f"✅ ДОБАВЛЕН: {item.name} #{item.identifier}")
                else:
                    print(f"⚠️ НЕ ДОБАВЛЕН (дубль): {item.name}")
            
            col_idx += 1
        
        return items_added

    def _parse_item_column(self, df, start_row: int, col_idx: int, category: str) -> dict:
        """✅ парсинг столбца для структуры Excel"""
        item_data = {'category': category}
        row_idx = start_row
        properties = {}
        
        print(f"   📦 Парсим столбец {col_idx}...")
        
        while row_idx < len(df) and row_idx < start_row + 30:
            cell_value = str(df.iloc[row_idx, col_idx]).strip()
            
            if pd.isna(df.iloc[row_idx, col_idx]) or not cell_value:
                row_idx += 1
                continue
                
            print(f"     {row_idx}: '{cell_value}'")
            
            # ✅ ПОЛНЫЙ словарь соответствий Excel → Item поля
            prop_map = {
                'название': 'name',
                'стоимость': 'cost',
                'урон': 'damage',
                'пробитие': 'penetration',
                'защита': 'protection',
                'снижение урона': 'damage_reduction',
                'лечение': 'recovery',
                'аттрибуты': 'used_player_stats',
                'тип': 'type',
                'использование': 'usecondition',
                'максимальное значение ловкости': 'max_player_stats',
                'максимальное значение': 'max_player_stats',
                'оверхил': 'overflow',
                'охил': 'overflow',
                'описание': 'description'
            }
            
            prop_key = None
            for excel_name, standard_name in prop_map.items():
                if cell_value.lower().startswith(excel_name.lower()):
                    prop_key = standard_name
                    break
            
            if prop_key:
                # Следующая строка = значение свойства
                if row_idx + 1 < len(df):
                    value = str(df.iloc[row_idx + 1, col_idx]).strip()
                    properties[prop_key] = value
                    print(f"      → {prop_key}: '{value}'")
                    row_idx += 2  # Пропускаем название+значение
                    continue
            
            # Первое непустое = название предмета
            if 'name' not in item_data and 'название' not in properties:
                item_data['name'] = cell_value
                print(f"      → Название предмета: {cell_value}")
                
            row_idx += 1
        
        # Переносим все свойства в item_data
        item_data.update(properties)
        
        # Минимальная проверка
        if item_data.get('name') or item_data.get('название'):
            print(f"✅ Найден предмет: {item_data.get('name', item_data.get('название', '???'))}")
            return item_data
        
        print(f"   ❌ Столбец {col_idx} пустой")
        return None

    def _create_item(self, data: dict, category: str) -> Item:
        """✅ ПОЛНОЕ создание Item со ВСЕМИ полями"""
        name = data.get('name') or data.get('название', 'Без названия')
        
        # ✅ ИСПРАВЛЕННАЯ генерация ID
        base_id = re.sub(r'[^A-ZА-Я0-9]', '', name)[:4].upper()
        item_count = len(dm.items_db.items)
        identifier = f"{base_id}{item_count + 1:03d}"
        
        # Безопасное преобразование в int
        def safe_int(val, default=0):
            try:
                return int(str(val).strip())
            except (ValueError, TypeError):
                return default
        
        # ✅ Парсинг атрибутов → used_player_stats (Set[str])
        attrs_str = data.get('used_player_stats', '')
        used_stats = set()
        if attrs_str:
            # "Ловкость,Сила" → {'Ловкость', 'Сила'}
            attrs_list = re.split(r'[,\s]+', str(attrs_str).strip())
            used_stats = {attr.strip() for attr in attrs_list if attr.strip()}
        
        # ✅ Парсинг max_player_stats (Dict[str, int])
        max_stats = {}
        max_stats_str = data.get('max_player_stats', '')
        if max_stats_str:
            stat_name = str(max_stats_str).lower()
            value = safe_int(max_stats_str)
            if 'ловк' in stat_name or 'dex' in stat_name:
                max_stats['Ловкость'] = value
            elif 'сила' in stat_name or 'str' in stat_name:
                max_stats['Сила'] = value
        
        # ✅ Создание Item со ВСЕМИ полями
        item = Item(
            identifier=identifier,
            name=name,
            category=category,  # ✅ Критично для фильтрации
            cost=safe_int(data.get('cost', 0)),
            damage=safe_int(data.get('damage', 0)),
            penetration=safe_int(data.get('penetration', 0)),
            protection=safe_int(data.get('protection', 0)),
            damage_reduction=safe_int(data.get('damage_reduction', 0)),
            recovery=safe_int(data.get('recovery', 0)),
            overflow=safe_int(data.get('overflow', 0)),
            used_player_stats=used_stats,  # ✅ Для фильтрации по атрибутам
            usecondition=safe_int(data.get('usecondition', 0)),
            max_player_stats=max_stats  # ✅ Максимальные статы
        )
        
        # ✅ Сохранение типа в названии для UI фильтрации
        item_type = data.get('type', 'Неизвестно')
        if item_type and item_type != 'Неизвестно':
            item.name = f"{name} [{item_type}]"
        
        print(f"🎯 Создан Item: {item.identifier} | {item.name} | Тип: {item_type} | Категория: {category}")
        return item


# ✅ Точка входа для тестирования
def import_market_from_excel(excel_path: str = "Market.xlsx") -> str:
    """Удобная функция для вызова из других модулей"""
    importer = ExcelMarketImporter(excel_path)
    return importer.import_market()