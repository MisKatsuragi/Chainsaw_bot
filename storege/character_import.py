import pandas as pd
from pathlib import Path
from storege.data_manager import dm
from storege.databases.character_db import Character
from common_utils import send_message
from typing import Dict, Any

def import_profiles_from_excel(file_path: str) -> str:
    """
    Импорт профилей персонажей из Excel файла
    
    Формат Excel:
    - Строка 1: названия свойств (user_id, name, toughness, strength, ...)
    - Столбец A: названия свойств
    - Остальные столбцы: данные персонажей
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return f"❌ Файл {file_path} не найден"
        
        # Читаем Excel файл
        df = pd.read_excel(file_path)
        
        if df.empty:
            return "❌ Excel файл пуст"
        
        # Первая колонка - названия свойств
        properties = df.iloc[:, 0].dropna().str.lower().str.strip().tolist()
        
        imported_count = 0
        
        # Обрабатываем каждую колонку персонажа (начиная со второй)
        for col_idx in range(1, len(df.columns)):
            col_name = df.columns[col_idx]
            character_data = {}
            
            # Собираем данные для персонажа из текущей колонки
            for idx, prop in enumerate(properties):
                if idx < len(df) and pd.notna(df.iloc[idx, col_idx]):
                    value = df.iloc[idx, col_idx]
                    # Конвертируем числовые значения
                    if prop in ['user_id', 'level', 'toughness', 'strength', 'reflexes', 
                               'perception', 'intellect', 'charisma', 'luck', 'yen', 
                               'flesh_particles', 'total_flesh_particles']:
                        try:
                            character_data[prop] = int(float(value))
                        except:
                            character_data[prop] = value
                    else:
                        character_data[prop] = str(value)
            
            # Проверяем наличие user_id
            if 'user_id' not in character_data or not character_data['user_id']:
                print(f"⚠️ Пропущен персонаж в колонке {col_name}: нет user_id")
                continue
            
            user_id = character_data['user_id']
            
            # Создаем или обновляем персонажа
            try:
                if user_id in dm.characters_db.characters:
                    character = dm.characters_db.characters[user_id]
                    # Обновляем только изменяемые поля
                    for key, value in character_data.items():
                        if key in ['name', 'faction', 'char_class', 'self_description', 'rank']:
                            setattr(character, key, value)
                    dm.characters_db.save_character(character)
                else:
                    character = Character.from_dict(character_data)
                    dm.characters_db.save_character(character)
                
                imported_count += 1
                print(f"✅ Импортирован персонаж ID {user_id}")
                
            except Exception as e:
                print(f"❌ Ошибка импорта персонажа {user_id}: {str(e)}")
                continue
        
        return f"✅ **Импорт завершен!**\n📊 Импортировано профилей: {imported_count}"
        
    except Exception as e:
        return f"❌ **Ошибка импорта:** {str(e)}"

def import_god_command(event, vk_session, peer_id, file_path: str):
    """Команда импорта для GOD (требует путь к файлу)"""
    result = import_profiles_from_excel(file_path)
    send_message(vk_session, peer_id, result)