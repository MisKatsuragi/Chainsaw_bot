from common_utils import send_message, get_current_time
from handlers.market import market_command
from storege.data_manager import dm
from storege.databases.items_db import Item
from storege.databases.character_db import Character


def hi_command(event, vk_session, peer_id):
    send_message(vk_session, peer_id, "Хули ты на меня орёшь, блять?! Ты на ебало моё посмотри! Оно, блять, тупое, а не глухое нахрен!")


def time_command(event, vk_session, peer_id):
    send_message(vk_session, peer_id, f"⏰ Time on Host-server now: {get_current_time()}")

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
}