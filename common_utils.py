import random
import time
import re
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from storege.data_manager import dm

# BUFFERS - буферизация команд пользователей
USER_BUFFERS: Dict[int, dict] = {}
BUFFER_TIMEOUT = timedelta(minutes=3)  # 3 минуты на ввод команды

def send_message(vk_session, peer_id, message):
    """Универсальная отправка сообщений"""
    vk_session.method("messages.send", {
        "peer_id": peer_id,
        "message": message,
        "random_id": random.randint(1, 1000000)
    })

def get_current_time():
    """Текущее время в формате HH:MM:SS"""
    return time.strftime('%H:%M:%S')

def get_user_link(user_id: int, vk_session=None, name: str = None) -> str:
    """Создает кликабельную ссылку @id"""
    if name:
        return f"[id{user_id}|{name}]"
    return f"@id{user_id}"

def get_peer_id(event) -> int:
    """Определяет peer_id для ЛС и чатов"""
    if event.chat_id:
        return 2000000000 + event.chat_id
    return event.user_id

def parse_target_user(text: str, event) -> int:
    """Парсит ID пользователя из текста, reply, forward или упоминаний"""
    
    # 1. Reply/Forward (самый приоритетный)
    if hasattr(event, 'fwd_messages') and event.fwd_messages:
        return event.fwd_messages[0]['from_id']
    elif hasattr(event, 'reply_message') and event.reply_message:
        return event.reply_message['from_id']
    
    # 2. VK Mini Apps упоминания [id123456|Имя]
    id_match = re.search(r'\[id(\d+)(?:\|[^\]]*)?\]', text)
    if id_match:
        return int(id_match.group(1))
    
    # 3. @id123 (короткие упоминания)
    mention_match = re.search(r'@id(\d+)', text)
    if mention_match:
        return int(mention_match.group(1))
    
    # 4. vk.com/id123456 или vk.com/name
    vk_match = re.search(r'vk\.com/(?:id)?(\d+)', text)
    if vk_match:
        return int(vk_match.group(1))
    
    # 5. Просто цифры (ID в тексте)
    digits_match = re.search(r'(\d{8,})', text)  # VK ID обычно 8+ цифр
    if digits_match:
        return int(digits_match.group(1))
    
    # 6. ID отправителя команды
    return event.user_id

def format_character_stats(character):
    """Форматирует характеристики персонажа"""
    stats = []
    if character.toughness > 10: stats.append(f"Кр:{character.toughness}")
    if character.strength > 10: stats.append(f"С:{character.strength}")
    if character.reflexes > 10: stats.append(f"Р:{character.reflexes}")
    if character.perception > 10: stats.append(f"В:{character.perception}")
    return " ".join(stats) if stats else "Стандарт"

def format_item_short(item):
    """Краткое описание предмета"""
    stats = []
    if item.damage: stats.append(f"Урон:{item.damage}")
    if item.protection: stats.append(f"З:{item.protection}")
    if item.penetration: stats.append(f"Пр:{item.penetration}")
    if item.damage_reduction: stats.append(f"Сниж:{item.damage_reduction}")
    if item.recovery: stats.append(f"Восст:{item.recovery}")
    return f"{item.name} ({', '.join(stats)})" if stats else item.name

# ==================== БУФЕРИЗАЦИЯ КОМАНД ====================
def start_user_buffer(user_id: int, command_name: str, callback: Callable, timeout: Optional[timedelta] = None):
    """
    Запускает буфер для последовательного ввода команд
    
    Args:
        user_id: ID пользователя
        command_name: Название команды (для сообщений)
        callback: Функция обработки результата buffer_data
        timeout: Максимальное время ожидания (по умолчанию 3 мин)
    """
    if timeout is None:
        timeout = BUFFER_TIMEOUT
    
    USER_BUFFERS[user_id] = {
        'command': command_name,
        'callback': callback,
        'start_time': datetime.now(),
        'timeout': timeout,
        'steps': []
    }
    
    print(f"🟡 Buffer started for {user_id}: {command_name}")

def add_buffer_step(user_id: int, data: str):
    """Добавляет шаг в буфер пользователя"""
    if user_id not in USER_BUFFERS:
        return False
    
    buffer = USER_BUFFERS[user_id]
    
    # Проверяем таймаут
    if datetime.now() > buffer['start_time'] + buffer['timeout']:
        clear_user_buffer(user_id)
        return False
    
    buffer['steps'].append(data)
    print(f"📝 Buffer step for {user_id}: {data} (total: {len(buffer['steps'])})")
    return True

def get_user_buffer(user_id: int) -> Optional[dict]:
    """Получает буфер пользователя"""
    if user_id not in USER_BUFFERS:
        return None
    
    buffer = USER_BUFFERS[user_id]
    
    # Автоочистка по таймауту
    if datetime.now() > buffer['start_time'] + buffer['timeout']:
        clear_user_buffer(user_id)
        return None
    
    return buffer

def complete_user_buffer(user_id: int, vk_session, peer_id):
    """Завершает буфер и вызывает callback"""
    buffer = get_user_buffer(user_id)
    if not buffer:
        return False
    
    try:
        result = buffer['callback'](buffer['steps'])
        if result:
            send_message(vk_session, peer_id, result)
    except Exception as e:
        send_message(vk_session, peer_id, f"❌ Ошибка буфера: {e}")
    finally:
        clear_user_buffer(user_id)
    return True

def clear_user_buffer(user_id: int):
    """Очищает буфер пользователя"""
    if user_id in USER_BUFFERS:
        print(f"🟥 Buffer cleared for {user_id}: {USER_BUFFERS[user_id]['command']}")
        del USER_BUFFERS[user_id]

def has_active_buffer(user_id: int) -> bool:
    """Проверяет наличие активного буфера"""
    buffer = get_user_buffer(user_id)
    return buffer is not None

def cancel_user_buffer(user_id: int, vk_session, peer_id, reason: str = "отменено"):
    """Отменяет буфер пользователя"""
    if clear_user_buffer(user_id):
        send_message(vk_session, peer_id, f"❌ Ввод {reason}")
        return True
    return False