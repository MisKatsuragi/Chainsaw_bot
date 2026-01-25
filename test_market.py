from storege.data_manager import dm
from handlers.market import format_item_short, extract_subcategory

print("🔍 ТЕСТ ФОРМАТИРОВАНИЯ:")
for identifier, item in list(dm.items_db.items.items())[:5]:
    print(f"{format_item_short(item)}")
    print(f"  Подкатегория: {extract_subcategory(item.name, item.category)}")
    print()

print("✅ ГОТОВО! Теперь перезапустите бота")