import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from config_reader import Config


class ConfigTest(unittest.TestCase):
    def test_frozen_application_reads_config_next_to_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            executable_dir = Path(temporary_directory)
            config_path = executable_dir / "config.ini"
            config_path.write_text(
                "[settings]\nlayout switching = FLU\n",
                encoding="utf-8",
            )

            with patch.object(
                sys, "frozen", True, create=True
            ), patch.object(
                sys, "executable", str(executable_dir / "app.exe")
            ):
                config = Config()

            self.assertEqual(config.layout_switching, "FLU")

    def test_hotkeys_can_be_configured_with_key_and_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "config.ini"
            config_path.write_text(
                """[hotkeys]
ctrl =
left shift = 0x422
right shift = 0x409
""",
                encoding="utf-8",
            )

            config = Config(config_path=config_path)

            self.assertEqual(config.hotkeys, {
                "ctrl": None,
                "left shift": 0x422,
                "right shift": 0x409,
            })

    def test_missing_hotkeys_section_uses_no_mappings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "empty.ini"
            config_path.write_text("[settings]\n", encoding="utf-8")

            config = Config(config_path=config_path)

            self.assertEqual(config.hotkeys, {})

    def test_layout_switching_defaults_to_ckl(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "config.ini"
            config_path.write_text("[settings]\n", encoding="utf-8")

            config = Config(config_path=config_path)

            self.assertEqual(config.layout_switching, "CKL")

    def test_layout_switching_accepts_flu(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config_path = Path(temporary_directory) / "config.ini"
            config_path.write_text(
                "[settings]\nlayout switching = FLU\n",
                encoding="utf-8",
            )

            config = Config(config_path=config_path)

            self.assertEqual(config.layout_switching, "FLU")


if __name__ == "__main__":
    unittest.main()
