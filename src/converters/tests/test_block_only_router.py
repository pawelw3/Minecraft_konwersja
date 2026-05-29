from converters.block_only_router import convert_block_only


def test_router_dispatches_mekanism():
    result = convert_block_only(2159, "Mekanism:OreBlock", 2, (0, 64, 0))
    assert result.success
    assert result.target_block == "mekanism:tin_ore"


def test_router_dispatches_extrautils():
    result = convert_block_only(1955, "ExtraUtilities:angelBlock", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "angelblockrenewed:angel_block"


def test_router_unknown_mod_never_air():
    result = convert_block_only(3000, "SomeMod:decor", 4, (0, 64, 0))
    assert result.success
    assert result.target_block != "minecraft:air"
    assert result.confidence == "low"


def test_router_dispatches_reliquary():
    result = convert_block_only(3192, "xreliquary:lilypad", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "reliquary:fertile_lily_pad"


def test_router_dispatches_thermal():
    result = convert_block_only(962, "ThermalFoundation:Ore", 1, (0, 64, 0))
    assert result.success
    assert result.target_block == "thermal:tin_ore"


def test_router_dispatches_witchery():
    result = convert_block_only(3687, "witchery:shadedglass", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:tinted_glass"


def test_router_dispatches_ae2():
    result = convert_block_only(432, "appliedenergistics2:tile.blockquartz", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "ae2:quartz_block"


def test_router_dispatches_bibliocraft():
    result = convert_block_only(1234, "BiblioCraft:bell", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:bell"


def test_router_dispatches_bigreactors():
    result = convert_block_only(987, "bigreactors:yelloriteore", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "biggerreactors:uranium_ore"


def test_router_dispatches_bloodmagic():
    result = convert_block_only(876, "AWWayofTime:bloodRune", 2, (0, 64, 0))
    assert result.success
    assert result.target_block == "bloodmagic:capacity_rune"


def test_router_dispatches_buildcraft():
    result = convert_block_only(765, "BuildCraft|Builders:blockFrame", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "minecraft:iron_bars"


def test_router_dispatches_chisel():
    result = convert_block_only(654, "chisel:andesite", 0, (0, 64, 0))
    assert result.success
    assert result.target_block == "rechiseled:andesite_1"
