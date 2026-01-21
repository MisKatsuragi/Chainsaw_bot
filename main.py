import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sys
import os
import time
from common_utils import send_message, is_admin, get_peer_id
from storege.data_manager import dm # ✅ Глобальный dm
from user_commands import USER_COMMANDS
from data_commands import DATA_COMMANDS
from admin_commands import ADMIN_COMMANDS, handle_data_command
from god_commands import GOD_COMMANDS
from config import VK_TOKEN, HOST

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkLongPoll(vk_session)
admins = dm.admins
god = dm.god 
itsMe = True

def handle_message(event):
    msg = event.text.lower().strip()
    user_id = event.user_id
    peer_id = get_peer_id(event)  # ← Универсальная функция
    
    print(f"💬 {user_id} в {peer_id}: {msg}")
    
    # 1. /god команда
    if msg == "/god":
        ADMIN_COMMANDS["/god"](event, vk_session, admins, peer_id, god)
        return
    
    # Проверяем DATA_COMMANDS
    if msg in DATA_COMMANDS:
        handle_data_command(event, vk_session, admins, peer_id)
        return
    
    # 2. Админ команды
    if msg.startswith('/') and is_admin(user_id, admins):
        cmd = msg.split()[0]
        if cmd in GOD_COMMANDS:
            GOD_COMMANDS[cmd](event, vk_session, admins, peer_id, god)
        elif cmd in ADMIN_COMMANDS:
            ADMIN_COMMANDS[cmd](event, vk_session, admins, peer_id)
        else:
            send_message(vk_session, peer_id, "❓")
        return
    
    # 3. Пользовательские команды
    for cmd, func in USER_COMMANDS.items():
        if msg.startswith(cmd + ' ') or msg == cmd:
            func(event, vk_session, admins, peer_id)
            return

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if itsMe:
                    user_id = event.user_id
                    peer_id = get_peer_id(event)
                    send_message(vk_session, peer_id, f"Host: {HOST}")
                    handle_message(event)
                    itsMe=False
                else:
                    handle_message(event)
    except Exception as e:
        print(f"❌ {e}. Переподключение...")
        time.sleep(5)