"""The add-on's content loads into the example game when the operator lists it, starts off, and an admin can switch it on."""

from dataclasses import replace

import pytest
from sqlalchemy import select
from terraforma.addons import integrate
from terraforma.content.models import Ability, Item, Job
from terraforma.content.schema import check_seed
from terraforma.example import GAME
from terraforma.fights.rules import Rules
from terraforma.gamestate.components import Components
from terraforma.testing import in_app_db

from example_addon import ADDON

KEY = "wayfarer_pack"
ITEMS = {"trail_ration", "campfire_tea", "walking_staff", "wayfarer_cloak"}
ABILITIES = {"second_wind", "trip_wire", "forage"}


@pytest.fixture
def listed():
    return replace(GAME, addons=(ADDON,))


@pytest.fixture
def components(listed):
    return Components(integrate(listed, [KEY]), listed)


def rows(client, model):
    async def read(session):
        return {row.key: row for row in (await session.scalars(select(model))).all()}

    return in_app_db(client, read)


def test_the_merged_seed_passes_the_engines_checks(listed):
    # Everything the add-on's rows name (statuses, abilities) exists in the game or in the add-on, and every section a row names is declared.
    layered = integrate(listed, [KEY]).load_seed()
    rules = Rules()
    check_seed(layered.rows, rules.stats, rules.resource_names)
    assert {row["key"] for row in layered.rows["items"] if layered.owners["items"][row["key"]] == KEY} == ITEMS


def test_listing_the_add_on_adds_its_content_switched_off(app_client):
    items, abilities, jobs = rows(app_client, Item), rows(app_client, Ability), rows(app_client, Job)
    assert ITEMS <= items.keys() and ABILITIES <= abilities.keys() and "wayfarer" in jobs
    assert [entry["ability"] for entry in jobs["wayfarer"].abilities] == ["second_wind", "trip_wire", "forage"]
    # Components start off: nothing of the add-on is offered until an admin commits a state that turns it on.
    assert not any(items[key].active for key in ITEMS) and not any(abilities[key].active for key in ABILITIES)
    assert not jobs["wayfarer"].active
    assert all(items[key].active for key in ("herb", "short_sword")), "(the game's own rows are untouched)"


def test_the_whole_add_on_can_be_switched_on(components):
    assert components.check(components.default(), {}) == []
    whole = components.switch(components.default(), KEY, True)
    assert components.check(whole, {}) == []
    assert set(whole["states"][KEY]) == {"items", "abilities", "jobs"}


def test_a_job_cannot_be_on_while_its_abilities_are_off(components):
    # The wayfarer needs second_wind, trip_wire and forage, so switching only the job on is refused, naming what is missing.
    job_only = {"states": {KEY: {"jobs": {"wayfarer": "on"}}}}
    problems = components.check(job_only, {})
    assert [problem.split("needs abilities ")[1] for problem in problems] == ["'second_wind', which is off", "'trip_wire', which is off", "'forage', which is off"]
    with_abilities = components.switch(components.switch(components.default(), KEY, True, "abilities"), KEY, True, "jobs")
    assert components.check(with_abilities, {}) == []


def test_sections_switch_together(components):
    supplies = components.switch(components.default(), KEY, True, "items", "supplies")
    assert supplies["states"][KEY]["items"] == {"trail_ration": "on", "campfire_tea": "on"}
    snares = components.switch(components.default(), KEY, True, "abilities", "snares")
    assert snares["states"][KEY]["abilities"] == {"trip_wire": "on"}
    assert components.switch(supplies, KEY, False, "items", "supplies") == components.default()


@pytest.mark.parametrize("addons", [[]])
def test_unlisted_the_add_on_adds_nothing(app_client):
    assert not (ITEMS & rows(app_client, Item).keys())
    assert "wayfarer" not in rows(app_client, Job)
