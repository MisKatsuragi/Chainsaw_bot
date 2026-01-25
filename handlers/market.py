# market.py 
from typing import Dict, List, Optional
from storege.data_manager import dm
from storege.databases.items_db import Item
from common_utils import send_message
import re

SUBCATEGORIES = {
    "Холодное оружие": ["Кинжал", "Тесак", "Меч", "Дробящее", "Копьё", "Хлодное стрелковое"],
    "Огнестрельное оружие": ["Пистолет", "Пистолет-пулемёт", "Штурмовая винтовка", "Снайперская винтовка", "Дробовик"],
    "Вспомогательное снаряжение": ["Броня", "Аптечка", "Инфа"]
}

CATEGORIES = {
    "cold": "Холодное оружие",
    "fire": "Огнестрельное оружие", 
    "helpful": "Вспомогательное снаряжение",
    "холодное": "Холодное оружие",
    "огнестрельное": "Огнестрельное оружие",
    "вспомогательное": "Вспомогательное снаряжение",
    "огонь": "Огнестрельное оружие"
}

def market_command(event, vk_session, peer_id):
    """🏪 Главное меню"""
    market_text = """🏪 МАРКЕТ

🔪 Холодное оружие (cold/холодное)
🔫 Огнестрельное оружие (fire/огнестрельное/огонь) 
🛡️ Вспомогательное снаряжение (helpful/вспомогательное)

📋 Выберите категорию"""
    send_message(vk_session, peer_id, market_text)
    
    from after_commands import after_manager
    after_manager.add_command(event.user_id, "market.category")
    return True

def handle_category_cmd(event, vk_session, peer_id, state):
    """Обработка категории"""
    text = event.text.lower().strip()
    
    # Команда выхода всегда работает
    if text == "exit":
        return exit_market_command(event, vk_session, peer_id, state)
    
    if text not in CATEGORIES:
        send_message(vk_session, peer_id, 
            "❓ Категории:\n• cold/холодное\n• fire/огнестрельное/огонь\n• helpful/вспомогательное")
        return True
    
    category = CATEGORIES[text]
    subcats = SUBCATEGORIES.get(category, [])
    
    print(f"🔍 '{text}' → '{category}' | Подкат: {len(subcats)}")
    
    # Подкатегории
    if subcats:
        subcats_text = f"📂 {category}\n\n"
        for i, subcat in enumerate(subcats, 1):
            subcats_text += f"{i}. {subcat}\n"
        subcats_text += "\nℹ️ Номер или 'назад'"
        send_message(vk_session, peer_id, subcats_text)
        
        from after_commands import after_manager
        after_manager.add_command(event.user_id, "market.subcategory", {"category": category})
        return True
    
    # Нет подкатегорий - показываем все
    items = dm.get_items_by_category(category)
    print(f"📦 '{category}': {len(items)} предметов")
    
    resp_text = f"📂 {category}\n\n"
    for item in items[:10]:
        resp_text += format_item_short(item) + "\n\n"
    resp_text += "\nℹ️ описание #артикул"
    send_message(vk_session, peer_id, resp_text)
    return True

def handle_subcategory_cmd(event, vk_session, peer_id, state):
    text = event.text.strip().lower()
    
    # Команда выхода всегда работает
    if text == "exit":
        return exit_market_command(event, vk_session, peer_id, state)
    
    if text == "назад":
        market_command(event, vk_session, peer_id)
        return True
    
    try:
        subcat_num = int(text)
    except:
        send_message(vk_session, peer_id, "❓ Номер или 'назад'")
        return True
    
    category = state.data.get("category")
    subcats = SUBCATEGORIES.get(category, [])
    
    if not (1 <= subcat_num <= len(subcats)):
        send_message(vk_session, peer_id, f"❓ 1-{len(subcats)}")
        return True
    
    subcat = subcats[subcat_num - 1]
    items = filter_items_by_subcategory(category, subcat)
    
    print(f"🔍 '{subcat}': {len(items)} предметов")
    
    text = f"📦 {subcat}\n\n"
    if items:
        for item in items:
            text += format_item_short(item) + "\n\n"
    else:
        text += "❌ Не найдено\n\n👉 назад"
    
    text += "ℹ️ описание #артикул"
    send_message(vk_session, peer_id, text)
    return True

def handle_description_cmd(event, vk_session, peer_id, state):
    """ команда описание"""
    text_lower = event.text.lower().strip()
    
    # ТОЧНОЕ совпадение "описание #ID"
    if not text_lower.startswith("описание"):
        return False
    
    match = re.search(r'#(\w+)', event.text)
    if not match:
        send_message(vk_session, peer_id, "❓ описание #артикул")
        return True
    
    identifier = match.group(1).upper()
    item = dm.items_db.get_item(identifier)
    
    print(f"🔍 Описание для #{identifier}")
    
    if item:
        send_message(vk_session, peer_id, format_item_full(item))
    else:
        send_message(vk_session, peer_id, f"❌ #{identifier} не найден")
    
    return True

