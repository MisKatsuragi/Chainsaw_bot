import re
from common_utils import send_message, get_current_time, format_item_short, format_item_full
from handlers.market import market_command
from handlers.character_handler import change_name_command, change_description_command, create_profile_command, character_profile_command
from storege.data_manager import dm
from storege.databases.items_db import Item
from storege.databases.character_db import Character
from vk_api import VkApi


def hi_command(event, vk_session, peer_id):
    send_message(vk_session, peer_id, "Хули ты на меня орёшь, блять?! Ты на ебало моё посмотри! Оно, блять, тупое, а не глухое нахрен!")


def time_command(event, vk_session, peer_id):
    send_message(vk_session, peer_id, f"⏰ Time on Host-server now: {get_current_time()}")


def inventory_command(event, vk_session, peer_id):
    """🎒 Показать инвентарь - аналогично магазину"""
    character = dm.get_or_create_character(event.user_id, f"User{event.user_id}")
    
    if not character.inventory_items:
        send_message(vk_session, peer_id, "🎒 Инвентарь пуст")
        return
    
    inv_text = "🎒 **ВАШ ИНВЕНТАРЬ:**\n\n"
    for identifier in character.inventory_items:
        item = dm.get_item(identifier)
        if item:
            inv_text += format_item_short(item) + "\n\n"
    
    inv_text += f"\n💰 Йен: {character.yen}"
    send_message(vk_session, peer_id, inv_text)


def describe_item_command(event, vk_session, peer_id):
    """Описание предмета #артикул"""
    text_lower = event.text.lower().strip()
    
    if not text_lower.startswith("описание"):
        return False
    
    match = re.search(r'#(\w+)', event.text)
    if not match:
        send_message(vk_session, peer_id, "❓ описание #артикул")
        return True
    
    identifier = match.group(1).upper()
    item = dm.get_item(identifier)
    
    print(f"🔍 Описание для #{identifier}")
    
    if item:
        send_message(vk_session, peer_id, format_item_full(item))
    else:
        send_message(vk_session, peer_id, f"❌ #{identifier} не найден")
    
    return True


# ✅ ИСПРАВЛЕННЫЙ словарь команд - БЕЗ конфликтов!
USER_COMMANDS = {
    "РАБОТАЙ": hi_command,
    "time": time_command, 
    "market": market_command,
    "bag": inventory_command,
    "инвентарь": inventory_command,
    "описание": describe_item_command, 
    
    # ✅ Профиль - ТОЛЬКО просмотр
    "profile": character_profile_command,
    "профиль": character_profile_command,
    
    # ✅ Создание профиля
    "createprofile": create_profile_command,
    "create профиль": create_profile_command,
    
    # ✅ Смена свойств - все с аргументами
    "changename": change_name_command,
    "сменаимени": change_name_command,
    "name": change_name_command,
    "имя": change_name_command,
    
    "changedesc": change_description_command,
    "about": change_description_command, 
}