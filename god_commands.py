import sys
from common_utils import send_message, parse_target_user, get_user_link, is_god

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

# Словарь команд Бога
GOD_COMMANDS = {
    "/admin": promote_to_admin,
    "/unadmin": demote_admin,
    "/deleteall": demote_all_admins,
    "/yougod": transfer_god,
}