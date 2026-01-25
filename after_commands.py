from typing import Dict, Optional, Callable, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AfterCommandState:
    user_id: int
    command_type: str
    data: dict = None


class AfterCommandManager:
    def __init__(self, handlers_dir: str = "handlers"):
        self.handlers_dir = Path(handlers_dir)
        self.handlers_dir.mkdir(exist_ok=True)
        
        # ✅ Как DataManager управляет базами данных
        self._commands: Dict[int, AfterCommandState] = {}
        self._handlers: Dict[str, Callable] = {}
        self._registered_modules: Set[str] = set()
        
        # ✅ Автозагрузка handlers при первом обращении
        self._auto_load_handlers()
    
    def _auto_load_handlers(self):
        """Автозагрузка всех модулей handlers"""
        modules = ['market', 'inventory', 'trades']  # ✅ Можно расширять
        
        for module_name in modules:
            try:
                module = __import__(f"{module_name}", fromlist=['after_handlers'])
                handlers = getattr(module, 'after_handlers', None)
                if handlers:
                    for cmd_type, handler in handlers.items():
                        self.register_handler(cmd_type, handler)
                    self._registered_modules.add(module_name)
                    print(f"✅ Загружены handlers из {module_name}: {list(handlers.keys())}")
            except (ImportError, AttributeError):
                print(f"⚠️ Модуль {module_name} не доступен")
    
    def register_handler(self, command_type: str, handler: Callable):
        """Регистрация handler (аналог mark_dirty)"""
        self._handlers[command_type] = handler
    
    def add_command(self, user_id: int, command_type: str, data: dict = None):
        """Добавление отложенной команды (аналог get_or_create_character)"""
        self._commands[user_id] = AfterCommandState(user_id, command_type, data)
        print(f"✅ AfterCommand: {user_id} -> {command_type}")
    
    def has_pending(self, user_id: int) -> bool:
        """Проверка наличия отложенной команды"""
        return user_id in self._commands
    
    def get_state(self, user_id: int) -> Optional[AfterCommandState]:
        """Получение состояния команды"""
        return self._commands.get(user_id)
    
    def handle_after_command(self, event, vk_session, peer_id, command_set=None):
        """Главная функция обработки (аналог save_all)"""
        user_id = event.user_id
        state = self.get_state(user_id)
        
        if not state:
            return False
        
        handler = self._handlers.get(state.command_type)
        if handler:
            print(f"🔄 Выполняем handler: {state.command_type}")
            handled = handler(event, vk_session, peer_id, state)
            if handled:
                return True
        
        # ✅ Автоочистка выполненных команд
        self.clear_command(user_id)
        print(f"🗑️ Очищена команда {user_id}: {state.command_type}")
        return True
    
    def clear_command(self, user_id: int):
        """Очистка команды пользователя"""
        if user_id in self._commands:
            del self._commands[user_id]
    
    @property
    def active_users(self) -> Set[int]:
        """Список пользователей с активными командами"""
        return set(self._commands.keys())
    
    @property
    def registered_commands(self) -> Set[str]:
        """Список всех зарегистрированных команд"""
        return set(self._handlers.keys())
    
    def get_stats(self):
        """Статистика (аналог DataManager.get_stats)"""
        return {
            'active_users': len(self._commands),
            'registered_handlers': len(self._handlers),
            'registered_modules': len(self._registered_modules)
        }


# ✅ Глобальный экземпляр как в DataManager
after_manager = AfterCommandManager()