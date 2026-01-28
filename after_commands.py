import time
from typing import Dict, Optional, Callable, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AfterCommandState:
    user_id: int
    command_type: str
    data: dict = None
    timeout_time: float = 0


class AfterCommandManager:
    def __init__(self, handlers_dir: str = "handlers"):
        self.handlers_dir = Path(handlers_dir)
        self.handlers_dir.mkdir(exist_ok=True)
        
        # Управляет базами команд
        self._commands: Dict[int, AfterCommandState] = {}
        self._timeouts: Dict[int, float] = {}
        self._handlers: Dict[str, Callable] = {}
        self._registered_modules: Set[str] = set()
        
        # Автозагрузка handlers при первом обращении
        self._auto_load_handlers()
    
    def _auto_load_handlers(self):
        """Автозагрузка всех модулей handlers"""
        modules = ['handlers.market', 'handlers.inventory', 'handlers.contracts'] # нужно расширять
        
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

    def set_timeout(self, user_id: int, seconds: int):
        """Установка таймаута для пользователя"""
        self._timeouts[user_id] = time.time() + seconds
        print(f"⏰ Таймаут для {user_id}: {seconds}с")
    
    def clear_timeout(self, user_id: int):
        """Очистка таймаута пользователя"""
        if user_id in self._timeouts:
            del self._timeouts[user_id]
    
    def check_timeouts(self):
        """Проверка истекших таймаутов"""
        current_time = time.time()
        expired_users = []
        
        for user_id, timeout_time in self._timeouts.items():
            if current_time > timeout_time:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self.clear_command(user_id)
            self.clear_timeout(user_id)
            print(f"⏰ Таймаут истек для {user_id}")
    
    def has_pending(self, user_id: int) -> bool:
        """Проверка наличия отложенной команды с учетом таймаута"""
        self.check_timeouts()  # Проверяем таймауты перед проверкой
        return user_id in self._commands
    
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
        
        # Автоочистка выполненных команд
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


# Глобальный экземпляр как в DataManager
after_manager = AfterCommandManager()