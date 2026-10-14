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

        set_layout.assert_called_once_with(101, None, ())

    def test_ckl_remains_cyclic(self) -> None:
        installed_hkls = (101, 202)
        with (
            patch.object(keyboard_layout_controller, "get_active_hkl", return_value=101),
            patch.object(keyboard_layout_controller, "get_installed_hkls", return_value=installed_hkls),
            patch.object(keyboard_layout_controller, "set_layout") as set_layout,
        ):
            keyboard_layout_controller.set_next_layout("CKL")

        set_layout.assert_called_once_with(202, None, ())

    def test_ckl_forwards_layout_change_callback(self) -> None:
        installed_hkls = (101, 202)
        on_layout_changed = lambda hkl: None
        with (
            patch.object(keyboard_layout_controller, "get_active_hkl", return_value=101),
            patch.object(keyboard_layout_controller, "get_installed_hkls", return_value=installed_hkls),
            patch.object(keyboard_layout_controller, "set_layout") as set_layout,
        ):
            keyboard_layout_controller.set_next_layout("CKL", on_layout_changed)

        set_layout.assert_called_once_with(202, on_layout_changed, ())

    def test_set_layout_invokes_layout_change_callback(self) -> None:
        on_layout_changed = unittest.mock.Mock()
        with (
            patch.object(keyboard_layout_controller.win32gui, "GetForegroundWindow", return_value=1),
            patch.object(keyboard_layout_controller, "get_parent_window", return_value=None),
            patch.object(keyboard_layout_controller.win32gui, "GetWindowText", return_value=""),
            patch.object(keyboard_layout_controller.win32api, "PostMessage") as post_message,
            patch.object(keyboard_layout_controller, "save_current_hkl") as save_current_hkl,
        ):
            keyboard_layout_controller.set_layout(202, on_layout_changed)

        post_message.assert_called_once_with(
            1,
            keyboard_layout_controller.WM_INPUTLANGCHANGEREQUEST,
            keyboard_layout_controller.INPUTLANGCHANGE_SYSCHARSET,
            202,
        )
        save_current_hkl.assert_called_once_with(202)
        on_layout_changed.assert_called_once_with(202)

    def test_set_layout_skips_when_child_title_matches_exception(self) -> None:
        with (
            patch.object(keyboard_layout_controller.win32gui, "GetForegroundWindow", return_value=1),
            patch.object(keyboard_layout_controller, "get_parent_window", return_value=2),
            patch.object(
                keyboard_layout_controller.win32gui,
                "GetWindowText",
                side_effect=("Excluded Application - Document", "Parent"),
            ),
            patch.object(keyboard_layout_controller.win32api, "PostMessage") as post_message,
            patch.object(keyboard_layout_controller, "save_current_hkl") as save_current_hkl,
        ):
            keyboard_layout_controller.set_layout(202, window_title_exceptions=("application",))

        post_message.assert_not_called()
        save_current_hkl.assert_not_called()

    def test_set_layout_skips_when_parent_title_matches_exception(self) -> None:
        with (
            patch.object(keyboard_layout_controller.win32gui, "GetForegroundWindow", return_value=1),
            patch.object(keyboard_layout_controller, "get_parent_window", return_value=2),
            patch.object(
                keyboard_layout_controller.win32gui,
                "GetWindowText",
                side_effect=("Child", "Excluded Parent Window"),
            ),
            patch.object(keyboard_layout_controller.win32api, "PostMessage") as post_message,
            patch.object(keyboard_layout_controller, "save_current_hkl") as save_current_hkl,
        ):
            keyboard_layout_controller.set_layout(202, window_title_exceptions=("excluded parent",))

        post_message.assert_not_called()
        save_current_hkl.assert_not_called()


if __name__ == "__main__":
    unittest.main()
