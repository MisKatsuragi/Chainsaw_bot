from common_utils import send_message, get_current_time, is_admin, format_item
from database import db

def hi_command(event, vk_session, _, peer_id):
    send_message(vk_session, peer_id, "Hi friend!")

def time_command(event, vk_session, _, peer_id):
    send_message(vk_session, peer_id, f"⏰ Текущее время: {get_current_time()}")

def help_command(event, vk_session, admins, peer_id):
    user_id = event.user_id
    help_text = """📋 Команды:
• hi • time • balance
• market • buy меч • sell меч
• inventory"""
    
    if is_admin(user_id, admins):
        help_text += "\n🔧 /give @id 100 • /status • /additem"
    
    send_message(vk_session, peer_id, help_text)

def balance_command(event, vk_session, _, peer_id):
    user = db.get_user(event.user_id)
    send_message(vk_session, peer_id, f"💰 Баланс: {user.coins} монет")

def market_command(event, vk_session, _, peer_id):
    items = db.get_market_items()
    if not items:
        send_message(vk_session, peer_id, "🏪 Рынок пуст")
        return
    
    market_text = "🏪 Рынок:\n"
    for item in items:
        market_text += f"#{item.index}: {format_item(item)}\n"
    send_message(vk_session, peer_id, market_text)

def buy_command(event, vk_session, _, peer_id):
    try:
        parts = event.text.lower().split(maxsplit=1)
        if len(parts) < 2:
            send_message(vk_session, peer_id, "❓ buy <название/номер>")
            return
        
        result = db.buy_item(event.user_id, parts[1])
        send_message(vk_session, peer_id, result)
    except Exception as e:
        send_message(vk_session, peer_id, "❌ Ошибка покупки")

def sell_command(event, vk_session, _, peer_id):
    try:
        parts = event.text.lower().split(maxsplit=1)
        if len(parts) < 2:
            send_message(vk_session, peer_id, "❓ sell <название/номер>")
            return
        
        result = db.sell_item(event.user_id, parts[1])
        send_message(vk_session, peer_id, result)
    except Exception:
        send_message(vk_session, peer_id, "❌ Ошибка продажи")

def inventory_command(event, vk_session, _, peer_id):
    user = db.get_user(event.user_id)
    if not user.items:
        send_message(vk_session, peer_id, "🎒 Инвентарь пуст")
        return
    
    inv_text = "🎒 Инвентарь:\n"
    for user_index, item in user.items.items():
        inv_text += f"#{user_index}: {item.name} (#{item.index})\n"
    inv_text += f"💰 {user.coins} монет"
    send_message(vk_session, peer_id, inv_text)

USER_COMMANDS = {
    "hi": hi_command, "time": time_command, "help": help_command,
    "balance": balance_command, "market": market_command,
    "buy": buy_command, "sell": sell_command, "inventory": inventory_command
}