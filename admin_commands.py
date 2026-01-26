import sys
from common_utils import send_message, parse_target_user, get_user_link
from config import HOST
from storege.data_manager import dm 
from data_commands import DATA_COMMANDS


# Назначение первого админа, в соответствии с законом робототехники 
# Человек всегда должен быть главнее машины
def make_god(event, vk_session, peer_id):
    user_id = event.user_id

    if dm.is_god(user_id):
        send_message(vk_session, peer_id, "❌ Таблетки прими!")
        return
    if dm.is_admin(user_id):
        send_message(vk_session, peer_id, "❌ Ишь самозванец!")
        return
    dm.roles_db.add_god(user_id)
    dm.roles_db.add_admin(user_id)
    user_link = get_user_link(user_id)
    send_message(vk_session, peer_id, f"✅ {user_link} = GOD!")
    print(f"Создатель: {user_id}")


# Выключение бота на хосте
def shut_down(event, vk_session, peer_id):
    if not dm.is_god(event.user_id):
        send_message(vk_session, peer_id, "Ты шо охуел?")
        return
    send_message(vk_session, peer_id, "Бот выключен")
    sys.exit(0)


# Общие данные о беседе
def status_command(event, vk_session, peer_id):
    god_id = list(dm.god)[0] if dm.god else None
    #god_link = get_user_link(god_id) if god_id else "Не назначен"
    user_info = vk_session.method("users.get", {"user_ids": event.user_id})[0]
    user_name = f"{user_info['first_name']} {user_info['last_name']}"
    characters_count = len(dm.characters_db.characters)
    market_items_count = len(dm.items_db.items)
    send_message(vk_session, peer_id, 
        f"Host: {HOST}\n"
        f"👑 **Бог**: {user_name}\n"
        f"👥 Админов: {len(dm.admins)}\n"
        f"👤 Персонажей: {characters_count}\n"
        f"🛒 Рынок: {market_items_count}\n"
        f"💰 Йен в игре: {sum(c.yen for c in dm.characters_db.characters.values())}")



def handle_data_command(event, vk_session, peer_id):
    """Обработчик команд DATA_COMMANDS"""
    if not dm.is_admin(event.user_id) and not dm.is_god(event.user_id): 
        return
    
    command = event.text.split()[0]
    if command in DATA_COMMANDS:
        result = DATA_COMMANDS[command](event, vk_session, peer_id)
        send_message(vk_session, peer_id, result)


# Дать йен персонажу
def give_command(event, vk_session, peer_id):
    if not dm.is_admin(event.user_id):
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        target_link = get_user_link(target_id)
        parts = text.split()
        yen = int(parts[-1])
        character = dm.get_or_create_character(target_id, f"User{target_id}")
        character.yen += yen
        character.total_yen_received += yen
        
        send_message(vk_session, peer_id, f"✅ +{yen}¥ персонажу {target_link}")
        print(f"Админ выдал {yen}¥ пользователю {target_id}")
    except:
        send_message(vk_session, peer_id, "❓ /give [ссылка] 100")


# Забрать йен у персонажа
def pick_command(event, vk_session, peer_id):
    if not dm.is_admin(event.user_id): 
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        text = event.text
        target_id = parse_target_user(text, event)
        target_link = get_user_link(target_id)
        parts = text.split()
        yen = int(parts[-1])
        
        character = dm.get_or_create_character(target_id, f"User{target_id}")
        if character.yen >= yen:
            character.yen -= yen
            character.total_yen_spend += yen
            send_message(vk_session, peer_id, f"✅ -{yen}¥ у персонажа {target_link}")
        else:
            send_message(vk_session, peer_id, f"❌ У персонажа только {character.yen}¥")
    except:
        send_message(vk_session, peer_id, "❓ /pick [ссылка] 100")


def stat_command(event, vk_session, peer_id):
    """ /stat сила 5 [ссылка] - управление характеристиками персонажей """
    if not dm.is_admin(event.user_id) and not dm.is_god(event.user_id):
        return
    
    try:
        parts = event.text.strip().split(maxsplit=3)
        if len(parts) < 3:
            send_message(vk_session, peer_id, 
                "❓ **Формат:** `/stat <характеристика> <значение> [ссылка/ответ]`\n\n"
                "📋 **Характеристики:** сила, рефлексы, восприятие, интеллект, харизма, удача, здоровье, уровень, йен, частицы")
            return
        
        stat_name, value_str = parts[1].lower(), parts[2]
        target_id = parse_target_user(event.text, event)
        target_link = get_user_link(target_id)
        
        # Проверяем, что характеристика существует
        stat_mapping = {
            'сила': 'strength',
            'strength': 'strength',
            'рефлексы': 'reflexes', 
            'reflexes': 'reflexes',
            'восприятие': 'perception',
            'perception': 'perception',
            'интеллект': 'intellect',
            'intellect': 'intellect',
            'харизма': 'charisma',
            'charisma': 'charisma',
            'удача': 'luck',
            'luck': 'luck',
            'здоровье': 'toughness',
            'toughness': 'toughness',
            'уровень': 'level',
            'level': 'level',
            'йен': 'yen',
            'yen': 'yen',
            'частицы': 'flesh_particles',
            'flesh': 'flesh_particles',
        }
        
        if stat_name not in stat_mapping:
            send_message(vk_session, peer_id, 
                f"❌ Неизвестная характеристика: **{parts[1]}**\n"
                "📋 Доступно: сила, рефлексы, восприятие, интеллект, харизма, удача, здоровье, уровень, йен, частицы")
            return
        
        db_field = stat_mapping[stat_name]
        change_value = int(value_str)
        
        # Получаем персонажа
        character = dm.characters_db.create_or_get_character(target_id, f"User{target_id}")  
        setattr(character, db_field, change_value)
        dm.characters_db.save_character(character)
        
        # target_link = get_user_link(target_id)
        stat_display = {
            'strength': '💪 Сила',
            'reflexes': '⚡ Рефлексы', 
            'perception': '👁️ Восприятие',
            'intellect': '🧠 Интеллект',
            'charisma': '🗣️ Харизма',
            'luck': '🍀 Удача',
            'toughness': '❤️ Здоровье',
            'level': '⚡ Уровень',
            'yen': '💰 Йен',
            'flesh_particles': '👹 Частицы'
        }.get(db_field, db_field)
        
        send_message(vk_session, peer_id, 
            f"✅ **{stat_display}** !\n"
            f"👤 {target_link} установлено {stat_display}: {change_value}\n")
            
    except Exception as e:
        send_message(vk_session, peer_id, f"❌ Ошибка: {str(e)}")


