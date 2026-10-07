#  Copyright (C) 2024 Oleksii Sylichenko (a.silichenko@gmail.com)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import configparser
import logging
from pathlib import Path
from typing import Optional

logger: logging.Logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'key_press_timeout': 0.15,
    'layout_check_interval': 0.5,
    'layout_switching': 'CKL',
}


class Config:
    """Reads application settings and hotkey mappings from an INI file."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        path = config_path or Path(__file__).with_name('config.ini')
        parser = configparser.ConfigParser()
        parser.read(path, encoding='utf-8')

        self.key_press_timeout: float = float(
            parser.getfloat('settings', 'key press timeout', fallback=DEFAULT_CONFIG['key_press_timeout'])
        )
        self.layout_check_interval: float = float(
            parser.getfloat(
                'settings',
                'layout check interval',
                fallback=DEFAULT_CONFIG['layout_check_interval'],
            )
        )
        self.layout_switching: str = parser.get(
            'settings',
            'layout switching',
            fallback=DEFAULT_CONFIG['layout_switching'],
        ).strip().upper()
        if self.layout_switching not in {'CKL', 'FLU'}:
            logger.warning(
                'Unsupported layout switching mode %r; using CKL',
                self.layout_switching,
            )
            self.layout_switching = 'CKL'

        hotkeys: dict[str, Optional[int]] = {}
        if parser.has_section('hotkeys'):
            for key, value in parser.items('hotkeys'):
                hotkeys[key.strip().lower()] = (
                    None if not value.strip() else int(value.strip(), 0)
                )

        self.hotkeys: dict[str, Optional[int]] = hotkeys


def main() -> None:
    config: Config = Config()
    print(f'{config.hotkeys = }')
    print(f'{config.key_press_timeout = }')
    print(f'{config.layout_check_interval = }')


if __name__ == "__main__":
    main()
