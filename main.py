import os
import sys
import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from common_utils import send_message, get_peer_id
from storege.data_manager import dm
from after_commands import after_manager  # ✅ Импорт в начале
from user_commands import USER_COMMANDS
from data_commands import DATA_COMMANDS
from admin_commands import ADMIN_COMMANDS, handle_data_command
from god_commands import GOD_COMMANDS
from config import VK_TOKEN, HOST

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkLongPoll(vk_session)

itsMe = True


def handle_message(event):
    msg = event.text.strip()
    user_id = event.user_id
    peer_id = get_peer_id(event)
    
    print(f"💬 {user_id}: {msg}")
    print(f"🔍 after_handler.has_pending({user_id}): {after_manager.has_pending(user_id)}")
    
    # 1. Команда /god 
    if msg == "/god":
        ADMIN_COMMANDS["/god"](event, vk_session, peer_id)
        return
    
    # 2. DATA_COMMANDS
    if msg in DATA_COMMANDS:
        handle_data_command(event, vk_session, peer_id)
        return
    
    # 3. Админ команды (все /команды)
    if msg.startswith('/'):
        if dm.is_admin(user_id):
            cmd = msg.split()[0]
            if cmd in GOD_COMMANDS:
                GOD_COMMANDS[cmd](event, vk_session, peer_id)
            elif cmd in ADMIN_COMMANDS:
                ADMIN_COMMANDS[cmd](event, vk_session, peer_id)
            else:
                send_message(vk_session, peer_id, "❓ Неизвестная команда")
        else:
            send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    # 4. Пользовательские команды
    for cmd_name, func in USER_COMMANDS.items():
        if msg == cmd_name or msg.startswith(cmd_name + ' '):
            func(event, vk_session, peer_id)
            return
        
    # 5. AFTER_COMMANDS ПЕРЕХВАТ
    if after_manager.has_pending(user_id):  # ✅ Используем метод вместо глобального словаря
        print(f"🚀 AFTER_HANDLER для {user_id}")
        if after_manager.handle_after_command(event, vk_session, peer_id, {}):
            print("✅ AFTER_COMMAND обработан")
            return


print("🚀 Бот запущен!")
while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if itsMe:
                    user_id = event.user_id
                    peer_id = get_peer_id(event)
                    send_message(vk_session, peer_id, f"🤖 Chainsaw Bot v2.0 | Host: {HOST}")
                    itsMe = False
                
                handle_message(event)
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Ошибка: {e}. Переподключение через 5 сек...")
        time.sleep(5)