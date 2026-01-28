import re
from common_utils import send_message
from storege.data_manager import dm
from storege.databases.character_db import Character
from vk_api import VkApi


def character_profile_command(event, vk_session, peer_id):
    """👤 profile - Показать профиль персонажа"""
    character = dm.characters_db.get_character(event.user_id)
    if not character:
        send_message(vk_session, peer_id, "❌ Профиль не найден. Создайте его командой 'createprofile'")
        return
    
    profile_text = f"👤 **Профиль персонажа**\n\n"
    #profile_text += f"🆔 ID: {character.user_id}\n"
    profile_text += f"👤 Имя: {character.name}\n"
    profile_text += f"⭐ Ранг: {character.rank}\n"
    profile_text += f"⚡ Уровень: {character.level}\n"
    profile_text += f"🏛️ Фракция: {character.faction}\n"
    profile_text += f"🎭 Класс: {character.char_class}\n"
    profile_text += f"🔗 Профиль: {character.profile_link or 'Не указан'}\n\n"
    
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
    """Создать профиль"""
    if dm.characters_db.get_character(event.user_id):
        send_message(vk_session, peer_id, "❌ Профиль уже существует! Используйте 'profile' для просмотра.")
        return
    
    try:
        user_info = vk_session.method("users.get", {"user_ids": event.user_id})[0]
        user_name = f"{user_info['first_name']} {user_info['last_name']}"
    except:
        user_name = f"User{event.user_id}"
    
    character = dm.characters_db.create_or_get_character(event.user_id, user_name)
    
    if len(character.inventory_items) == 0:  # Новый персонаж
        character.rank = "Новичок"
        character.level = 1
        character.yen = 500
        character.toughness = 10
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


# ========== СМЕНА СТРОКОВЫХ ПОЛЕЙ ==========
def change_string_field(field_name, field_display, event, vk_session, peer_id):
    """Универсальная функция смены строковых полей"""
    character = dm.characters_db.get_character(event.user_id)
    if not character:
        send_message(vk_session, peer_id, "❌ Сначала создайте профиль командой 'createprofile'")
        return
    
    text_parts = event.text.strip().split(maxsplit=1)
    if len(text_parts) < 2:
        send_message(vk_session, peer_id, f"❓ **Формат:** {field_name} НовоеЗначение")
        return
    
    new_value = text_parts[1].strip()
    if not new_value:
        send_message(vk_session, peer_id, f"❌ {field_display} не может быть пустым!")
        return
    
    setattr(character, field_name, new_value)
    dm.characters_db.save_character(character)
    
    preview = new_value[:50] + "..." if len(new_value) > 50 else new_value
    send_message(vk_session, peer_id, f"✅ **{field_display} изменено!**\n{field_display} **{preview}**")


def change_name_command(event, vk_session, peer_id):
    """имя НовоеИмя"""
    change_string_field("name", "👤 Имя", event, vk_session, peer_id)


def change_faction_command(event, vk_session, peer_id):
    """фракция НазваниеФракции"""
    change_string_field("faction", "🏛️ Фракция", event, vk_session, peer_id)


def change_class_command(event, vk_session, peer_id):
    """класс НазваниеКласса"""
    change_string_field("char_class", "🎭 Класс", event, vk_session, peer_id)


def change_description_command(event, vk_session, peer_id):
    """changedesc Описание / осебе Описание"""
    change_string_field("self_description", "📝 Описание", event, vk_session, peer_id)


def change_profile_link_command(event, vk_session, peer_id):
    """профильссылка Ссылка"""
    change_string_field("profile_link", "🔗 Профиль", event, vk_session, peer_id)


def change_rank_command(event, vk_session, peer_id):
    """ранг НовыйРанг"""
    change_string_field("rank", "⭐ Ранг", event, vk_session, peer_id)


