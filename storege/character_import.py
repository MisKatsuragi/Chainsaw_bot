# storage/character_import.py - ПОЛНЫЙ КОД с дополнительным импортом

import pandas as pd
from pathlib import Path
import re
from .data_manager import dm
from .databases.character_db import Character


class ExcelCharacterImporter:
    def __init__(self, excel_path: str = "Characters.xlsx"):
        self.excel_path = Path(excel_path)
        self.character_fields = [
            'name', 'rank', 'level', 'char_class', 'profile_link',
            'toughness', 'strength', 'reflexes', 'perception', 
            'intellect', 'charisma', 'luck', 'yen', 'flesh_particles',
            'self_description'
        ]
        
    def import_characters(self) -> str:
        """Основной импорт из основного файла"""
        print(f"🔍 Ищем файл: {self.excel_path.absolute()}")
        if not self.excel_path.exists():
            return f"❌ Файл не найден: {self.excel_path.absolute()}"
        
        try:
            df = pd.read_excel(self.excel_path, header=None)
            print(f"✅ Excel: {df.shape}")
            print("📊 Первые строки:")
            print(df.iloc[:10, :3].to_string())
            
            chars_added = self._parse_excel(df)
            return f"✅ Импортировано {chars_added} персонажей!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def import_additional_characters(self, additional_path: str = "Characters_Additional.xlsx") -> str:
        """✅ ДОПОЛНИТЕЛЬНЫЙ импорт из ВТОРОГО файла"""
        print(f"🔍 Ищем ДОПОЛНИТЕЛЬНЫЙ файл: {Path(additional_path).absolute()}")
        
        additional_path = Path(additional_path)
        if not additional_path.exists():
            return f"ℹ️ Дополнительный файл не найден: {additional_path.absolute()}"
        
        try:
            # ✅ Считаем ДО и ПОСЛЕ
            before_count = len(dm.characters_db.characters)
            print(f"📊 Было персонажей: {before_count}")
            
            # ✅ ТОТ ЖЕ САМЫЙ парсер
            df = pd.read_excel(additional_path, header=None)
            chars_added = self._parse_excel(df)
            
            after_count = len(dm.characters_db.characters)
            print(f"📊 Стало персонажей: {after_count}")
            
            return f"✅ ДОПОЛНИТЕЛЬНЫЙ импорт: +{chars_added} персонажей!\n👥 Всего персонажей: {after_count}"
        except Exception as e:
            return f"❌ Ошибка доп. импорта: {str(e)}"

    def _parse_excel(self, df) -> int:
        chars_added = 0
        row_idx = 0
        
        while row_idx < len(df):
            cell = str(df.iloc[row_idx, 0]).strip()
            if cell:  # Фракция объявлена в первой ячейке
                faction = cell
                print(f"\n🎯 ФРАКЦИЯ: {faction} (строка {row_idx})")
                
                # Следующая строка - заголовки свойств (проверяем соответствие)
                headers_row = row_idx + 1
                if headers_row < len(df):
                    headers = [str(df.iloc[headers_row, col]).strip().lower() 
                             for col in range(len(df.columns))]
                    print(f"📋 Заголовки: {headers[:5]}...")
                    
                    # Ищем персонажей начиная со следующей строки
                    chars_added += self._parse_faction_characters(
                        df, headers_row + 1, faction
                    )
            
            row_idx += 1
        return chars_added

    def _parse_faction_characters(self, df, start_row: int, faction: str) -> int:
        """Парсит персонажей в колонках начиная с указанной строки"""
        chars_added = 0
        
        for col_idx in range(len(df.columns)):
            char_data = self._read_character_column(df, start_row, col_idx)
            if char_data:
                # Присваиваем user_id по номеру колонки (или можно добавить поле)
                user_id = col_idx + 1  # 1, 2, 3... для каждой колонки
                
                char = Character(
                    user_id=user_id,
                    faction=faction,
                    **char_data
                )
                
                existing = dm.get_character(user_id)
                if not existing:
                    dm.characters_db.characters[user_id] = char
                    dm.mark_dirty('characters')
                    chars_added += 1
                    print(f"✅ Персонаж #{user_id}: {char.name} [{faction}]")
                else:
                    print(f"⚠️  Персонаж #{user_id} уже существует, пропускаем")
        
        dm.characters_db.save()
        return chars_added

    def _read_character_column(self, df, start_row: int, col_idx: int) -> dict:
        """Читает данные персонажа из колонки"""
        safe_int = lambda val: int(str(val).strip()) if str(val).strip().isdigit() else 0
        safe_str = lambda val: str(val).strip() if str(val).strip() else ""
        
        char_data = {}
        row_idx = start_row
        
        # Читаем по порядку полей
        for field_name in self.character_fields:
            if row_idx >= len(df):
                break
                
            val = df.iloc[row_idx, col_idx]
            val_str = str(val).strip()
            
            if pd.isna(val) or val_str.lower() == 'nan' or not val_str:
                value = 0 if 'level' in field_name or field_name in [
                    'toughness', 'strength', 'reflexes', 'perception', 
                    'intellect', 'charisma', 'luck', 'yen', 'flesh_particles'
                ] else ""
            else:
                if field_name in ['level', 'toughness', 'strength', 'reflexes', 
                                'perception', 'intellect', 'charisma', 'luck', 
                                'yen', 'flesh_particles']:
                    value = safe_int(val)
                else:
                    value = safe_str(val)
            
            char_data[field_name] = value
            row_idx += 1
        
        # Проверяем, что есть имя
        if not char_data.get('name') or char_data['name'] == 'Без имени':
            return None
            
        print(f"📦 Колонка {col_idx}: {char_data['name']} -> {list(char_data.keys())}")
        return char_data


# ✅ ФУНКЦИИ-ОБЕРТКИ (для обратной совместимости)
def import_characters_from_excel(excel_path: str = "Characters.xlsx") -> str:
    importer = ExcelCharacterImporter(excel_path)
    return importer.import_characters()

def import_additional_characters_from_excel(excel_path: str = "Characters_Additional.xlsx") -> str:
    """✅ НОВЫЙ ЭКСПОРТ - использует тот же класс!"""
    importer = ExcelCharacterImporter("dummy.xlsx")  # путь не важен
    return importer.import_additional_characters(excel_path)