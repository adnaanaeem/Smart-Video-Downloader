# tests/conftest.py
# Shared pytest fixtures: a headless QApplication, plus loaders for the format-JSON fixtures.

import json
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def make_window(qapp):
    """Returns a factory that builds a fresh SmartVideoDownloader instance per test."""
    import main

    def _make():
        return main.SmartVideoDownloader()

    return _make


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as f:
        return json.load(f)