# ========== СМЕНА ЧИСЛОВЫХ ПОЛЕЙ ==========
def change_numeric_field(field_name, event, vk_session, peer_id):
    """Универсальная функция смены числовых полей"""
    character = dm.characters_db.get_character(event.user_id)
    if not character:
        send_message(vk_session, peer_id, "❌ Сначала создайте профиль командой 'createprofile'")
        return
    
    text_parts = event.text.strip().split(maxsplit=1)
    if len(text_parts) < 2:
        send_message(vk_session, peer_id, f"❓ **Формат:** {field_name} 10")
        return
    
    try:
        new_value = int(text_parts[1].strip())
    except ValueError:
        return
    
    setattr(character, field_name, new_value)
    dm.characters_db.save_character(character)
    
    send_message(vk_session, peer_id, f"✅ **{field_name} изменено!**\n{field_name} **{new_value}**")


def change_yen_command(event, vk_session, peer_id):
    """йен 1000"""
    change_numeric_field("yen", "💰 Йен", min_val=0, event=event, vk_session=vk_session, peer_id=peer_id)


def change_flesh_particles_command(event, vk_session, peer_id):
    """частицы 5"""
    change_numeric_field("flesh_particles", "👹 Частицы плоти", event=event, vk_session=vk_session, peer_id=peer_id)


def change_level_command(event, vk_session, peer_id):
    """уровень 10"""
    change_numeric_field("level", "⚡ Уровень", event=event, vk_session=vk_session, peer_id=peer_id)


def change_toughness_command(event, vk_session, peer_id):
    """здоровье 15"""
    change_numeric_field("toughness", "❤️ Здоровье", event=event, vk_session=vk_session, peer_id=peer_id)


def change_strength_command(event, vk_session, peer_id):
    """сила 10"""
    change_numeric_field("strength", "💪 Сила", event=event, vk_session=vk_session, peer_id=peer_id)


def change_reflexes_command(event, vk_session, peer_id):
    """рефлексы 8"""
    change_numeric_field("reflexes", "⚡ Рефлексы",  event=event, vk_session=vk_session, peer_id=peer_id)


def change_perception_command(event, vk_session, peer_id):
    """восприятие 12"""
    change_numeric_field("perception", "👁️ Восприятие", event=event, vk_session=vk_session, peer_id=peer_id)


def change_intellect_command(event, vk_session, peer_id):
    """интеллект 15"""
    change_numeric_field("intellect", "🧠 Интеллект", event=event, vk_session=vk_session, peer_id=peer_id)


def change_charisma_command(event, vk_session, peer_id):
    """харизма 7"""
    change_numeric_field("charisma", "🗣️ Харизма", event=event, vk_session=vk_session, peer_id=peer_id)


def change_luck_command(event, vk_session, peer_id):
    """удача 9"""
    change_numeric_field("luck", "🍀 Удача", event=event, vk_session=vk_session, peer_id=peer_id)


# ========== ПРОФИЛЬНЫЕ КОМАНДЫ ==========
PROFILE_COMMANDS = {
    # Просмотр и создание
    "profile": character_profile_command,
    "профиль": character_profile_command,
    "createprofile": create_profile_command,
    "create профиль": create_profile_command,
    
    # Строковые поля
    "name": change_name_command,
    "имя": change_name_command,
    "changename": change_name_command,
    "сменаимени": change_name_command,
    
    "faction": change_faction_command,
    "фракция": change_faction_command,
    
    "class": change_class_command,
    "класс": change_class_command,
    
    "changedesc": change_description_command,
    "осебе": change_description_command,
    "desc": change_description_command,
    
    "profilelink": change_profile_link_command,
    "профильссылка": change_profile_link_command,
    
    "rank": change_rank_command,
    "ранг": change_rank_command,
    
    # Числовые поля
    "yen": change_yen_command,
    "йен": change_yen_command,
    
    "flesh": change_flesh_particles_command,
    "частицы": change_flesh_particles_command,
    
    "level": change_level_command,
    "уровень": change_level_command,
    
    "toughness": change_toughness_command,
    "здоровье": change_toughness_command,
    
    "strength": change_strength_command,
    "сила": change_strength_command,
    
    "reflexes": change_reflexes_command,
    "рефлексы": change_reflexes_command,
    
    "perception": change_perception_command,
    "восприятие": change_perception_command,
    
    "intellect": change_intellect_command,
    "интеллект": change_intellect_command,
    
    "charisma": change_charisma_command,
    "харизма": change_charisma_command,
    
    "luck": change_luck_command,
    "удача": change_luck_command,
}
