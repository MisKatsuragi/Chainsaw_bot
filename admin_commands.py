import sys
from common_utils import send_message, is_admin, parse_target_user, get_user_link
from config import HOST
from database import db

# Назначение первого админа, в соотвествии с законом робототехники 
# Человек всегда должен быть главнее машины
def make_god(event, vk_session, admins, peer_id):
    user_id = event.user_id
    if admins:
        send_message(vk_session, peer_id, "❌ You are NOT a God!")
        return
    admins.add(user_id)
    user_link = get_user_link(user_id)
    send_message(vk_session, peer_id, f"✅ {user_link} = GOD!")
    print(f"Создатель: {user_id}")

# Выключение бота на хосте
def shut_down(event, vk_session, admins, peer_id):
    if not is_admin(event.user_id, admins): 
        send_message(vk_session, peer_id, "Ты шо охуел?")
        return
    send_message(vk_session, peer_id, "Бот выключен")
    sys.exit(0)

# Общие данные о беседе
def status_command(event, vk_session, admins, peer_id):
    send_message(vk_session, peer_id, 
        f"Host: {HOST}\n"
        f"👥 Админов: {len(admins)}\n"
        f"👤 Пользователей: {len(db.users)}\n"
        f"🛒 Рынок: {len(db.market_items)}")

# Дать пользователю денёг
def give_command(event, vk_session, admins, peer_id):
    if not is_admin(event.user_id, admins):
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        parts = text.split()
        coins = int(parts[-1])
        
        db.get_user(target_id).coins += coins
        send_message(vk_session, peer_id, f"✅ +{coins} монет")
    except:
        send_message(vk_session, peer_id, "❓ /give [ссылка] 100")

# Забрать у пользователя денеги
def pick_command(event, vk_session, admins, peer_id):
    if not is_admin(event.user_id, admins):
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        parts = text.split()
        coins = int(parts[-1])
        
        user = db.get_user(target_id)
        if user.coins >= coins:
            user.coins -= coins
            send_message(vk_session, peer_id, f"✅ -{coins} монет у пользователя")
        else:
            send_message(vk_session, peer_id, f"❌ У пользователя только {user.coins}")
    except:
        send_message(vk_session, peer_id, "❓ /pick [ссылка] 100")

# Добавить новый предмет на рынок
def additem_command(event, vk_session, admins, peer_id):
    if not is_admin(event.user_id, admins):
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        parts = event.text.split(maxsplit=3)
        name, cost, desc = parts[1], int(parts[2]), parts[3]
        index = db.add_market_item(name, cost, desc)
        send_message(vk_session, peer_id, f"✅ #{index}: {name} добавлен!")
    except:
        send_message(vk_session, peer_id, "❓ /additem <name> <cost> <desc>")

ADMIN_COMMANDS = {
    "/god": make_god, "/status": status_command,
    "/give": give_command, "/pick": pick_command,
    "/additem": additem_command,
    "/shutdown": shut_down,
}