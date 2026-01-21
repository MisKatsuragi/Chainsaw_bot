from .data_manager import DataManager

def LoadUsersData(dm: DataManager):  # ✅ Принимает dm
    if dm.load_from_file():
        return "✅ Данные загружены!"
    return "ℹ️ Файл не найден"

def ReloadUsersData(dm: DataManager):
    if dm.reload_from_file():
        return "✅ Данные перезагружены с бэкапом!"
    return "❌ Ошибка перезагрузки"