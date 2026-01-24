from common_utils import send_message, get_current_time
from storege.data_manager import dm
from storege.databases.items_db import Item
from storege.databases.character_db import Character


def hi_command(event, vk_session, peer_id):
    send_message(vk_session, peer_id, "Хули ты на меня орёшь, блять?! Ты на ебало моё посмотри! Оно, блять, тупое, а не глухое нахрен!")


def time_command(event, vk_session, peer_id):
    send_message(vk_session, peer_id, f"⏰ Time on Host-server now: {get_current_time()}")

CATEGORIES = {
    "cold": "Холодное оружие",
    "fire": "Огнестрельное оружие", 
    "useless": "Вспомогательное снаряжение"
}

def market_command(event, vk_session, peer_id):
    market_text = """🏪 Маркет

🔪 Холодное оружие (market холодное)
🔫 Огнестрельное оружие (market огнестрельное) 
🛡️ Вспомогательное снаряжение (market вспомогательное)"""
    send_message(vk_session, peer_id, market_text)

def category_command(event, vk_session, peer_id):
    parts = event.text.lower().split()
    if len(parts) < 2:
        send_message(vk_session, peer_id, "❓ market <категория>")
        return
    
    category_key = parts[1]
    if category_key not in CATEGORIES:
        send_message(vk_session, peer_id, "❓ Категории: холодное, огнестрельное, вспомогательное")
        return
    
    category = CATEGORIES[category_key]
    items = dm.get_items_by_category(category)
    
    if not items:
        send_message(vk_session, peer_id, f"📂 {category}\n\nПусто")
        return
    
    text = f"📂 {category}\n\n"
    for item in items:
        text += f"#{item.identifier}: {item.name} - {item.cost}¥\n"
    text += "\nℹ️ описание #артикул"
    send_message(vk_session, peer_id, text)

def description_command(event, vk_session, peer_id):
    parts = event.text.lower().split()
    if len(parts) < 2 or not parts[1].startswith('#'):
        send_message(vk_session, peer_id, "❓ описание #артикул")
        return
    
    identifier = parts[1][1:]  # Убираем #
    item = dm.get_item(identifier)
    
    if not item:
        send_message(vk_session, peer_id, "❌ Предмет не найден")
        return
    
    # Формируем описание без служебных полей
    desc_parts = [
        f"**{item.name}** [{item.category}]",
        f"💰 Цена: {item.cost}¥",
        f"⚔️ Урон: {item.damage}" if item.damage else None,
        f"🛡️ Защита: {item.protection}" if item.protection else None,
        f"💥 Пробитие: {item.penetration}" if item.penetration else None,
        f"🩸 Снижение урона: {item.damage_reduction}" if item.damage_reduction else None,
        f"🔄 Восстановление: {item.recovery}" if item.recovery else None,
        "🔥 Одноразовый" if item.is_consumable else None
    ]
    
    desc = "\n".join(p for p in desc_parts if p)
    send_message(vk_session, peer_id, desc)

def inventory_command(event, vk_session, peer_id):
    character = dm.get_or_create_character(event.user_id, f"User{event.user_id}")
    
    if not character.inventory_items:
        send_message(vk_session, peer_id, "🎒 Инвентарь пуст")
        return
    
    inv_text = "🎒 Инвентарь:\n"
    for identifier in character.inventory_items:
        item = dm.get_item(identifier)
        if item:
            stats = []
            if item.damage: stats.append(f"Урон:{item.damage}")
            if item.damage_reduction: stats.append(f"Снижение:{item.damage_reduction}")
            if item.protection: stats.append(f"Защита:{item.protection}")
            if item.penetration: stats.append(f"Пробитие:{item.penetration}")
            if item.recovery: stats.append(f"Восст:{item.recovery}")
            
            inv_text += f"#{item.identifier} {item.name}"
            if stats:
                inv_text += f" ({', '.join(stats)})"
            inv_text += "\n"
    
    inv_text += f"\n💰 Йен: {character.yen}"
    send_message(vk_session, peer_id, inv_text)

# Обновляем словарь команд
USER_COMMANDS = {
    "РАБОТАЙ": hi_command,
    "time": time_command, 
    "market": market_command,
    "inventory": inventory_command, 
    "описание": description_command
}

# Добавляем обработку категорий в основной хэндлер команд
def handle_market_category(text: str) -> str:
    parts = text.lower().split()
    if len(parts) > 1 and parts[0] == "market" and parts[1] in CATEGORIES:
        return "category"
    return None