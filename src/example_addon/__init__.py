"""An example add-on for the TerraForma RPG Engine: a few items, a job and some abilities.

An add-on is content without a game: a seed folder (and, when it has art or sound, an assets folder) handed to the engine as an
``AddOn``. The engine never imports it. A game lists the add-ons it supports (``Game(addons=(ADDON,))``) and the operator turns
one on in ``settings.toml`` (``addons = ["wayfarer_pack"]``). Its components start off; an admin switches them on.
"""

from pathlib import Path

from terraforma.addons import AddOn, SectionNode

HERE = Path(__file__).parent

# The tree an admin sees under each kind: a switch for every level (a row says where it sits with "section" in the seed).
ADDON = AddOn(
    key="wayfarer_pack",
    name="Wayfarer's Pack",
    seed_dir=HERE / "seed",
    sections={
        "items": (SectionNode("supplies", "Supplies"), SectionNode("gear", "Gear")),
        "abilities": (SectionNode("camp", "Camp skills"), SectionNode("snares", "Snares")),
    },
)