def exit_market_command(event, vk_session, peer_id, state):
    """🚪 Выход из магазина"""
    from after_commands import after_manager
    after_manager.clear_command(event.user_id)
    send_message(vk_session, peer_id, "✅ Вы вышли из магазина")
    print(f"🚪 Пользователь {event.user_id} вышел из магазина")
    return True

after_handlers = {
    "market.category": handle_category_cmd,
    "market.subcategory": handle_subcategory_cmd,
    "market.description": handle_description_cmd 
}

def format_item_short(item: Item) -> str:
    lines = [f"#{item.identifier} {item.name}"]
    lines.append(f"💰 {item.cost}¥")
    
    stats = []
    if item.damage: stats.append(f"Урон:{item.damage}")
    if item.penetration: stats.append(f"Пр:{item.penetration}")
    if item.protection: stats.append(f"Защ:{item.protection}")
    if item.damage_reduction: stats.append(f"Сниж:{item.damage_reduction}")
    if item.recovery: stats.append(f"Восст:{item.recovery}")
    if item.overflow: stats.append(f"Оверх:{item.overflow}")
    if item.usecondition: stats.append(f"Исп:{item.usecondition}") 
    
    if stats:
        lines.append("|".join(stats))
    
    if item.used_player_stats:
        lines.append(f"⚡ {', '.join(item.used_player_stats)}")
    
    return "\n".join(lines)

def format_item_full(item: Item) -> str:
    """Полное описание С описанием"""
    text = f"📦 {item.name}\n"
    text += f"🏷️ #{item.identifier} | 💰 {item.cost}¥\n"
    text += f"📂 {item.category}\n\n"
    
    stats = []
    if item.damage: stats.append(f"⚔️ Урон: {item.damage}")
    if item.penetration: stats.append(f"💥 Пр: {item.penetration}")
    if item.protection: stats.append(f"🛡️ Защ: {item.protection}")
    if item.damage_reduction: stats.append(f"🛡️ Сниж: {item.damage_reduction}")
    if item.recovery: stats.append(f"💉 Восст: {item.recovery}")
    if item.overflow: stats.append(f"💥 Оверх: {item.overflow}")
    if item.usecondition: stats.append(f"🔧 Исп: {item.usecondition}")
    
    if stats:
        text += "📊 Статы:\n" + "\n".join(stats) + "\n\n"
    
    if item.used_player_stats:
        text += f"⚡ Требует: {', '.join(item.used_player_stats)}\n\n"
    
    if item.max_player_stats:
        text += "📏 Макс статы:\n" + "\n".join([f"• {k}: {v}" for k,v in item.max_player_stats.items()]) + "\n\n"
    
    if item.description:
        text += f"📝 {item.description}\n\n"
    
    text += "🛒 купить #артикул"
    return text

def extract_subcategory(name: str, category: str) -> str:
    """✅ Точное извлечение типа из [Тип]"""
    # 1. Извлекаем из [Тип]
    match = re.search(r'\[(.*?)\]', name)
    if match:
        return match.group(1)
    
    # 2. Ищем в названии
    name_lower = name.lower()
    type_map = {
        "Холодное оружие": ["кинжал", "тесак", "меч", "дробящее", "копьё", "хлодное стрелковое"],
        "Огнестрельное оружие": ["пистолет", "автомат", "снайперск", "дробовик"],
        "Вспомогательное снаряжение": ["броня", "аптечка", "инфа"]
    }
    
    for types in type_map.get(category, []):
        if types in name_lower:
            return types.capitalize()
    
    return "Разное"

def filter_items_by_subcategory(category: str, subcat: str) -> List[Item]:
    """✅ Фильтр по точному типу"""
    items = dm.get_items_by_category(category)
    filtered = []
    
    target_type = subcat.lower()
    
    for item in items:
        item_type = extract_subcategory(item.name, category).lower()
        if item_type == target_type:
            filtered.append(item)
            print(f"✅ {item.name} [{item_type}]")
    
    return filtered

def buy_item_command(event, vk_session, peer_id):
    """Покупка"""
    text = event.text.strip()
    match = re.search(r'#(\w+)', text)
    
    if not match:
        send_message(vk_session, peer_id, "❓ купить #артикул")
        return True
    
    identifier = match.group(1).upper()
    item = dm.items_db.get_item(identifier)
    
    if not item:
        send_message(vk_session, peer_id, f"❌ #{identifier} не найден")
        return True
    
    success = dm.buy_item(event.user_id, item)
    if success:
        send_message(vk_session, peer_id, f"✅ Куплен {item.name}\n💰 -{item.cost}¥")
    else:
        send_message(vk_session, peer_id, "❌ Недостаточно ¥")
    return True
