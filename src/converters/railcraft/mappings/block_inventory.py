"""
Inwentaryzacja bloków i Tile Entities moda Railcraft 9.12.2.0 (1.7.10).

Źródło prawdy: dekompilacja Railcraft_1.7.10-9.12.2.0.jar (Vineflower 1.10.1)
- mods/railcraft/common/blocks/RailcraftBlocks.java
- mods/railcraft/common/blocks/machine/*/EnumMachine*.java
- mods/railcraft/common/blocks/tracks/EnumTrack.java
- mods/railcraft/common/blocks/signals/EnumSignal.java
- mods/railcraft/common/blocks/detector/EnumDetector.java
- mods/railcraft/common/blocks/machine/MachineTileRegistery.java
- mods/railcraft/common/blocks/hidden/TileHidden.java

Uwaga: W NBT mapy 1.7.10 nazwy TileEntity ID to nazwy rejestrowane przez
GameRegistry.registerTileEntity (zob. MachineTileRegistery.java oraz
bezpośrednie rejestracje w blokach), a nie nazwy klas Java.
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# 1. TORY (BlockTrack + TileTrack / TileTrackTESR)
# ──────────────────────────────────────────────────────────────────────────────

# Wszystkie tory Railcrafta dzielą jeden blok railcraft.track (meta = EnumTrack.ordinal).
# Tile Entity: RailcraftTrackTile lub RailcraftTrackTESRTile.
# NBT zawiera "trackTag" (string, np. "railcraft:track.switch") lub "trackId" (short).
#
# UWAGA: W Railcrafcie 1.7.10 tory specjalne są TileEntity. Vanilla tory
# (minecraft:rail itp.) NIE są TE. Konwersja torów na Railcraft Reborn wymaga
# indywidualnego mapowania per trackTag.

RAILCRAFT_TRACKS: list[dict] = [
    # Deprecated / legacy (nieaktywne w configu domyślnym):
    {"meta": 0,  "tag": "railcraft:track.boarding",        "name": "Boarding Track",          "class": "TrackBoarding",         "deprecated": True},
    {"meta": 1,  "tag": "railcraft:track.holding",         "name": "Holding Track",           "class": "TrackHolding",          "deprecated": True},
    {"meta": 2,  "tag": "railcraft:track.oneway",          "name": "One-Way Track",           "class": "TrackOneWay"},
    {"meta": 3,  "tag": "railcraft:track.control",         "name": "Control Track",           "class": "TrackControl"},
    {"meta": 4,  "tag": "railcraft:track.launcher",        "name": "Launcher Track",          "class": "TrackLauncher"},
    {"meta": 5,  "tag": "railcraft:track.priming",         "name": "Priming Track",           "class": "TrackPriming"},
    {"meta": 6,  "tag": "railcraft:track.junction",        "name": "Junction Track",          "class": "TrackJunction"},
    {"meta": 7,  "tag": "railcraft:track.switch",          "name": "Switch Track",            "class": "TrackSwitch"},
    {"meta": 8,  "tag": "railcraft:track.disembarking",    "name": "Disembarking Track",      "class": "TrackDisembark"},
    {"meta": 9,  "tag": "railcraft:track.suspended",       "name": "Suspended Track",         "class": "TrackSuspended"},
    {"meta": 10, "tag": "railcraft:track.gated.oneway",    "name": "Gated One-Way Track",     "class": "TrackGatedOneWay"},
    {"meta": 11, "tag": "railcraft:track.gated",           "name": "Gated Track",             "class": "TrackGated"},
    {"meta": 12, "tag": "railcraft:track.slow",            "name": "Wooden Track",            "class": "TrackSlow"},
    {"meta": 13, "tag": "railcraft:track.slow.boost",      "name": "Wooden Booster Track",    "class": "TrackSlowBooster"},
    {"meta": 14, "tag": "railcraft:track.slow.junction",   "name": "Wooden Junction Track",   "class": "TrackSlowJunction"},
    {"meta": 15, "tag": "railcraft:track.slow.switch",     "name": "Wooden Switch Track",     "class": "TrackSlowSwitch"},
    {"meta": 16, "tag": "railcraft:track.speed",           "name": "High Speed Track",        "class": "TrackSpeed"},
    {"meta": 17, "tag": "railcraft:track.speed.boost",     "name": "High Speed Booster",      "class": "TrackSpeedBoost"},
    {"meta": 18, "tag": "railcraft:track.speed.transition","name": "High Speed Transition",   "class": "TrackSpeedTransition"},
    {"meta": 19, "tag": "railcraft:track.speed.switch",    "name": "High Speed Switch",       "class": "TrackSpeedSwitch"},
    {"meta": 20, "tag": "railcraft:track.boarding.train",  "name": "Train Boarding Track",    "class": "TrackBoardingTrain",    "deprecated": True},
    {"meta": 21, "tag": "railcraft:track.holding.train",   "name": "Train Holding Track",     "class": "TrackHoldingTrain",     "deprecated": True},
    {"meta": 22, "tag": "railcraft:track.coupler",         "name": "Coupler Track",           "class": "TrackCoupler"},
    {"meta": 23, "tag": "railcraft:track.decoupler",       "name": "Decoupler Track",         "class": "TrackCoupler",          "deprecated": True},
    {"meta": 24, "tag": "railcraft:track.reinforced",      "name": "Reinforced Track",        "class": "TrackReinforced"},
    {"meta": 25, "tag": "railcraft:track.reinforced.boost","name": "Reinforced Booster",      "class": "TrackReinforcedBooster"},
    {"meta": 26, "tag": "railcraft:track.reinforced.junction","name": "Reinforced Junction",  "class": "TrackReinforcedJunction"},
    {"meta": 27, "tag": "railcraft:track.reinforced.switch","name": "Reinforced Switch",      "class": "TrackReinforcedSwitch"},
    {"meta": 28, "tag": "railcraft:track.buffer.stop",     "name": "Buffer Stop Track",       "class": "TrackBufferStop"},
    {"meta": 29, "tag": "railcraft:track.disposal",        "name": "Disposal Track",          "class": "TrackDisposal"},
    {"meta": 30, "tag": "railcraft:track.detector.direction","name": "Detector Direction",    "class": "TrackDetectorDirection"},
    {"meta": 31, "tag": "railcraft:track.embarking",       "name": "Embarking Track",         "class": "TrackEmbarking"},
    {"meta": 32, "tag": "railcraft:track.wye",             "name": "Wye Track",               "class": "TrackWye"},
    {"meta": 33, "tag": "railcraft:track.slow.wye",        "name": "Wooden Wye Track",        "class": "TrackSlowWye"},
    {"meta": 34, "tag": "railcraft:track.reinforced.wye",  "name": "Reinforced Wye",          "class": "TrackReinforcedWye"},
    {"meta": 35, "tag": "railcraft:track.speed.wye",       "name": "High Speed Wye",          "class": "TrackSpeedWye"},
    {"meta": 36, "tag": "railcraft:track.lockdown",        "name": "Lockdown Track",          "class": "TrackLockdown",         "deprecated": True},
    {"meta": 37, "tag": "railcraft:track.lockdown.train",  "name": "Train Lockdown Track",    "class": "TrackLockdownTrain",    "deprecated": True},
    {"meta": 38, "tag": "railcraft:track.whistle",         "name": "Whistle Track",           "class": "TrackWhistle"},
    {"meta": 39, "tag": "railcraft:track.locomotive",      "name": "Locomotive Track",        "class": "TrackLocomotive"},
    {"meta": 40, "tag": "railcraft:track.limiter",         "name": "Limiter Track",           "class": "TrackLimiter"},
    {"meta": 41, "tag": "railcraft:track.routing",         "name": "Routing Track",           "class": "TrackRouting"},
    {"meta": 42, "tag": "railcraft:track.locking",         "name": "Locking Track",           "class": "TrackNextGenLocking"},
    {"meta": 43, "tag": "railcraft:track.electric",        "name": "Electric Track",          "class": "TrackElectric"},
    {"meta": 44, "tag": "railcraft:track.electric.junction","name": "Electric Junction",      "class": "TrackElectricJunction"},
    {"meta": 45, "tag": "railcraft:track.electric.switch", "name": "Electric Switch",         "class": "TrackElectricSwitch"},
    {"meta": 46, "tag": "railcraft:track.electric.wye",    "name": "Electric Wye",            "class": "TrackElectricWye"},
    {"meta": 47, "tag": "railcraft:track.force",           "name": "Force Track",             "class": "TrackForce"},
]

# Tory dzielą 2 klasy TileEntity:
# - TileTrack        -> ID "RailcraftTrackTile"
# - TileTrackTESR    -> ID "RailcraftTrackTESRTile" (dziedziczy po TileTrack, max render distance = 32767)
RAILCRAFT_TRACK_TE = {
    "RailcraftTrackTile": "TileTrack",
    "RailcraftTrackTESRTile": "TileTrackTESR",
}

# ──────────────────────────────────────────────────────────────────────────────
# 2. MASZYNY ALPHA (railcraft.machine.alpha, meta 0-15)
# ──────────────────────────────────────────────────────────────────────────────

RAILCRAFT_MACHINE_ALPHA: list[dict] = [
    {"meta": 0,  "tag": "tile.railcraft.machine.alpha.anchor.world",      "name": "World Anchor",         "te_class": "TileAnchorWorld",      "te_id": "RCWorldAnchorTile"},
    {"meta": 1,  "tag": "tile.railcraft.machine.alpha.turbine",           "name": "Steam Turbine",        "te_class": "TileSteamTurbine",     "te_id": "RCSteamTurbineTile"},
    {"meta": 2,  "tag": "tile.railcraft.machine.alpha.anchor.personal",   "name": "Personal Anchor",      "te_class": "TileAnchorPersonal",   "te_id": "RCPersonalAnchorTile"},
    {"meta": 3,  "tag": "tile.railcraft.machine.alpha.steam.oven",        "name": "Steam Oven",           "te_class": "TileSteamOven",        "te_id": "RCSteamOvenTile"},
    {"meta": 4,  "tag": "tile.railcraft.machine.alpha.anchor.admin",      "name": "Admin Anchor",         "te_class": "TileAnchorAdmin",      "te_id": "RCAdminAnchorTile"},
    {"meta": 5,  "tag": "tile.railcraft.machine.alpha.smoker",            "name": "Smoker",               "te_class": "TileSmoker",           "te_id": "RCSmokerTile"},
    {"meta": 6,  "tag": "tile.railcraft.machine.alpha.trade.station",     "name": "Trade Station",        "te_class": "TileTradeStation",     "te_id": "RCTradeStationTile"},
    {"meta": 7,  "tag": "tile.railcraft.machine.alpha.coke.oven",         "name": "Coke Oven",            "te_class": "TileCokeOven",         "te_id": "RCCokeOvenTile"},
    {"meta": 8,  "tag": "tile.railcraft.machine.alpha.rolling.machine",   "name": "Rolling Machine",      "te_class": "TileRollingMachine",   "te_id": "RCRollingMachineTile"},
    {"meta": 9,  "tag": "tile.railcraft.machine.alpha.steam.trap",        "name": "Steam Trap",           "te_class": "TileSteamTrapManual",  "te_id": "RCSteamTrapManualTile"},
    {"meta": 10, "tag": "tile.railcraft.machine.alpha.steam.trap.auto",   "name": "Auto Steam Trap",      "te_class": "TileSteamTrapAuto",    "te_id": "RCSteamTrapAutoTile"},
    {"meta": 11, "tag": "tile.railcraft.machine.alpha.feed.station",      "name": "Feed Station",         "te_class": "TileFeedStation",      "te_id": "RCFeedStationTile"},
    {"meta": 12, "tag": "tile.railcraft.machine.alpha.blast.furnace",     "name": "Blast Furnace",        "te_class": "TileBlastFurnace",     "te_id": "RCBlastFurnaceTile"},
    {"meta": 13, "tag": "tile.railcraft.machine.alpha.anchor.passive",    "name": "Passive Anchor",       "te_class": "TileAnchorPassive",    "te_id": "RCPassiveAnchorTile"},
    {"meta": 14, "tag": "tile.railcraft.machine.alpha.tank.water",        "name": "Water Tank Siding",    "te_class": "TileTankWater",        "te_id": "RCWaterTankTile"},
    {"meta": 15, "tag": "tile.railcraft.machine.alpha.rock.crusher",      "name": "Rock Crusher",         "te_class": "TileRockCrusher",      "te_id": "RCRockCrusherTile"},
]

# ──────────────────────────────────────────────────────────────────────────────
# 3. MASZYNY BETA (railcraft.machine.beta, meta 0-15)
# ──────────────────────────────────────────────────────────────────────────────

RAILCRAFT_MACHINE_BETA: list[dict] = [
    {"meta": 0,  "tag": "tile.railcraft.machine.beta.tank.iron.wall",       "name": "Iron Tank Wall",         "te_class": "TileTankIronWall",       "te_id": "RCIronTankWallTile"},
    {"meta": 1,  "tag": "tile.railcraft.machine.beta.tank.iron.gauge",      "name": "Iron Tank Gauge",        "te_class": "TileTankIronGauge",      "te_id": "RCIronTankGaugeTile"},
    {"meta": 2,  "tag": "tile.railcraft.machine.beta.tank.iron.valve",      "name": "Iron Tank Valve",        "te_class": "TileTankIronValve",      "te_id": "RCIronTankValveTile"},
    {"meta": 3,  "tag": "tile.railcraft.machine.beta.boiler.tank.pressure.low",  "name": "Low Pressure Boiler Tank", "te_class": "TileBoilerTankLow",  "te_id": "RCBoilerTankLowTile"},
    {"meta": 4,  "tag": "tile.railcraft.machine.beta.boiler.tank.pressure.high", "name": "High Pressure Boiler Tank","te_class": "TileBoilerTankHigh", "te_id": "RCBoilerTankHighTile"},
    {"meta": 5,  "tag": "tile.railcraft.machine.beta.boiler.firebox.solid", "name": "Solid Fueled Firebox",   "te_class": "TileBoilerFireboxSolid", "te_id": "RCBoilerFireboxSoildTile"},
    {"meta": 6,  "tag": "tile.railcraft.machine.beta.boiler.firebox.liquid","name": "Liquid Fueled Firebox",  "te_class": "TileBoilerFireboxFluid", "te_id": "RCBoilerFireboxLiquidTile"},
    {"meta": 7,  "tag": "tile.railcraft.machine.beta.engine.steam.hobby",   "name": "Hobbyist Steam Engine",  "te_class": "TileEngineSteamHobby",   "te_id": "RCEngineSteamHobby"},
    {"meta": 8,  "tag": "tile.railcraft.machine.beta.engine.steam.low",     "name": "Commercial Steam Engine","te_class": "TileEngineSteamLow",     "te_id": "RCEngineSteamLow"},
    {"meta": 9,  "tag": "tile.railcraft.machine.beta.engine.steam.high",    "name": "Industrial Steam Engine","te_class": "TileEngineSteamHigh",    "te_id": "RCEngineSteamHigh"},
    {"meta": 10, "tag": "tile.railcraft.machine.beta.anchor.sentinel",      "name": "Anchor Sentinel",        "te_class": "TileSentinel",           "te_id": "RCAnchorSentinelTile"},
    {"meta": 11, "tag": "tile.railcraft.machine.beta.chest.void",           "name": "Void Chest",             "te_class": "TileChestVoid",          "te_id": "RCVoidChestTile"},
    {"meta": 12, "tag": "tile.railcraft.machine.beta.chest.metals",         "name": "Metals Chest",           "te_class": "TileChestMetals",        "te_id": "RCMetalsChestTile"},
    {"meta": 13, "tag": "tile.railcraft.machine.beta.tank.steel.wall",      "name": "Steel Tank Wall",        "te_class": "TileTankSteelWall",      "te_id": "RCSteelTankWallTile"},
    {"meta": 14, "tag": "tile.railcraft.machine.beta.tank.steel.gauge",     "name": "Steel Tank Gauge",       "te_class": "TileTankSteelGauge",     "te_id": "RCSteelTankGaugeTile"},
    {"meta": 15, "tag": "tile.railcraft.machine.beta.tank.steel.valve",     "name": "Steel Tank Valve",       "te_class": "TileTankSteelValve",     "te_id": "RCSteelTankValveTile"},
]

# ──────────────────────────────────────────────────────────────────────────────
# 4. MASZYNY GAMMA (railcraft.machine.gamma, meta 0-11)
# ──────────────────────────────────────────────────────────────────────────────

RAILCRAFT_MACHINE_GAMMA: list[dict] = [
    {"meta": 0,  "tag": "tile.railcraft.machine.gamma.loader.item",           "name": "Item Loader",            "te_class": "TileItemLoader",         "te_id": "RCLoaderTile"},
    {"meta": 1,  "tag": "tile.railcraft.machine.gamma.unloader.item",         "name": "Item Unloader",          "te_class": "TileItemUnloader",       "te_id": "RCUnloaderTile"},
    {"meta": 2,  "tag": "tile.railcraft.machine.gamma.loader.item.advanced",  "name": "Adv. Item Loader",       "te_class": "TileItemLoaderAdvanced", "te_id": "RCLoaderAdvancedTile"},
    {"meta": 3,  "tag": "tile.railcraft.machine.gamma.unloader.item.advanced","name": "Adv. Item Unloader",     "te_class": "TileItemUnloaderAdvanced","te_id": "RCUnloaderAdvancedTile"},
    {"meta": 4,  "tag": "tile.railcraft.machine.gamma.loader.liquid",         "name": "Fluid Loader",           "te_class": "TileFluidLoader",        "te_id": "RCLoaderTileLiquid"},
    {"meta": 5,  "tag": "tile.railcraft.machine.gamma.unloader.liquid",       "name": "Fluid Unloader",         "te_class": "TileFluidUnloader",      "te_id": "RCUnloaderTileLiquid"},
    {"meta": 6,  "tag": "tile.railcraft.machine.gamma.loader.energy",         "name": "Energy Loader (IC2)",    "te_class": "TileEnergyLoader",       "te_id": "RCLoaderTileEnergy"},
    {"meta": 7,  "tag": "tile.railcraft.machine.gamma.unloader.energy",       "name": "Energy Unloader (IC2)",  "te_class": "TileEnergyUnloader",     "te_id": "RCUnloaderTileEnergy"},
    {"meta": 8,  "tag": "tile.railcraft.machine.gamma.dispenser.cart",        "name": "Cart Dispenser",         "te_class": "TileDispenserCart",      "te_id": "RCMinecartDispenserTile"},
    {"meta": 9,  "tag": "tile.railcraft.machine.gamma.dispenser.train",       "name": "Train Dispenser",        "te_class": "TileDispenserTrain",     "te_id": "RCTrainDispenserTile"},
    {"meta": 10, "tag": "tile.railcraft.machine.gamma.loader.rf",             "name": "RF Loader",              "te_class": "TileRFLoader",           "te_id": "RCLoaderTileRF"},
    {"meta": 11, "tag": "tile.railcraft.machine.gamma.unloader.rf",           "name": "RF Unloader",            "te_class": "TileRFUnloader",         "te_id": "RCUnloaderTileRF"},
]

# ──────────────────────────────────────────────────────────────────────────────
# 5. MASZYNY DELTA (railcraft.machine.delta, meta 0-1)
# ──────────────────────────────────────────────────────────────────────────────

RAILCRAFT_MACHINE_DELTA: list[dict] = [
    {"meta": 0, "tag": "tile.railcraft.machine.delta.wire",  "name": "Electric Shunting Wire", "te_class": "TileWire",  "te_id": "RCWireTile"},
    {"meta": 1, "tag": "tile.railcraft.machine.delta.cage",  "name": "Spawner Refill",         "te_class": "TileCage",  "te_id": "RCCageTile"},
]

# ──────────────────────────────────────────────────────────────────────────────
# 6. MASZYNY EPSILON (railcraft.machine.epsilon, meta 0-5)
# ──────────────────────────────────────────────────────────────────────────────

RAILCRAFT_MACHINE_EPSILON: list[dict] = [
    {"meta": 0, "tag": "tile.railcraft.machine.epsilon.electric.feeder",      "name": "Electric Feeder",        "te_class": "TileElectricFeeder",      "te_id": "RCElectricFeederTile"},
    {"meta": 1, "tag": "tile.railcraft.machine.epsilon.electric.feeder.admin","name": "Admin Electric Feeder",  "te_class": "TileElectricFeederAdmin", "te_id": "RCElectricFeederAdminTile"},
    {"meta": 2, "tag": "tile.railcraft.machine.epsilon.admin.steam.producer", "name": "Admin Steam Producer",   "te_class": "TileAdminSteamProducer",  "te_id": "RCAdminSteamProducerTile"},
    {"meta": 3, "tag": "tile.railcraft.machine.epsilon.force.track.emitter",  "name": "Force Track Emitter",    "te_class": "TileForceTrackEmitter",   "te_id": "RCForceTrackEmitterTile"},
    {"meta": 4, "tag": "tile.railcraft.machine.epsilon.flux.transformer",     "name": "Flux Transformer",       "te_class": "TileFluxTransformer",     "te_id": "RCFluxTransformerTile"},
    {"meta": 5, "tag": "tile.railcraft.machine.epsilon.engraving.bench",      "name": "Engraving Bench",        "te_class": "TileEngravingBench",      "te_id": "RCEngravingBenchTile"},
]

# ──────────────────────────────────────────────────────────────────────────────
# 7. SYGNAŁY (BlockSignalRailcraft, meta z EnumSignal 0-13)
# ──────────────────────────────────────────────────────────────────────────────

RAILCRAFT_SIGNALS: list[dict] = [
    {"meta": 0,  "tag": "tile.railcraft.signal.box.interlock",       "name": "Interlock Box",            "te_class": "TileBoxInterlock",            "te_id": "RCTileStructureInterlockBox"},
    {"meta": 1,  "tag": "tile.railcraft.signal.block.signal.dual",   "name": "Dual-Head Block Signal",   "te_class": "TileSignalDualHeadBlockSignal", "te_id": "RCTileStructureDualHeadBlockSignal"},
    {"meta": 2,  "tag": "tile.railcraft.signal.switch.motor",        "name": "Switch Motor",             "te_class": "TileSwitchMotor",             "te_id": "RCTileStructureSwitchMotor"},
    {"meta": 3,  "tag": "tile.railcraft.signal.block.signal",        "name": "Block Signal",             "te_class": "TileSignalBlockSignal",       "te_id": "RCTileStructureBlockSignal"},
    {"meta": 4,  "tag": "tile.railcraft.signal.switch.lever",        "name": "Switch Lever",             "te_class": "TileSwitchLever",             "te_id": "RCTileStructureSwitchLever"},
    {"meta": 5,  "tag": "tile.railcraft.signal.switch.routing",      "name": "Routing Switch Motor",     "te_class": "TileSwitchRouting",           "te_id": "RCTileStructureSwitchRouting"},
    {"meta": 6,  "tag": "tile.railcraft.signal.box.sequencer",       "name": "Sequencer Box",            "te_class": "TileBoxSequencer",            "te_id": "RCTileStructureSequencerBox"},
    {"meta": 7,  "tag": "tile.railcraft.signal.box.capacitor",       "name": "Capacitor Box",            "te_class": "TileBoxCapacitor",            "te_id": "RCTileStructureCapacitorBox"},
    {"meta": 8,  "tag": "tile.railcraft.signal.box.receiver",        "name": "Receiver Box",             "te_class": "TileBoxReceiver",             "te_id": "RCTileStructureReceiverBox"},
    {"meta": 9,  "tag": "tile.railcraft.signal.box.controller",      "name": "Controller Box",           "te_class": "TileBoxController",           "te_id": "RCTileStructureControllerBox"},
    {"meta": 10, "tag": "tile.railcraft.signal.box.analog",          "name": "Analog Controller Box",    "te_class": "TileBoxAnalogController",     "te_id": "RCTileStructureAnalogBox"},
    {"meta": 11, "tag": "tile.railcraft.signal.distant",             "name": "Distant Signal",           "te_class": "TileSignalDistantSignal",     "te_id": "RCTileStructureDistantSignal"},
    {"meta": 12, "tag": "tile.railcraft.signal.distant.dual",        "name": "Dual-Head Distant Signal", "te_class": "TileSignalDualHeadDistantSignal", "te_id": "RCTileStructureDualHeadDistantSignal"},
    {"meta": 13, "tag": "tile.railcraft.signal.box.block.relay",     "name": "Signal Block Relay",       "te_class": "TileBoxBlockRelay",           "te_id": "RCTileStructureSignalBox"},
]

# ──────────────────────────────────────────────────────────────────────────────
# 8. DETEKTORY (railcraft.detector, meta z EnumDetector 0-16)
# ──────────────────────────────────────────────────────────────────────────────

RAILCRAFT_DETECTORS: list[dict] = [
    {"meta": 0,  "tag": "tile.railcraft.detector.item",        "name": "Detector - Item",         "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 1,  "tag": "tile.railcraft.detector.any",         "name": "Detector - Any",          "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 2,  "tag": "tile.railcraft.detector.empty",       "name": "Detector - Empty",        "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 3,  "tag": "tile.railcraft.detector.mob",         "name": "Detector - Mob",          "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 4,  "tag": "tile.railcraft.detector.powered",     "name": "Detector - Powered",      "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 5,  "tag": "tile.railcraft.detector.player",      "name": "Detector - Player",       "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 6,  "tag": "tile.railcraft.detector.explosive",   "name": "Detector - Explosive",    "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 7,  "tag": "tile.railcraft.detector.animal",      "name": "Detector - Animal",       "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 8,  "tag": "tile.railcraft.detector.tank",        "name": "Detector - Tank",         "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 9,  "tag": "tile.railcraft.detector.advanced",    "name": "Detector - Advanced",     "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 10, "tag": "tile.railcraft.detector.energy",      "name": "Detector - Energy (IC2)", "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 11, "tag": "tile.railcraft.detector.age",         "name": "Detector - Age",          "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 12, "tag": "tile.railcraft.detector.train",       "name": "Detector - Train",        "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 13, "tag": "tile.railcraft.detector.sheep",       "name": "Detector - Sheep",        "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 14, "tag": "tile.railcraft.detector.villager",    "name": "Detector - Villager",     "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 15, "tag": "tile.railcraft.detector.locomotive",  "name": "Detector - Locomotive",   "te_class": "TileDetector", "te_id": "RCDetectorTile"},
    {"meta": 16, "tag": "tile.railcraft.detector.routing",     "name": "Detector - Routing",      "te_class": "TileDetector", "te_id": "RCDetectorTile"},
]

# ──────────────────────────────────────────────────────────────────────────────
# 9. POZOSTAŁE BLOKI (bez TileEntity lub z prostym TE)
# ──────────────────────────────────────────────────────────────────────────────

RAILCRAFT_OTHER_BLOCKS: list[dict] = [
    {"block_id": "railcraft.residual.heat",   "name": "Residual Heat (Trail)",     "te_id": "RCHiddenTile",       "note": "IGNOROWANE - ślad gracza Railcrafta"},
    {"block_id": "railcraft.track.elevator",  "name": "Elevator Track",            "te_id": None,                 "note": "Brak TE"},
    {"block_id": "railcraft.frame",           "name": "Track Kit Frame",           "te_id": None},
    {"block_id": "railcraft.cube",            "name": "Cube Blocks",               "te_id": None,                 "note": "meta: coke, concrete, steel, infernal brick, crushed obsidian, sandy brick, abyssal stone, quarried stone, creosote, copper, tin, lead"},
    {"block_id": "railcraft.ore",             "name": "Ores",                      "te_id": None,                 "note": "meta: sulfur, saltpeter, dark diamond, dark emerald, dark lapis, firestone, waterstone, poor iron/gold/copper/tin/lead"},
    {"block_id": "railcraft.glass",           "name": "Strength Glass",            "te_id": None},
    {"block_id": "railcraft.brick.*",         "name": "Brick Blocks",              "te_id": None,                 "note": "Wiele wariantów per theme"},
    {"block_id": "railcraft.post",            "name": "Post",                      "te_id": "RCPostEmblemTile",   "note": "Emblem variant only"},
    {"block_id": "railcraft.post.metal.*",    "name": "Metal Post",                "te_id": None},
    {"block_id": "railcraft.slab",            "name": "Slabs",                     "te_id": "RCSlabTile"},
    {"block_id": "railcraft.stair",           "name": "Stairs",                    "te_id": "RCStairTile"},
    {"block_id": "railcraft.wall.alpha",      "name": "Alpha Walls",               "te_id": None},
    {"block_id": "railcraft.wall.beta",       "name": "Beta Walls",                "te_id": None},
    {"block_id": "railcraft.lantern.stone",   "name": "Stone Lanterns",            "te_id": None},
    {"block_id": "railcraft.lantern.metal",   "name": "Metal Lanterns",            "te_id": None},
    {"block_id": "railcraft.anvil",           "name": "Steel Anvil",               "te_id": None},
    {"block_id": "railcraft.worldlogic",      "name": "World Logic (worldspike)",  "te_id": None},
]

# ──────────────────────────────────────────────────────────────────────────────
# 10. AGREGATY
# ──────────────────────────────────────────────────────────────────────────────

ALL_RAILCRAFT_TE_IDS: set[str] = set()
for table in (RAILCRAFT_MACHINE_ALPHA, RAILCRAFT_MACHINE_BETA, RAILCRAFT_MACHINE_GAMMA,
              RAILCRAFT_MACHINE_DELTA, RAILCRAFT_MACHINE_EPSILON, RAILCRAFT_SIGNALS,
              RAILCRAFT_DETECTORS):
    for entry in table:
        te_id = entry.get("te_id")
        if te_id:
            ALL_RAILCRAFT_TE_IDS.add(te_id)

# Tory
ALL_RAILCRAFT_TE_IDS.update(RAILCRAFT_TRACK_TE.keys())
# Inne
ALL_RAILCRAFT_TE_IDS.add("RCHiddenTile")
ALL_RAILCRAFT_TE_IDS.add("RCPostEmblemTile")
ALL_RAILCRAFT_TE_IDS.add("RCSlabTile")
ALL_RAILCRAFT_TE_IDS.add("RCStairTile")
ALL_RAILCRAFT_TE_IDS.add("RCFirestoneRechargeTile")

# Ignorowane TE (nie konwertujemy)
RAILCRAFT_IGNORED_TE_IDS: set[str] = {
    "RCHiddenTile",  # Residual Heat / ślad gracza Railcrafta
}

# Bloki które wymagają konwersji TileEntity
RAILCRAFT_BLOCKS_WITH_TE: list[str] = [
    "railcraft.track",
    "railcraft.machine.alpha",
    "railcraft.machine.beta",
    "railcraft.machine.gamma",
    "railcraft.machine.delta",
    "railcraft.machine.epsilon",
    # Sygnały i detektory mają osobne bloki, ale NBT przechowuje je jako BlockSignalRailcraft / BlockDetector
]

# Suma statystyk
RAILCRAFT_BLOCK_REGISTRATIONS = len(RAILCRAFT_TRACKS) + len(RAILCRAFT_MACHINE_ALPHA) + len(RAILCRAFT_MACHINE_BETA) + len(RAILCRAFT_MACHINE_GAMMA) + len(RAILCRAFT_MACHINE_DELTA) + len(RAILCRAFT_MACHINE_EPSILON) + len(RAILCRAFT_SIGNALS) + len(RAILCRAFT_DETECTORS) + len(RAILCRAFT_OTHER_BLOCKS)
RAILCRAFT_TE_CLASSES = len(ALL_RAILCRAFT_TE_IDS)
