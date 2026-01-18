import random
import time
import re

def send_message(vk_session, peer_id, message):
    vk_session.method("messages.send", {
        "peer_id": peer_id,
        "message": message,
        "random_id": random.randint(1, 1000000)
    })

def get_current_time():
    return time.strftime('%H:%M:%S')

def is_admin(user_id, admins):
    return user_id in admins

def get_user_link(user_id, vk_session=None, name=None):
    """Создает кликабельную ссылку @id"""
    if name:
        return f"[id{user_id}|{name}]"
    return f"@id{user_id}"

def get_peer_id(event):
    """Определяет peer_id для ЛС и чатов"""
    if event.chat_id:
        return 2000000000 + event.chat_id
    return event.user_id

def parse_target_user(text, event):
    # Проверяем reply (ответ на сообщение)
    if hasattr(event, 'fwd_messages') and event.fwd_messages:
        return event.fwd_messages[0]['from_id']
    elif hasattr(event, 'reply_message') and event.reply_message:
        return event.reply_message['from_id']
    
    # Ищем ссылки в тексте
    # id12345678 или [id12345678|имя]
    id_match = re.search(r'\[?id(\d+)(?:\|[^\]]*)?\]?', text)
    if id_match:
        return int(id_match.group(1))
    
    # vk.com/id12345678 или vk.com/name
    vk_match = re.search(r'vk\.com/(?:id)?(\d+)', text)
    if vk_match:
        return int(vk_match.group(1))
    
    # Если ничего не найдено, используем ID отправителя команды
    return event.user_id

def format_item(item):
    return f"{item.name} ({item.cost} монет) - {item.description}"