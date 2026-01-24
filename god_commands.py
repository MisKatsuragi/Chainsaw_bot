import time
import shutil
from common_utils import send_message, parse_target_user, get_user_link
from storege.data_manager import dm  # ✅ Глобальный dm

# Назначение пользователя админом (только Бог)
def promote_to_admin(event, vk_session, peer_id):
    if not dm.is_god(event.user_id):  # ✅ Новый метод
        send_message(vk_session, peer_id, "❌ Только Бог!")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        
        if target_id in dm.admins:
            send_message(vk_session, peer_id, "❌ Пользователь уже админ!")
            return
            
        dm.add_admin(target_id)  # ✅ Новая база данных
        user_link = get_user_link(target_id)
        send_message(vk_session, peer_id, f"✅ {user_link} назначен админом Богом!")
        print(f"Бог {event.user_id} назначил админом: {target_id}")
        
    except:
        send_message(vk_session, peer_id, "❓ /godadmin [ссылка/@username/id]")

# Снятие пользователя с админской должности (только Бог)
def demote_admin(event, vk_session, peer_id):
    if not dm.is_god(event.user_id):  # ✅ Новый метод
        send_message(vk_session, peer_id, "❌ Только Бог!")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        
        if target_id not in dm.admins:
            send_message(vk_session, peer_id, "❌ Пользователь не админ!")
            return
            
        dm.roles_db.remove_admin(target_id)  # ✅ Новая база данных
        user_link = get_user_link(target_id)
        send_message(vk_session, peer_id, f"✅ {user_link} разжалован с админа!")
        print(f"Бог {event.user_id} разжаловал: {target_id}")
        
    except:
        send_message(vk_session, peer_id, "❓ /godunadmin [ссылка/@username/id]")

# Разжаловать всех админов (только Бог)
def demote_all_admins(event, vk_session, peer_id):
    if not dm.is_god(event.user_id):
        send_message(vk_session, peer_id, "❌ Только Бог!")
        return
    
    admin_count = len(dm.admins)
    dm.roles_db.admins.clear()  # ✅ Новая база данных
    dm.roles_db.save()
    send_message(vk_session, peer_id, f"✅ Разжалованы все {admin_count} админов!")
    print(f"Бог {event.user_id} разжаловал всех админов")

# Передать роль бога другому пользователю (только Бог)
def transfer_god(event, vk_session, peer_id):
    if not dm.is_god(event.user_id):
        send_message(vk_session, peer_id, "❌ Только Бог!")
        return
    
    try:
        text = event.text
        new_god_id = parse_target_user(text, event)
        
        if new_god_id == event.user_id:
            send_message(vk_session, peer_id, " Помахал короной!")
            return
            
        old_god_id = event.user_id
        old_god_link = get_user_link(old_god_id)
        new_god_link = get_user_link(new_god_id)
        
        # ✅ Новая база данных: удаляем старого бога, добавляем нового
        dm.roles_db.god.clear()
        dm.roles_db.god.add(new_god_id)
        dm.roles_db.save()
        
        send_message(vk_session, peer_id, 
                    f"👑 {old_god_link} передал власть Богу!\n"
                    f"👑 Новый Бог: {new_god_link}")
        print(f"Власть передана от {old_god_id} к {new_god_id}")
        
    except:
        send_message(vk_session, peer_id, "❓ /yougod [ссылка/@username/id]")

# Сброс ВСЕЙ конфигурации (только Бог)
def reset_all_command(event, vk_session, peer_id):
    user_id = event.user_id
    
    if not dm.is_god(user_id):
        send_message(vk_session, peer_id, "❌ Только Бог может уничтожить мир!")
        return
    
    user_link = get_user_link(user_id)
    
    try:
        # ✅ 1. Создаем бэкапы всех баз данных
        timestamp = int(time.time())
        backup_dir = dm.databases_dir / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        for db_file in ["items.json", "characters.json", "contracts.json", "roles.json"]:
            src = dm.databases_dir / db_file
            if src.exists():
                shutil.copy2(src, backup_dir / db_file)
        
        # ✅ 2. Полный сброс игровых данных
        dm.characters_db.characters.clear()
        dm.items_db.items.clear()
        dm.contracts_db.contracts.clear()
        
        # ✅ 3. Сброс ролей (кроме Бога)
        dm.roles_db.admins.clear()
        dm.roles_db.god = {user_id}  # Оставляем только Бога
        
        # ✅ 4. Принудительное сохранение
        dm.save_all()
        
        message = (f"💥 **МИР УНИЧТОЖЕН И ВОССТАНОВЛЕН**\n\n"
                  f"👑 Бог {user_link} сотворил новый мир!\n\n"
                  f"📊 **Состояние новой вселенной:**\n"
                  f"👤 Персонажей: 0\n"
                  f"🎒 Предметов на рынке: 0\n"
                  f"📜 Контрактов: 0\n"
                  f"👥 Админов: 0\n"
                  f"📦 Бэкап: `{backup_dir.name}`\n\n"
                  f"✨ Готово к новой игре!")
        
        send_message(vk_session, peer_id, message)
        print(f"🌍 Бог {user_id} сбросил мир. Бэкап: {backup_dir}")
        
    except Exception as e:
        send_message(vk_session, peer_id, f"❌ Ошибка апокалипсиса: {str(e)}")
        print(f"Ошибка сброса: {e}")

# Словарь команд Бога
GOD_COMMANDS = {
    "/admin": promote_to_admin,    # Назначить админа
    "/unadmin": demote_admin,      # Разжаловать админа  
    "/deleteall": demote_all_admins,  # Удалить всех админов
    "/yougod": transfer_god,          # Передать бога
    "/resetall": reset_all_command    # Полный сброс
}