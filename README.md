# TerraForma example add-on

A small add-on for the [TerraForma RPG Engine](https://github.com/wilminator/terraforma), here to show what an add-on is and to test that one works when installed on its own.

An add-on adds content to a game without being a game. This one, **Wayfarer's Pack** (`wayfarer_pack`), brings:

- a job, `wayfarer`, with two abilities (`seed/jobs.json`, `seed/abilities.json`);
- four items (`seed/items/supplies.json`, `seed/items/gear.json`), one of them wearable only by the new job;
- one more ability for a job the game already has (`seed/job_abilities.json`: the game's `scout` learns `trip_wire` at level 3).

Its seed is split into a file per kind, and `items` into a folder of files, to show both layouts (engine README, "Seed data").

## Using it

The engine never imports an add-on. The **game** lists the add-ons it supports and the **operator** turns them on:

```python
from terraforma.game import Game
from example_addon import ADDON

GAME = Game(name="My Game", seed_dir=..., addons=(ADDON,))
```

```toml
# settings.toml
addons = ["wayfarer_pack"]
```

The add-on's keys must not clash with the game's (the server refuses to start naming both), and rows may name the game's content: this one uses the game's `slowed` status and `scout` job. It needs a game that has them, such as the engine's own example game.

## Tests

```sh
pip install -e ".[dev]"
pytest
```

The tests serve the engine's example game with this add-on listed, and check that the merged seed passes the engine's checks, that the content is loaded when the add-on is listed, and that nothing is added when it is not.

## Licenses

MIT, so you can copy any of it into your own add-on. It has no art or sound yet; when it does, each file's source and license go in `assets/ASSETS.md` (the engine refuses an add-on's assets without it).
