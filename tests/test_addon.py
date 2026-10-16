"""The add-on's content loads into the example game when the operator lists it, and not otherwise."""

from dataclasses import replace

import pytest
from sqlalchemy import select
from terraforma.addons import integrate
from terraforma.content.models import Ability, Item, Job
from terraforma.content.schema import check_seed
from terraforma.example import GAME
from terraforma.fights.rules import Rules
from terraforma.testing import in_app_db

from example_addon import ADDON

ITEMS = {"trail_ration", "campfire_tea", "walking_staff", "wayfarer_cloak"}
ABILITIES = {"second_wind", "trip_wire", "forage"}


def rows(client, model):
    async def read(session):
        return {row.key: row for row in (await session.scalars(select(model))).all()}

    return in_app_db(client, read)


def test_the_merged_seed_passes_the_engines_checks():
    # Everything the add-on's rows name (statuses, jobs, abilities) exists in the game or in the add-on.
    game = replace(GAME, addons=(ADDON,))
    layered = integrate(game, ["wayfarer_pack"]).load_seed()
    rules = Rules()
    check_seed(layered.rows, rules.stats, rules.resource_names)
    assert {row["key"] for row in layered.rows["items"] if layered.owners["items"][row["key"]] == "wayfarer_pack"} == ITEMS


def test_listing_the_add_on_adds_its_content(app_client):
    items, abilities, jobs = rows(app_client, Item), rows(app_client, Ability), rows(app_client, Job)
    assert ITEMS <= items.keys() and ABILITIES <= abilities.keys()
    assert [entry["ability"] for entry in jobs["wayfarer"].abilities] == ["second_wind", "forage"]


def test_the_add_on_teaches_the_games_scout_a_new_ability(app_client):
    scout = {entry["ability"]: entry["level"] for entry in rows(app_client, Job)["scout"].abilities}
    assert scout["trip_wire"] == 3
    assert {"poison_dart", "daze"} <= scout.keys()  # (what the game gave the scout is still there)


@pytest.mark.parametrize("addons", [[]])
def test_unlisted_the_add_on_adds_nothing(app_client):
    assert not (ITEMS & rows(app_client, Item).keys())
    assert "wayfarer" not in rows(app_client, Job)
    assert "trip_wire" not in {entry["ability"] for entry in rows(app_client, Job)["scout"].abilities}
