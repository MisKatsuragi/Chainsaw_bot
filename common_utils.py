import random
import time
import re
from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
from storege.data_manager import dm
from storege.databases.items_db import Item

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

def format_item_short(item: Item) -> str:
    """Короткое описание предмета для списков"""
    lines = [f"#{item.identifier} {item.name}"]
    lines.append(f"💰 {item.cost}¥")
    
    stats = []
    if item.damage: stats.append(f"Урон:{item.damage}")
    if item.penetration: stats.append(f"Проникновение:{item.penetration}")
    if item.protection: stats.append(f"Защита:{item.protection}")
    if item.damage_reduction: stats.append(f"Снижение урона:{item.damage_reduction}")
    if item.recovery: stats.append(f"Лечение:{item.recovery}")
    if item.overflow: stats.append(f"Оверхил:{item.overflow}")
    if item.usecondition: stats.append(f"Условия использования:{item.usecondition}")
    
    if stats:
        lines.append("|".join(stats))
    
    if item.used_player_stats:
        lines.append(f"⚡ {', '.join(item.used_player_stats)}")
    
    return "\n".join(lines)


def format_item_full(item: Item) -> str:
    """Полное описание предмета"""
    text = f"📦 {item.name}\n"
    text += f"🏷️ #{item.identifier} | 💰 {item.cost}¥\n"
    text += f"📂 {item.category}\n\n"
    
    stats = []
    if item.damage: stats.append(f"⚔️ Урон: {item.damage}")
    if item.penetration: stats.append(f"💥 Проникновение: {item.penetration}")
    if item.protection: stats.append(f"🛡️ Защита: {item.protection}")
    if item.damage_reduction: stats.append(f"🛡️ Снижение урона: {item.damage_reduction}")
    if item.recovery: stats.append(f"💉 Лечение: {item.recovery}")
    if item.overflow: stats.append(f"💥 Оверхил: {item.overflow}")
    if item.usecondition: stats.append(f"🔧 Условия использования: {item.usecondition}")
    
    if stats:
        text += "📊 Статы:\n" + "\n".join(stats) + "\n\n"
    
    if item.used_player_stats:
        text += f"⚡ Требует: {', '.join(item.used_player_stats)}\n\n"
    
    if item.max_player_stats:
        text += "📏 Макс статы:\n" + "\n".join([f"• {k}: {v}" for k,v in item.max_player_stats.items()]) + "\n\n"
    
    if item.description:
        text += f"📝 {item.description}\n\n"
    
    text += "🛒 купить #артикул"
    return text