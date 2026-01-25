# market.py - ✅ УБИРАЕМ from after_commands import after_handler
from typing import Dict, List
from storege.data_manager import dm
from storege.databases.items_db import Item
from common_utils import send_message
import re


SUBCATEGORIES = {
    "Холодное оружие": ["Кинжалы", "Мечи", "Топоры", "Ножи"],
    "Огнестрельное оружие": ["Пистолеты", "Автоматы", "Снайперские", "Дробовики"],
    "Вспомогательное снаряжение": ["Броня", "Аптечки", "Гранаты"]
}

CATEGORIES = {
    "холодное": "Холодное оружие",
    "огнестрельное": "Огнестрельное оружие", 
    "вспомогательное": "Вспомогательное снаряжение"
}


def market_command(event, vk_session, peer_id):
    market_text = """🏪 Маркет

🔪 Холодное оружие (холодное)
🔫 Огнестрельное оружие (огнестрельное) 
🛡️ Вспомогательное снаряжение (вспомогательное)"""
    send_message(vk_session, peer_id, market_text)
    
    from after_commands import after_manager
    after_manager.add_command(event.user_id, "market.category")
    return True


def handle_category_cmd(event, vk_session, peer_id, state):
    print(f"🔍 handle_category_cmd: '{event.text}'")
    text = event.text.lower().strip()
    
    if text not in CATEGORIES:
        send_message(vk_session, peer_id, "❓ Категории: холодное, огнестрельное, вспомогательное")
        return True
    
    category = CATEGORIES[text]
    subcats = SUBCATEGORIES.get(category, [])
    
    if not subcats:
        items = dm.get_items_by_category(category)
        resp_text = f"📂 {category}\n\n"
        for item in items[:10]:
            resp_text += format_item_short(item) + "\n\n"
        resp_text += "ℹ️ описание #артикул"
        send_message(vk_session, peer_id, resp_text)
        return True
    
    subcats_text = f"📂 {category}\n\n"
    for i, subcat in enumerate(subcats, 1):
        subcats_text += f"{i}. {subcat}\n"
    subcats_text += "\nℹ️ Введите номер:"
    send_message(vk_session, peer_id, subcats_text)
    
    from after_commands import after_manager
    after_manager.add_command(event.user_id, "market.subcategory", {"category": category})
    return True


def handle_subcategory_cmd(event, vk_session, peer_id, state):
    print(f"🔍 handle_subcategory_cmd: '{event.text}'")
    try:
        subcat_num = int(event.text.strip())
    except ValueError:
        send_message(vk_session, peer_id, "❓ Введите номер")
        return True
    
    category = state.data.get("category")
    subcats = SUBCATEGORIES.get(category, [])
    
    if not (1 <= subcat_num <= len(subcats)):
        send_message(vk_session, peer_id, f"❓ 1-{len(subcats)}")
        return True
    
    subcat = subcats[subcat_num - 1]
    items = filter_items_by_subcategory(category, subcat)
    
    text = f"📦 {subcat}\n\n"
    for item in items[:10]:
        text += format_item_short(item) + "\n\n"
    text += "ℹ️ описание #артикул"
    send_message(vk_session, peer_id, text)
    return True


# ✅ НОВЫЙ ФОРМАТ - Словарь для автозагрузки AfterCommandManager
after_handlers = {
    "market.category": handle_category_cmd,
    "market.subcategory": handle_subcategory_cmd
}

# Остальные функции без изменений
def description_command(event, vk_session, peer_id):
    parts = event.text.lower().split()
    if len(parts) < 1 or not parts[0].startswith('#'):
        send_message(vk_session, peer_id, "❓ описание #артикул")
        return False
    
    identifier = parts[0][1:]
    item = dm.get_item(identifier)
    
    if not item:
        send_message(vk_session, peer_id, "❌ Не найден")
        return True
    
    desc = format_item_description(item)
    send_message(vk_session, peer_id, desc)
    return True

def format_item_short(item: Item) -> str:
    first = f"#{item.identifier} {item.name} - {item.cost}¥"
    stats = []
    if item.damage: stats.append(f"Урон:{item.damage}")
    if item.protection: stats.append(f"Защ:{item.protection}")
    if item.penetration: stats.append(f"Пр:{item.penetration}")
    if item.damage_reduction: stats.append(f"Сниж:{item.damage_reduction}")
    if item.recovery: stats.append(f"Восст:{item.recovery}")
    second = " | ".join(stats)
    return f"{first}\n{second}" if stats else first

def format_item_description(item: Item) -> str:
    parts = [f"**{item.name}** [{item.category}]", f"💰 {item.cost}¥"]
    if item.damage: parts.append(f"⚔️ Урон: {item.damage}")
    if item.protection: parts.append(f"🛡️ Защита: {item.protection}")
    if item.penetration: parts.append(f"💥 Пр: {item.penetration}")
    if item.damage_reduction: parts.append(f"🩸 Снижение: {item.damage_reduction}")
    if item.recovery: parts.append(f"🔄 Восст: {item.recovery}")
    return "\n".join(parts)

def filter_items_by_subcategory(category: str, subcat: str) -> List[Item]:
    items = dm.get_items_by_category(category)
    return [item for item in items if re.search(rf'\[{re.escape(subcat)}\]', item.name)]