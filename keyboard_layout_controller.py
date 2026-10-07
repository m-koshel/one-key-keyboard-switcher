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

from typing import Optional

import logging
import win32gui
import win32api
import win32process

"""WM_INPUTLANGCHANGEREQUEST: Message posted to the window when input language should be changed.
https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-inputlangchangerequest"""
from win32con import WM_INPUTLANGCHANGEREQUEST

INPUTLANGCHANGE_SYSCHARSET: int = 0x0001
"""Flag means: set the new input locale to be the keyboard layout.
https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-inputlangchangerequest
"""
logger = logging.getLogger(__name__)

def get_active_hkl() -> int:
    """Returns active keyboard HKL for the foreground window.

    :return: HKL
    """

    foreground_window_handle: int = win32gui.GetForegroundWindow()
    thread_id: int = win32process.GetWindowThreadProcessId(foreground_window_handle)[0]
    return win32api.GetKeyboardLayout(thread_id)


_current_hkl: int | None = None
_previous_hkl: int | None = None


def get_installed_hkls() -> tuple[int, ...]:
    """Returns installed keyboard layout handles (HKLs)."""

    return tuple(win32api.GetKeyboardLayoutList())


def reset_hkl_history() -> None:
    """Clears MRU HKL history."""

    global _current_hkl, _previous_hkl
    _current_hkl = None
    _previous_hkl = None


def save_current_hkl(hkl: int) -> None:
    """Records the currently active HKL for MRU switching."""

    global _current_hkl, _previous_hkl
    if _current_hkl is None:
        installed_hkls: tuple[int, ...] = get_installed_hkls()
        _previous_hkl = installed_hkls[0] if installed_hkls else None

    installed_hkls: tuple[int, ...] = get_installed_hkls()    
    first_hkl = installed_hkls[0]
    if _current_hkl != first_hkl and hkl != first_hkl: 
        _previous_hkl = first_hkl
    else:
        _previous_hkl = _current_hkl
    _current_hkl = hkl
      

def get_previous_hkl() -> int | None:
    """Returns the most recently used HKL before the current HKL."""

    return _previous_hkl


def set_next_layout(layout_switching: str = 'CKL') -> None:
    """Switches to the next cyclic HKL or the most recently used HKL."""

    global _current_hkl, _previous_hkl
    mode: str = layout_switching.strip().upper()
    installed_hkls: tuple[int, ...] = get_installed_hkls()
    if mode == 'FLU':
        if _previous_hkl is None:
            installed_hkls: tuple[int, ...] = get_installed_hkls()
            _previous_hkl = installed_hkls[0] if installed_hkls else None
        else:
            set_layout(_previous_hkl)
            return
    
    installed_hkls: tuple[int, ...] = get_installed_hkls()
    current_hkl: int = get_active_hkl()
    current_index: int = installed_hkls.index(current_hkl)
    next_hkl: int = installed_hkls[(current_index + 1) % len(installed_hkls)]
    set_layout(next_hkl)


def get_parent_window(hwnd: int) -> Optional[int]:
    return win32gui.GetParent(hwnd)


def set_layout(hkl: int) -> None:
    """Sets the keyboard layout according to either the language ID or the layout ID.
    If a language contains more than one layout, it could be important what you pass to this method
    and what you want to change.

    :param hkl: HKL of the keyboard layout. Must be present in the installed list.
    """

    foreground_wnd: int = win32gui.GetForegroundWindow()
    parent_hwnd: Optional[int] = get_parent_window(foreground_wnd)
    hwnd: int = parent_hwnd if parent_hwnd else foreground_wnd
    """If the foreground window has a parent, 
    then we have to address the request for a keyboard layout change to its parent.
    
    For example:
    
    "Notepad" -> "Save As":
        - "Save as" - is_child = False, is_popup = True
        - "Notepad" - parent window
    
    "Desktop" aka "Program Manager": is_child = False, is_popup = True, parent = 0
    "Start Menu": is_child = False, is_popup = True, parent = 0
    
    To get window title:
        window_title = win32gui.GetWindowText(foreground_wnd)
    """

    win32api.PostMessage(hwnd, WM_INPUTLANGCHANGEREQUEST, INPUTLANGCHANGE_SYSCHARSET, hkl)
    """Async request for language changing.
    Window may reject language changing.
    
    For sync request, use SendMessage, but note that this call
    does not update the language in the system language panel,
    but you can use it in addition to the PostMessage call.
    
    Always use the original ID. If it is negative, keep it negative; do not mask it with & 0xFFFFFFF.
    """
