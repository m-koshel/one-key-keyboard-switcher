import unittest
from unittest.mock import patch

import keyboard_layout_controller


class KeyboardLayoutControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        keyboard_layout_controller.reset_hkl_history()

    def test_flu_switches_to_previous_hkl(self) -> None:
        installed_hkls = (101, 202)
        with (
            patch.object(keyboard_layout_controller, "get_active_hkl", return_value=202),
            patch.object(keyboard_layout_controller, "get_installed_hkls", return_value=installed_hkls),
            patch.object(keyboard_layout_controller, "set_layout") as set_layout,
        ):
            keyboard_layout_controller.save_current_hkl(202)
            keyboard_layout_controller.set_next_layout("FLU")

        set_layout.assert_called_once_with(101, None)

    def test_ckl_remains_cyclic(self) -> None:
        installed_hkls = (101, 202)
        with (
            patch.object(keyboard_layout_controller, "get_active_hkl", return_value=101),
            patch.object(keyboard_layout_controller, "get_installed_hkls", return_value=installed_hkls),
            patch.object(keyboard_layout_controller, "set_layout") as set_layout,
        ):
            keyboard_layout_controller.set_next_layout("CKL")

        set_layout.assert_called_once_with(202, None)

    def test_ckl_forwards_layout_change_callback(self) -> None:
        installed_hkls = (101, 202)
        on_layout_changed = lambda hkl: None
        with (
            patch.object(keyboard_layout_controller, "get_active_hkl", return_value=101),
            patch.object(keyboard_layout_controller, "get_installed_hkls", return_value=installed_hkls),
            patch.object(keyboard_layout_controller, "set_layout") as set_layout,
        ):
            keyboard_layout_controller.set_next_layout("CKL", on_layout_changed)

        set_layout.assert_called_once_with(202, on_layout_changed)

    def test_set_layout_invokes_layout_change_callback(self) -> None:
        on_layout_changed = unittest.mock.Mock()
        with (
            patch.object(keyboard_layout_controller.win32gui, "GetForegroundWindow", return_value=1),
            patch.object(keyboard_layout_controller, "get_parent_window", return_value=None),
            patch.object(keyboard_layout_controller.win32api, "PostMessage"),
            patch.object(keyboard_layout_controller, "save_current_hkl"),
        ):
            keyboard_layout_controller.set_layout(202, on_layout_changed)

        on_layout_changed.assert_called_once_with(202)


if __name__ == "__main__":
    unittest.main()
