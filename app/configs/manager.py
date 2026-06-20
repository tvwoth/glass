"""
Configuration manager for contour calculator.
Provides CRUD operations for system and user configurations.
"""
import json
import os
import re
from typing import Any, Optional, List, Dict

VIRTUAL_CUSTOM_CONFIG = 'Пользовательская конфигурация'
H_PARAM_KEYS = (
    'j_x', 'c_x', 'cd_len', 'de_len', 'fg_len',
    'gh_len', 'hi_len', 'jk_len', 'hcor', 'h9',
)
MAX_CONFIG_NAME_LEN = 100
MAX_CONFIG_FILE_SIZE = 4096


class ConfigManager:
    """
    Manages configuration files (system presets and user configs).
    
    System configs are read-only and stored in app/configs/.
    User configs are stored in a separate directory (default: app/user_configs/).
    """

    def __init__(self, app_dir: str, user_configs_dir: Optional[str] = None):
        self.app_dir = app_dir
        self.system_dir = os.path.join(app_dir, 'configs')
        self.user_dir = user_configs_dir or os.environ.get(
            'USER_CONFIGS_DIR',
            os.path.join(app_dir, 'user_configs'),
        )
        self._ensure_user_dir()

    def _ensure_user_dir(self) -> None:
        """Ensure user configs directory exists."""
        try:
            os.makedirs(self.user_dir, exist_ok=True)
        except OSError:
            self.user_dir = None
            return

        if not os.path.isdir(self.user_dir):
            self.user_dir = None

    def load(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a configuration by name. Returns None for virtual custom config."""
        path = self.resolve_config_path(name)
        if not path:
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None

    def save(self, name: str, data: Dict[str, Any]) -> str:
        """Save a user configuration."""
        if not self.user_dir:
            raise ValueError('Каталог пользовательских конфигураций недоступен для записи')

        safe_name = self._sanitize_name(name)
        validated = self._validate_params(data)
        payload = {**validated, 'image': None}

        try:
            os.makedirs(self.user_dir, exist_ok=True)
        except OSError as e:
            raise ValueError(f'Не удалось создать директорию конфигураций: {str(e)}')

        path = os.path.join(self.user_dir, f'{safe_name}.json')
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
        except IOError as e:
            raise ValueError(f'Не удалось сохранить файл конфигурации: {str(e)}')
        except json.JSONDecodeError as e:
            raise ValueError(f'Ошибка кодирования JSON: {str(e)}')

        return safe_name

    def list(self) -> List[str]:
        """List all available configurations (system + user)."""
        return self.list_system() + self.list_user()

    def list_system(self) -> List[str]:
        """List system preset configurations."""
        if not os.path.isdir(self.system_dir):
            return []
        names = [
            os.path.splitext(f)[0]
            for f in os.listdir(self.system_dir)
            if f.endswith('.json')
        ]
        return sorted(names, key=lambda name: (name != 'задайте значения', name))

    def list_user(self) -> List[str]:
        """List user configurations."""
        if not self.user_dir or not os.path.isdir(self.user_dir):
            return []
        names = [
            os.path.splitext(f)[0]
            for f in os.listdir(self.user_dir)
            if f.endswith('.json')
        ]
        return sorted(names)

    def all_selectable_configs(self) -> List[str]:
        """Return all configs available for selection in UI (system + user + virtual)."""
        return self.list_system() + self.list_user() + [VIRTUAL_CUSTOM_CONFIG]

    def duplicate(self, name: str, new_name: str) -> str:
        """Duplicate an existing configuration."""
        data = self.load(name)
        if data is None:
            raise ValueError(f'Конфигурация «{name}» не найдена')
        return self.save(new_name, data)

    def delete(self, name: str) -> None:
        """Delete a user configuration."""
        if self._is_system(name):
            raise ValueError('Нельзя удалить системный пресет')
        if not self._is_user(name):
            raise ValueError('Пользовательская конфигурация не найдена')
        path = os.path.join(self.user_dir, f'{name}.json')
        os.remove(path)

    def rename(self, old_name: str, new_name: str) -> str:
        """Rename a user configuration."""
        if self._is_system(old_name):
            raise ValueError('Нельзя переименовать системный пресет')
        if not self._is_user(old_name):
            raise ValueError('Пользовательская конфигурация не найдена')
        safe_new = self._sanitize_name(new_name)
        old_path = os.path.join(self.user_dir, f'{old_name}.json')
        new_path = os.path.join(self.user_dir, f'{safe_new}.json')
        if os.path.isfile(new_path) and safe_new != old_name:
            raise ValueError('Конфигурация с таким именем уже существует')
        os.rename(old_path, new_path)
        return safe_new

    def resolve_config_path(self, name: str) -> Optional[str]:
        """Resolve configuration file path by name."""
        system_path = os.path.join(self.system_dir, f'{name}.json')
        if os.path.isfile(system_path):
            return system_path
        if not self.user_dir:
            return None
        user_path = os.path.join(self.user_dir, f'{name}.json')
        if os.path.isfile(user_path):
            return user_path
        return None

    def is_system(self, name: str) -> bool:
        """Check if configuration is a system preset."""
        return os.path.isfile(os.path.join(self.system_dir, f'{name}.json'))

    def is_user(self, name: str) -> bool:
        """Check if configuration is a user configuration."""
        if not self.user_dir:
            return False
        return os.path.isfile(os.path.join(self.user_dir, f'{name}.json'))

    def _is_system(self, name: str) -> bool:
        """Internal check for system config."""
        return self.is_system(name)

    def _is_user(self, name: str) -> bool:
        """Internal check for user config."""
        return self.is_user(name)

    def _sanitize_name(self, name: str) -> str:
        """Validate and sanitize configuration name."""
        name = (name or '').strip()
        if not name:
            raise ValueError('Имя конфигурации не может быть пустым')
        if len(name) > MAX_CONFIG_NAME_LEN:
            raise ValueError(f'Имя конфигурации не длиннее {MAX_CONFIG_NAME_LEN} символов')
        if '..' in name or '/' in name or '\\' in name:
            raise ValueError('Имя не должно содержать .., / или \\')
        if name == VIRTUAL_CUSTOM_CONFIG:
            raise ValueError('Зарезервированное имя конфигурации')
        if not re.match(r'^[\w\- ]+$', name, re.UNICODE):
            raise ValueError('Имя может содержать только буквы, цифры, пробелы, _ и -')
        return name

    def _validate_params(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Validate configuration parameters."""
        result: Dict[str, float] = {}
        for key in H_PARAM_KEYS:
            if key not in data or data[key] is None:
                raise ValueError(f'Поле {key} обязательно и должно быть числом')
            try:
                value = float(data[key])
            except (TypeError, ValueError) as exc:
                raise ValueError(f'Поле {key} должно быть числом') from exc
            result[key] = value
        return result

    def validate_h_params(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Public wrapper for parameter validation."""
        return self._validate_params(data)

    def params_match(self, params: Dict[str, Optional[float]], config_data: Dict) -> bool:
        """Check if current parameters match saved configuration."""
        for key in H_PARAM_KEYS:
            current = params.get(key)
            saved = config_data.get(key, 0)
            if current is None:
                continue
            if abs(current - saved) >= 1e-6:
                return False
        return True

    def to_config_dict(self, calculator) -> Dict[str, Any]:
        """Extract configuration from calculator state."""
        return {
            'j_x': calculator.J_X,
            'c_x': calculator.C_X,
            'cd_len': calculator.CD_LEN,
            'de_len': calculator.DE_LEN,
            'fg_len': calculator.FG_LEN,
            'gh_len': calculator.GH_LEN,
            'hi_len': calculator.HI_LEN,
            'jk_len': calculator.JK_LEN,
            'hcor': calculator.HCOR,
            'h9': calculator.H9,
            'image': None,
        }