def userinfo_command(event, vk_session, peer_id):
    """ /userinfo <поле> <значение> [ссылка/ответ] - управление строковыми полями персонажей (админ) """
    if not dm.is_admin(event.user_id) and not dm.is_god(event.user_id):
        return
    
    try:
        parts = event.text.strip().split(maxsplit=3)
        if len(parts) < 3:
            send_message(vk_session, peer_id, 
                "❓ **Формат:** `/userinfo <поле> <значение> [ссылка/ответ]`\n\n"
                "📋 **Поля:** имя, фракция, класс, описание, профильссылка, ранг")
            return
        
        field_name, value = parts[1].lower(), parts[2]
        target_id = parse_target_user(event.text, event)
        target_link = get_user_link(target_id)
        
        # Маппинг русских/английских названий полей на DB поля
        field_mapping = {
            # Имя
            'имя': 'name',
            'name': 'name',
            
            # Фракция
            'фракция': 'faction',
            'faction': 'faction',
            
            # Класс
            'класс': 'char_class',
            'class': 'char_class',
            
            # Описание
            'описание': 'self_description',
            'осебе': 'self_description',
            'desc': 'self_description',
            'description': 'self_description',
            'changedesc': 'self_description',
            
            # Профиль ссылка
            'профильссылка': 'profile_link',
            'profilelink': 'profile_link',
            'profile_link': 'profile_link',
            'ссылка': 'profile_link',
            
            # Ранг
            'ранг': 'rank',
            'rank': 'rank',
        }
        
        if field_name not in field_mapping:
            send_message(vk_session, peer_id, 
                f"❌ Неизвестное поле: **{parts[1]}**\n"
                "📋 Доступно: имя, фракция, класс, описание, профильссылка, ранг")
            return
        
        db_field = field_mapping[field_name]
        
        # Проверяем, что значение не пустое
        if not value or value.strip() == "":
            send_message(vk_session, peer_id, "❌ Значение не может быть пустым!")
            return
        
        # Получаем/создаем персонажа
        character = dm.characters_db.create_or_get_character(target_id, f"User{target_id}")
        setattr(character, db_field, value.strip())
        dm.characters_db.save_character(character)
        
        # Отображаемые названия
        field_display = {
            'name': '👤 Имя',
            'faction': '🏛️ Фракция',
            'char_class': '🎭 Класс',
            'self_description': '📝 Описание',
            'profile_link': '🔗 Профиль',
            'rank': '⭐ Ранг'
        }.get(db_field, db_field)
        
        # Обрезаем длинные значения для превью
        preview = value[:50]
        if len(value) > 50:
            preview += "..."
        
        send_message(vk_session, peer_id, 
            f"👤 {target_link}\n"
            f"{field_display}: **{preview}**")
            
    except Exception as e:
        send_message(vk_session, peer_id, f"❌ Ошибка: {str(e)}")


# Добавить предмет на рынок
def additem_command(event, vk_session, peer_id):
    if not dm.is_admin(event.user_id): 
        send_message(vk_session, peer_id, "❌ Нет прав")
        return
    
    try:
        parts = event.text.split(maxsplit=3)
        if len(parts) < 4:
            send_message(vk_session, peer_id, "❓ /additem <name> <cost> <category> <desc>")
            return
            
        name, cost, category, desc = parts[1], int(parts[2]), parts[3], parts[4]
        
        from storege.databases.items_db import Item
        item = Item(
            identifier=f"{name[:3].upper()}{len(dm.items_db.items)+1}",
            name=name,
            category=category,
            cost=cost
        )
        
        if dm.add_market_item(item):
            send_message(vk_session, peer_id, f"✅ #{item.identifier}: {name} добавлен!")
        else:
            send_message(vk_session, peer_id, "❌ Предмет уже существует")
    except Exception as e:
        send_message(vk_session, peer_id, f"❌ Ошибка: {e}")


ADMIN_COMMANDS = {
    "/god": make_god, 
    "/status": status_command,
    "/give": give_command, 
    "/pick": pick_command,
    "/additem": additem_command,
    "/shutdown": shut_down,
    "/stat": stat_command,
    "/стат": stat_command,
    "/userinfo": userinfo_command
}