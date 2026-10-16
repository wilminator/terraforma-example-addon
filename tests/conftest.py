"""The tests run the engine's example game with this add-on listed in its settings."""

from dataclasses import replace

import pytest

pytest_plugins = ["terraforma.testing"]


@pytest.fixture
def game():
    from terraforma.example import GAME

    from example_addon import ADDON

    return replace(GAME, addons=(ADDON,))


@pytest.fixture
def addons():
    return ["wayfarer_pack"]
