import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import time
from common_utils import send_message, is_admin, get_peer_id
from user_commands import USER_COMMANDS
from admin_commands import ADMIN_COMMANDS
from database import db
from config import VK_TOKEN, HOST

vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkLongPoll(vk_session)
admins = set()
itsMe = True

def handle_message(event):
    msg = event.text.lower().strip()
    user_id = event.user_id
    peer_id = get_peer_id(event)  # ← Универсальная функция
    
    print(f"💬 {user_id} в {peer_id}: {msg}")
    
    # 1. /god команда
    if msg == "/god":
        ADMIN_COMMANDS["/god"](event, vk_session, admins, peer_id)
        return
    
    # 2. Админ команды
    if msg.startswith('/') and is_admin(user_id, admins):
        cmd = msg.split()[0]
        if cmd in ADMIN_COMMANDS:
            ADMIN_COMMANDS[cmd](event, vk_session, admins, peer_id)
        else:
            send_message(vk_session, peer_id, "❓")
        return
    
    # 3. Пользовательские команды
    for cmd, func in USER_COMMANDS.items():
        if msg.startswith(cmd + ' ') or msg == cmd:
            func(event, vk_session, admins, peer_id)
            return

print("🚀 Бот запущен! ")
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