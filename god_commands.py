import sys
import os
import time
import shutil
from common_utils import send_message, parse_target_user, get_user_link, is_god
from data_manager import dm

# Назначение пользователя админом
def promote_to_admin(event, vk_session, admins, peer_id, god):
    if not is_god(event.user_id, god):
        send_message(vk_session, peer_id, "❌ Только Бог!")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        
        if target_id in admins:
            send_message(vk_session, peer_id, "❌ Пользователь уже админ!")
            return
            
        admins.add(target_id)
        user_link = get_user_link(target_id)
        send_message(vk_session, peer_id, f"✅ {user_link} назначен админом Богом!")
        print(f"Бог {event.user_id} назначил админом: {target_id}")
        
    except:
        send_message(vk_session, peer_id, "❓ /godadmin [ссылка/@username/id]")

# Снятие пользователя с админской должности
def demote_admin(event, vk_session, admins, peer_id, god):
    if not is_god(event.user_id, god):
        send_message(vk_session, peer_id, "❌ Только Бог!")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        
        if target_id not in admins:
            send_message(vk_session, peer_id, "❌ Пользователь не админ!")
            return
            
        admins.remove(target_id)
        user_link = get_user_link(target_id)
        send_message(vk_session, peer_id, f"✅ {user_link} разжалован с админа!")
        print(f"Бог {event.user_id} разжаловал: {target_id}")
        
    except:
        send_message(vk_session, peer_id, "❓ /godunadmin [ссылка/@username/id]")

# Рахжаловать всех админов
def demote_all_admins(event, vk_session, admins, peer_id, god):
    if not is_god(event.user_id, god):
        send_message(vk_session, peer_id, "❌ Только Бог!")
        return
    
    admin_count = len(admins)
    admins.clear()
    send_message(vk_session, peer_id, f"✅ Разжалованы все {admin_count} админов!")
    print(f"Бог {event.user_id} разжаловал всех админов")

# Передать роль бога другому пользоватаелю
def transfer_god(event, vk_session, admins, peer_id, god):
    if not is_god(event.user_id, god):
        send_message(vk_session, peer_id, "❌ Только Бог!")
        return
    
    try:
        text = event.text
        new_god_id = parse_target_user(text, event)
        
        if new_god_id == list(god)[0]:
            send_message(vk_session, peer_id, "❌ Помахал короной!")
            return
        
        old_god_id = list(god)[0]  # получаем текущего бога
        old_god_link = get_user_link(old_god_id)
        new_god_link = get_user_link(new_god_id)
        god.clear()
        god.add(new_god_id)
        
        god = new_god_id
        send_message(vk_session, peer_id, 
                    f"👑 {old_god_link} передал власть Богу!\n"
                    f"👑 Новый Бог: {new_god_link}")
        print(f"Власть передана {event.user_id} к {new_god_id}")
        
    except:
        send_message(vk_session, peer_id, "❓ /youGod [ссылка/@username/id]")

    # Сброс ВСЕЙ конфигурации в изначальное состояние
def reset_all_command(event, vk_session, admins, peer_id, god):
    user_id = event.user_id
    
    if not is_god(user_id, god):
        send_message(vk_session, peer_id, "❌ Только Бог может уничтожить мир!")
        return
    
    user_link = get_user_link(user_id)
    
    try:
        # ✅ 1. Создаем бэкап текущих данных
        backup_name = f"backup_{int(time.time())}.json"
        shutil.copy2("database.json", backup_name)
        
        # ✅ 2. Полный сброс базы данных
        db = dm.db
        db.users.clear()
        db.market_items.clear()
        db.market_index = 1
        db.user_next_index.clear()
        db.admins.clear()
        db.god.clear()
        
        # ✅ 3. Восстанавливаем Бога
        # db.admins.add(user_id)
        # db.god.add(user_id)
        # db.set_user_position(user_id, "god")
        
        # ✅ 4. Переинициализируем рынок
        db.init_market()
        
        # ✅ 5. Принудительное сохранение
        dm.mark_dirty()
        dm.save_to_file()
        
        message = (f"💥 **МИР УНИЧТОЖЕН И ВОССТАНОВЛЕН**\n\n"
                  f"👑 Бог {user_link} сотворил новый мир!\n\n"
                  f"📊 **Состояние новой вселенной:**\n"
                  f"👤 Пользователей: 0\n"
                  f"🎒 Предметов на рынке: 3\n"
                  f"💰 Экономика: 0 монет\n"
                  f"📦 Бэкап: `{backup_name}`\n\n"
                  f"✨ Готово к новой игре!")
        
        send_message(vk_session, peer_id, message)
        print(f"🌍 Бог {user_id} сбросил мир. Бэкап: {backup_name}")
        
    except Exception as e:
        send_message(vk_session, peer_id, f"❌ Ошибка апокалипсиса: {str(e)}")
        print(f"Ошибка сброса: {e}")


# Словарь команд Бога
GOD_COMMANDS = {
    "/admin": promote_to_admin,
    "/unadmin": demote_admin,
    "/deleteall": demote_all_admins,
    "/yougod": transfer_god,
    "/resetall": reset_all_command 
}