from .data_manager import DataManager

def StoreUsersData(dm: DataManager):  # ✅ Принимает dm
    if dm.save_to_file():
        return "✅ Данные сохранены!"
    return "ℹ️ Нет изменений для сохранения"

def StoreUsersDataAsync(dm: DataManager):
    import threading
    thread = threading.Thread(target=dm.save_to_file, daemon=True)
    thread.start()
    return "✅ Сохранение запущено..."