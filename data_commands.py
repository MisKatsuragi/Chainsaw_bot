from store_data import StoreUsersData
from load_data import LoadUsersData, ReloadUsersData
from excel_export import ExcelExport
from data_manager import dm  # ✅ Глобальный dm


def get_economy_stats_message() -> str:
    """Экономическая статистика"""
    stats = dm.get_stats()
    msg = (f"📊 **Экономика**\n"
            f"👤 Пользователей: {stats['users_count']}\n"
            f"🎒 Предметов: {stats['total_items']}\n"
            f"➕ Внесено в экономику: {stats['total_received']:,}\n"
            f"💸 Пользователи истратили: {stats['total_spent']:,}")
    return msg

def get_forbes_message():
    stats = dm.get_stats()  # Используем get_stats() вместо get_forbes_message()
    msg = "💎 **Топ-10 богатых**:\n"
    for i, (user_id, user_data) in enumerate(stats['rich_users'], 1):
        position = user_data.stats.position
        pos_emoji = "👑" if position == "god" else "⭐" if position == "admin" else ""
        msg += f"{i}. {pos_emoji} {user_id}: {user_data.coins} монет\n"
    return msg

DATA_COMMANDS = {
    "/store": lambda: StoreUsersData(dm),  # ✅ Передаем dm
    "/load": lambda: LoadUsersData(dm),
    "/reload": lambda: ReloadUsersData(dm),
    "/export": lambda: ExcelExport(dm),
    "/stat": lambda: get_economy_stats_message(),
    "/forbs": lambda: get_forbes_message(),
}