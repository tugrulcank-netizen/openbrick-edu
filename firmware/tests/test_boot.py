# Tests for boot module
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock import MagicMock, patch
from firmware.boot.manager import BootManager


class TestBootManager:
    def test_boot_manager_creates_with_defaults(self):
        bm = BootManager()
        assert bm.ready is False

    def test_boot_sequence_sets_ready(self):
        bm = BootManager()
        bm.matrix = MagicMock()
        bm.ble = MagicMock()
        bm.run()
        assert bm.ready is True

    def test_boot_sequence_initializes_matrix(self):
        bm = BootManager()
        bm.matrix = MagicMock()
        bm.ble = MagicMock()
        bm.run()
        bm.matrix.init.assert_called_once()

    def test_boot_sequence_initializes_ble(self):
        bm = BootManager()
        bm.matrix = MagicMock()
        bm.ble = MagicMock()
        bm.run()
        bm.ble.init.assert_called_once()

    def test_boot_sequence_shows_splash(self):
        bm = BootManager()
        bm.matrix = MagicMock()
        bm.ble = MagicMock()
        bm.run()
        bm.matrix.splash.assert_called_once()

    def test_boot_fails_if_ble_init_fails(self):
        bm = BootManager()
        bm.matrix = MagicMock()
        bm.ble = MagicMock()
        bm.ble.init.return_value = False
        bm.run()
        assert bm.ready is False
