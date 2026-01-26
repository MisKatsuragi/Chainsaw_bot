from storege.load_data import LoadUsersData, ReloadUsersData
from storege.excel_import import import_market_from_excel
from storege.economy_analyzer import ecm
from storege.data_manager import dm
from common_utils import send_message


def get_forbes_message(event, vk_session, peer_id):
    """Топ богатых по йенам и частицам"""
    message = "💎 **ТОП-10 ПО ЙЕНАМ**\n\n"
    
    # Топ по йенам
    top_yen = ecm.get_top_yen_players(10)
    if top_yen:
        for i, player in enumerate(top_yen, 1):
            message += f"{i:2d}. **{player['name']}** [{player['rank']}] **{player['yen']:,}¥**\n"
    else:
        message += "👥 Нет игроков\n\n"
    
    message += "\n👹 **ТОП-10 ПО ЧАСТИЦАМ ПЛОТИ**\n\n"
    
    # Топ по частицам
    top_flesh = ecm.get_top_flesh_players(10)
    if top_flesh:
        for i, player in enumerate(top_flesh, 1):
            message += f"{i:2d}. **{player['name']}** [{player['rank']}] **{player['flesh_particles']:,}**\n"
    else:
        message += "👥 Нет игроков\n"
    
    send_message(vk_session, peer_id, message)

def top_yen_command(event, vk_session, peer_id):
    """Только топ по йенам"""
    top_players = ecm.get_top_yen_players(10)
    
    if not top_players:
        send_message(vk_session, peer_id, "❌ Нет игроков с йенами!")
        return
    
    message = "💰 **ТОП-10 ПО ЙЕНАМ**\n\n"
    for i, player in enumerate(top_players, 1):
        message += f"{i:2d}. **{player['name']}** [{player['rank']}] **{player['yen']:,}¥**\n"
    
    send_message(vk_session, peer_id, message)


def top_flesh_command(event, vk_session, peer_id):
    """Только топ по частицам плоти"""
    top_players = ecm.get_top_flesh_players(10)
    
    if not top_players:
        send_message(vk_session, peer_id, "❌ Нет игроков с частицами!")
        return
    
    message = "👹 **ТОП-10 ПО ЧАСТИЦАМ ПЛОТИ**\n\n"
    for i, player in enumerate(top_players, 1):
        message += f"{i:2d}. **{player['name']}** [{player['rank']}] **{player['flesh_particles']:,}**\n"
    
    send_message(vk_session, peer_id, message)



def get_economy_stats_message(event, vk_session, peer_id):
    """Экономическая статистика"""
    stats = dm.get_stats()
    
    if 'error' in stats:
        send_message(vk_session, peer_id, stats['error'])
        return
    
    message = "📈 **ЭКОНОМИКА СЕРВЕРА**\n\n"
    message += f"👥 Игроков: **{stats['users_count']}**\n"
    message += f"👥 Предметов: **{stats['total_items']}**\n"
    message += f"💰 Всего йен: **{stats['total_yen']:,}¥**\n"
    message += f"💰 Внесено в экономику: **{stats['total_received']:,}¥**\n"
    message += f"💰 Пользователи исторатели: **{stats['total_spent']:,}¥**\n"
    
    send_message(vk_session, peer_id, message)

DATA_COMMANDS = {
    "/load": lambda: LoadUsersData(dm),
    "/reload": lambda: ReloadUsersData(dm),
    "/importmarket": lambda: import_market_from_excel(),
    "/экономика": get_economy_stats_message,
    "/forbs": get_forbes_message,
    "/yen_top": top_yen_command,
    "/flesh_top": top_flesh_command,
}