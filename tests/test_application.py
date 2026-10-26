from pathlib import Path
import os
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication
from workflow_bridge.application import create_host
from workflow_bridge.core.paths import get_cache_dir, get_data_dir
from workflow_bridge.state import BridgeRuntime


class StandaloneApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_host_starts_empty_without_pet_services_or_account_migration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "own-data"
            with patch.dict(os.environ, {"WORKFLOW_BRIDGE_HOME":str(root)}), patch("requests.Session", side_effect=AssertionError("no external service")):
                window = create_host(self.app)
                try:
                    workflow, weixin, bark, questions = window.controllers
                    self.assertIsInstance(window.runtime, BridgeRuntime)
                    self.assertEqual(get_cache_dir(), root / "cache")
                    self.assertFalse(questions._enabled)
                    self.assertIsNone(weixin._credentials)
                    self.assertFalse(bark._enabled)
                    self.assertFalse(any(name=="aipet" or name.startswith("aipet.") for name in sys.modules))
                    self.assertFalse(any(name=="torch" or name.startswith("torch.") for name in sys.modules))
                    window.pause_action.setChecked(True)
                    self.assertTrue(window.runtime.paused)
                    self.assertFalse(workflow._allowed())
                    self.assertFalse(weixin._interactive_allowed())
                    self.assertFalse(questions._allowed())
                    self.assertFalse(bark._allowed())
                    self.assertFalse(root.exists())
                finally:
                    # This fixture shares QApplication with subsequent tests;
                    # the real executable smoke test covers application quit.
                    window.quit_coordinator.finish = lambda: None
                    window.quit_coordinator.request()
                    deadline=time.monotonic()+3
                    while not window.quit_coordinator.completed and time.monotonic()<deadline:
                        self.app.processEvents()
                        time.sleep(0.005)
                    self.assertTrue(window.quit_coordinator.completed)
                    self.assertTrue(window.runtime.closing)
                    window.deleteLater()
                    self.app.processEvents()

    def test_data_path_rejects_relative_parent_traversal_and_remote_roots(self):
        for value in ("relative", r"C:\safe\..\other", r"\\host\share\data"):
            with self.subTest(value=value), patch.dict(os.environ, {"WORKFLOW_BRIDGE_HOME":value}), self.assertRaises(ValueError):
                get_data_dir()
