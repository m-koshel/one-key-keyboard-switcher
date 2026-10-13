import os
import sys
import unittest
from unittest.mock import patch

import paths


class PathsTest(unittest.TestCase):
    def test_source_execution_uses_source_package_folder(self) -> None:
        source_dir = os.path.abspath("source")
        with patch.object(sys, "frozen", False, create=True), patch.object(
            paths, "get_root_dir", return_value=source_dir
        ):
            self.assertEqual(
                paths.get_root_module_dir(),
                os.path.join(source_dir, "onekey_layout_switcher"),
            )

    def test_frozen_execution_uses_distribution_asset_folder(self) -> None:
        with patch.object(sys, "frozen", True, create=True), patch.object(
            sys, "executable", "C:/dist/MultiLayoutSwitcher.exe"
        ):
            self.assertEqual(
                os.path.normpath(paths.get_root_module_dir()),
                os.path.normpath("C:/dist/multi_layout_switcher"),
            )


if __name__ == "__main__":
    unittest.main()
