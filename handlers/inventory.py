# handlers/inventory.py
import re
from common_utils import send_message, format_item_short, format_item_full
from storege.data_manager import dm

def buy_item_command(event, vk_session, peer_id):
    """🛒 Покупка предмета #артикул"""
    text = event.text.strip()
    match = re.search(r'#(\w+)', text)
    
    if not match:
        send_message(vk_session, peer_id, "❓ купить #артикул")
        return True
    
    identifier = match.group(1).upper()
    character = dm.get_or_create_character(event.user_id, f"User{event.user_id}")
    item = dm.get_item(identifier)
    
    if not item:
        send_message(vk_session, peer_id, f"❌ #{identifier} не найден")
        return True
    
    if identifier in character.inventory_items:
        send_message(vk_session, peer_id, f"❌ #{identifier} уже есть в инвентаре")
        return True
    
    if character.yen >= item.cost:
        # ✅ Реальная покупка
        character.yen -= item.cost
        character.inventory_items.add(identifier)
        dm.characters_db.save_character(character)
        
        send_message(vk_session, peer_id, 
            f"🛒 **ПОКУПКА УСПЕШНА**\n\n"
            f"✅ {item.name}\n"
            f"💰 Стоимость: {item.cost}¥\n"
            f"💳 Остаток: {character.yen}¥\n\n"
            f"📦 **Инвентарь обновлён**\n"
            f"{format_item_short(item)}")
        print(f"🛒 [{event.user_id}] Купил {item.name}")
    else:
        send_message(vk_session, peer_id, 
            f"❌ Недостаточно ¥\n"
            f"💰 Нужно: {item.cost}¥\n"
            f"💳 У вас: {character.yen}¥")
    return True


def sell_item_command(event, vk_session, peer_id):
    """💰 Продажа предмета #артикул"""
    text = event.text.strip()
    match = re.search(r'#(\w+)', text)
    
    if not match:
        send_message(vk_session, peer_id, "❓ продать #артикул")
        return True
    
    identifier = match.group(1).upper()
    character = dm.get_or_create_character(event.user_id, f"User{event.user_id}")
    
    if identifier not in character.inventory_items:
        send_message(vk_session, peer_id, f"❌ #{identifier} нет в инвентаре")
        return True
    
    item = dm.get_item(identifier)
    if not item:
        send_message(vk_session, peer_id, f"❌ #{identifier} не найден")
        return True
    
    sell_price = int(item.cost * 0.7)
    character.yen += sell_price
    character.inventory_items.remove(identifier)
    dm.characters_db.save_character(character)
    
    send_message(vk_session, peer_id,
        f"💰 **ПРОДАЖА УСПЕШНА**\n\n"
        f"✅ Продан {item.name}\n"
        f"💵 Выручка: {sell_price}¥\n"
        f"💳 Баланс: {character.yen}¥")
    print(f"💰 [{event.user_id}] Продал {item.name}")
    return True

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
    
    if item:
        send_message(vk_session, peer_id, format_item_full(item))
    else:
        send_message(vk_session, peer_id, f"❌ #{identifier} не найден")
    
    return True
