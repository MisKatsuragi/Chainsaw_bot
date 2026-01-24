import sys
from common_utils import send_message, parse_target_user, get_user_link
from config import HOST
from storege.data_manager import dm 
from data_commands import DATA_COMMANDS


# Назначение первого админа, в соответствии с законом робототехники 
# Человек всегда должен быть главнее машины
def make_god(event, vk_session, peer_id):
    user_id = event.user_id

    if dm.is_god(user_id):
        send_message(vk_session, peer_id, "❌ Таблетки прими!")
        return
    if dm.is_admin(user_id):
        send_message(vk_session, peer_id, "❌ Ишь самозванец!")
        return
    dm.roles_db.add_god(user_id)
    dm.roles_db.add_admin(user_id)
    user_link = get_user_link(user_id)
    send_message(vk_session, peer_id, f"✅ {user_link} = GOD!")
    print(f"Создатель: {user_id}")


# Выключение бота на хосте
def shut_down(event, vk_session, peer_id):
    if not dm.is_god(event.user_id):
        send_message(vk_session, peer_id, "Ты шо охуел?")
        return
    send_message(vk_session, peer_id, "Бот выключен")
    sys.exit(0)


# Общие данные о беседе
def status_command(event, vk_session, peer_id):
    god_id = list(dm.god)[0] if dm.god else None
    god_link = get_user_link(god_id) if god_id else "Не назначен"
    characters_count = len(dm.characters_db.characters)
    market_items_count = len(dm.items_db.items)
    send_message(vk_session, peer_id, 
        f"Host: {HOST}\n"
        f"👑 **Бог**: {god_link}\n"
        f"👥 Админов: {len(dm.admins)}\n"
        f"👤 Персонажей: {characters_count}\n"
        f"🛒 Рынок: {market_items_count}\n"
        f"💰 Йен в игре: {sum(c.yen for c in dm.characters_db.characters.values())}")



def handle_data_command(event, vk_session, peer_id):
    """Обработчик команд DATA_COMMANDS"""
    if not dm.is_admin(event.user_id) and not dm.is_god(event.user_id): 
        return
    
    command = event.text.split()[0]
    if command in DATA_COMMANDS:
        result = DATA_COMMANDS[command]()
        send_message(vk_session, peer_id, result)


# Дать йен персонажу
def give_command(event, vk_session, peer_id):
    if not dm.is_admin(event.user_id):
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        target_link = get_user_link(target_id)
        parts = text.split()
        yen = int(parts[-1])
        character = dm.get_or_create_character(target_id, f"User{target_id}")
        character.yen += yen
        
        send_message(vk_session, peer_id, f"✅ +{yen}¥ персонажу {target_link}")
        print(f"Админ выдал {yen}¥ пользователю {target_id}")
    except:
        send_message(vk_session, peer_id, "❓ /give [ссылка] 100")


# Забрать йен у персонажа
def pick_command(event, vk_session, peer_id):
    if not dm.is_admin(event.user_id): 
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        target_link = get_user_link(target_id)
        parts = text.split()
        yen = int(parts[-1])
        
        character = dm.get_or_create_character(target_id, f"User{target_id}")
        if character.yen >= yen:
            character.yen -= yen
            send_message(vk_session, peer_id, f"✅ -{yen}¥ у персонажа {target_link}")
        else:
            send_message(vk_session, peer_id, f"❌ У персонажа только {character.yen}¥")
    except:
        send_message(vk_session, peer_id, "❓ /pick [ссылка] 100")


# Добавить предмет на рынок
def additem_command(event, vk_session, peer_id):
    if not dm.is_admin(event.user_id): 
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        parts = event.text.split(maxsplit=3)
        if len(parts) < 4:
            send_message(vk_session, peer_id, "❓ /additem <name> <cost> <category> <desc>")
            return
            
        name, cost, category, desc = parts[1], int(parts[2]), parts[3], parts[4]
        
        from storege.databases.items_db import Item
        item = Item(
            identifier=f"{name[:3].upper()}{len(dm.items_db.items)+1}",
            name=name,
            category=category,
            cost=cost
        )
        
        if dm.add_market_item(item):
            send_message(vk_session, peer_id, f"✅ #{item.identifier}: {name} добавлен!")
        else:
            send_message(vk_session, peer_id, "❌ Предмет уже существует")
    except Exception as e:
        send_message(vk_session, peer_id, f"❌ Ошибка: {e}")


ADMIN_COMMANDS = {
    "/god": make_god, 
    "/status": status_command,
    "/give": give_command, 
    "/pick": pick_command,
    "/additem": additem_command,
    "/shutdown": shut_down,
}