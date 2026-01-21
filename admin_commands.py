import sys
from common_utils import send_message, is_admin, parse_target_user, get_user_link
from config import HOST
from storege.data_manager import dm  # ✅ Правильный импорт
from data_commands import DATA_COMMANDS


# Назначение первого админа, в соответствии с законом робототехники 
# Человек всегда должен быть главнее машины
def make_god(event, vk_session, admins, peer_id, god):
    user_id = event.user_id

    if user_id in god:
        send_message(vk_session, peer_id, "❌ Таблетки прими!")
        return
    if admins:
        send_message(vk_session, peer_id, "❌ Ишь самозванец!")
        return
    admins.add(user_id)
    god.add(user_id)
    dm.db.admins.add(user_id)  # ✅ Сохраняем в БД
    dm.db.god.add(user_id)     # ✅ Сохраняем в БД
    dm.set_user_position(user_id, "god")  # ✅ Сохраняем позицию
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
    stats = dm.get_stats()  # ✅ Используем dm.get_stats()
    god_id = list(dm.god)[0] if dm.god else None
    god_link = get_user_link(god_id)
    send_message(vk_session, peer_id, 
        f"Host: {HOST}\n"
        f"👑 **Бог**: {god_link}\n"
        f"👥 Админов: {len(admins)}\n"
        f"👤 Пользователей: {stats['users_count']}\n"  # ✅ dm.users
        f"🛒 Рынок: {stats['market_count']}\n"          # ✅ dm.market_items
        f"💰 Общий баланс: {stats['total_received']:,}")


def handle_data_command(event, vk_session, admins, peer_id):
    """Обработчик команд DATA_COMMANDS"""
    if not is_admin(event.user_id, admins):
        return
    
    command = event.text.split()[0]
    if command in DATA_COMMANDS:
        result = DATA_COMMANDS[command]()
        send_message(vk_session, peer_id, result)


# Дать пользователю денег
def give_command(event, vk_session, admins, peer_id):
    if not is_admin(event.user_id, admins):
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        target_link = get_user_link(target_id)
        parts = text.split()
        coins = int(parts[-1])
        
        user = dm.get_user(target_id)  # ✅ dm.get_user
        user.coins += coins
        user.stats.total_received += coins  # ✅ Обновляем статистику
        send_message(vk_session, peer_id, f"✅ +{coins} монет пользователю {target_link}")
        # ✅ Отмечаем изменения для сохранения
        dm.mark_dirty()
    except:
        send_message(vk_session, peer_id, "❓ /give [ссылка] 100")


# Забрать у пользователя деньги
def pick_command(event, vk_session, admins, peer_id):
    if not is_admin(event.user_id, admins):
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        target_link = get_user_link(target_id)
        parts = text.split()
        coins = int(parts[-1])
        
        user = dm.get_user(target_id)  # ✅ dm.get_user
        if user.coins >= coins:
            user.coins -= coins
            send_message(vk_session, peer_id, f"✅ -{coins} монет у пользователя {target_link}")
            # ✅ Отмечаем изменения для сохранения
            dm.mark_dirty()
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
        index = dm.add_market_item(name, cost, desc)  # ✅ dm.add_market_item
        send_message(vk_session, peer_id, f"✅ #{index}: {name} добавлен!")
    except:
        send_message(vk_session, peer_id, "❓ /additem <name> <cost> <desc>")


ADMIN_COMMANDS = {
    "/god": make_god, 
    "/status": status_command,
    "/give": give_command, 
    "/pick": pick_command,
    "/additem": additem_command,
    "/shutdown": shut_down,
}