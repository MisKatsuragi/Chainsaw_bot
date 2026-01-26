from common_utils import send_message
from storege.data_manager import dm
from storege.databases.character_db import Character
from vk_api import VkApi

def character_profile_command(event, vk_session, peer_id):
    """Показать профиль персонажа"""
    character = dm.characters_db.get_character(event.user_id)
    if not character:
        send_message(vk_session, peer_id, "❌ Профиль не найден. Создайте его командой 'createprofile'")
        return
    
    profile_text = f"👤 **Профиль персонажа**\n\n"
    profile_text += f"🆔 ID: {character.user_id}\n"
    profile_text += f"👤 Имя: {character.name}\n"
    profile_text += f"⭐ Ранг: {character.rank}\n"
    profile_text += f"⚡ Уровень: {character.level}\n"
    profile_text += f"🏛️ Фракция: {character.faction}\n"
    profile_text += f"🎭 Класс: {character.char_class}\n"
    profile_text += f"🔗 Профиль: {character.profile_link}\n\n"
    
    # Характеристики с эмодзи
    profile_text += "📊 **Характеристики:**\n"
    profile_text += f"❤️ Здоровье: {'❤️' * character.toughness}\n"
    profile_text += f"💪 Сила: {'💪' * character.strength}\n"
    profile_text += f"⚡ Рефлексы: {'⚡' * character.reflexes}\n"
    profile_text += f"👁️ Восприятие: {'👁️' * character.perception}\n"
    profile_text += f"🧠 Интеллект: {'🧠' * character.intellect}\n"
    profile_text += f"🗣️ Харизма: {'🗣️' * character.charisma}\n"
    profile_text += f"🍀 Удача: {'🍀' * character.luck}\n\n"
    
    profile_text += f"💰 Йен: {character.yen}\n"
    profile_text += f"👹 Частицы плоти: {character.flesh_particles}/{character.total_flesh_particles}\n"
    profile_text += f"📝 Описание: {character.self_description or 'Не указано'}\n"
    
    send_message(vk_session, peer_id, profile_text)

def create_profile_command(event, vk_session, peer_id):
    """Создать профиль через дефолтную инициализацию базы данных"""
    # Проверяем, существует ли уже персонаж
    if dm.characters_db.get_character(event.user_id):
        send_message(vk_session, peer_id, "❌ Профиль уже существует! Используйте 'profile' для просмотра.")
        return
    
    # Получаем имя пользователя из VK
    try:
        user_info = vk_session.method("users.get", {"user_ids": event.user_id})[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
    except:
        user_name = f"User{event.user_id}"
    
    # Используем метод create_or_get_character из базы - он создаст с дефолтными значениями
    # Затем перезаписываем нужные дефолтные значения для нового персонажа
    character = dm.characters_db.create_or_get_character(event.user_id, user_name)
    
    # Устанавливаем дефолтные значения для нового персонажа
    if len(character.inventory_items) == 0:  # Если это действительно новый персонаж
        character.rank = "Новичок"
        character.level = 1
        character.yen = 500
        character.toughness = 10  # 10 сердечек здоровья
        character.strength = 5
        character.reflexes = 5
        character.perception = 5
        character.intellect = 5
        character.charisma = 5
        character.luck = 5
        character.flesh_particles = 0
        character.total_flesh_particles = 0
        
        dm.characters_db.save_character(character)
        
        send_message(vk_session, peer_id, 
            f"✅ **Профиль создан!**\n"
            f"👤 Имя: {user_name}\n"
            f"⭐ Ранг: Новичок\n"
            f"⚡ Уровень: 1\n"
            f"💰 Йен: 500\n"
            f"❤️ Здоровье: {'❤️' * 10}\n"
            f"📝 Используйте 'profile' для просмотра!")
    else:
        send_message(vk_session, peer_id, "✅ Профиль уже готов к использованию!")

def change_name_command(event, vk_session, peer_id):
    """Начать изменение имени"""
    character = dm.characters_db.get_character(event.user_id)
    if not character:
        send_message(vk_session, peer_id, "❌ Сначала создайте профиль командой 'createprofile'")
        return
    
    send_message(vk_session, peer_id, "✏️ **Введите новое имя персонажа:**")

def change_faction_command(event, vk_session, peer_id):
    """Начать изменение фракции"""
    character = dm.characters_db.get_character(event.user_id)
    if not character:
        send_message(vk_session, peer_id, "❌ Сначала создайте профиль командой 'createprofile'")
        return
    
    send_message(vk_session, peer_id, "🏛️ **Введите название фракции:**")

def change_description_command(event, vk_session, peer_id):
    """Начать изменение описания"""
    character = dm.characters_db.get_character(event.user_id)
    if not character:
        send_message(vk_session, peer_id, "❌ Сначала создайте профиль командой 'createprofile'")
        return
    
    send_message(vk_session, peer_id, "📝 **Введите новое описание о себе:**")