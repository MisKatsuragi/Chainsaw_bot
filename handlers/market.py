# market.py 
import re
from typing import Dict, List, Optional
from storege.data_manager import dm
from storege.databases.items_db import Item
from common_utils import send_message, format_item_short, format_item_full


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

# ✅ Команды выхода из магазина
EXIT_COMMANDS = {"exit", "выход", "назад", "стоп", "отмена"}

def market_command(event, vk_session, peer_id):
    """🏪 Главное меню"""
    market_text = """🏪 МАРКЕТ

🔪 Холодное оружие (cold/холодное)
🔫 Огнестрельное оружие (fire/огнестрельное/огонь) 
🛡️ Вспомогательное снаряжение (helpful/вспомогательное)

📦 **Управление:**
• `описание #артикул` - инфо
• `купить #артикул` - покупка
• `продать #артикул` - продажа
• `инвентарь` - сумка

📋 Выберите категорию"""
    send_message(vk_session, peer_id, market_text)
    
    from after_commands import after_manager
    after_manager.add_command(event.user_id, "market.category")
    after_manager.set_timeout(event.user_id, 60)
    return True

def handle_category_cmd(event, vk_session, peer_id, state):
    """Обработка категории"""
    text = event.text.lower().strip()
    
    # ✅ Команда выхода всегда работает
    if text in EXIT_COMMANDS:
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
        after_manager.set_timeout(event.user_id, 60)
        return True
    
    # Нет подкатегорий - показываем все
    items = dm.get_items_by_category(category)
    print(f"📦 '{category}': {len(items)} предметов")
    
    resp_text = f"📂 {category}\n\n"
    for item in items[:10]:
        resp_text += format_item_short(item) + "\n\n"
    resp_text += "\nℹ️ описание #артикул"
    send_message(vk_session, peer_id, resp_text)
    after_manager.set_timeout(event.user_id, 60)
    return True

def handle_subcategory_cmd(event, vk_session, peer_id, state):
    text = event.text.strip().lower()
    
    # ✅ Команда выхода всегда работает
    if text in EXIT_COMMANDS:
        return exit_market_command(event, vk_session, peer_id, state)
    
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
    # ✅ Продлеваем таймаут
    from after_commands import after_manager
    after_manager.set_timeout(event.user_id, 60)
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
    "market.subcategory": handle_subcategory_cmd
}

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
