"""Open Modular Turrets 1.7.10 – static mappings for the converter."""
from __future__ import annotations

# All 1.7.10 TileEntity string IDs registered by OMT (from TileEntityHandler.java).
# Includes the lowercase "turretbase" variant that may appear in older saves.
OMT_TE_IDS: frozenset[str] = frozenset([
    # Bases (5 tiers)
    "turretbase",
    "turretWoodBase",
    "turretBaseOne",
    "turretBaseTwo",
    "turretBaseThree",
    "turretBaseFour",
    # Heads (10 types)
    "disposableItemTurret",
    "potatoCannonTurret",
    "machineGunTurret",
    "incendiaryTurret",
    "grenadeTurret",
    "relativisticTurret",
    "rocketTurret",
    "teleporterTurret",
    "laserTurret",
    "railGunTurret",
    # Power expanders (5 tiers)
    "expanderPowerTierOne",
    "expanderPowerTierTwo",
    "expanderPowerTierThree",
    "expanderPowerTierFour",
    "expanderPowerTierFive",
    # Inventory expanders (5 tiers)
    "expanderInvTierOne",
    "expanderInvTierTwo",
    "expanderInvTierThree",
    "expanderInvTierFour",
    "expanderInvTierFive",
    # Misc
    "leverTileEntity",
])

# Maps TE ID → 1.7.10 block registry name (for source_block_id in placeholder).
TE_ID_TO_BLOCK_REGISTRY: dict[str, str] = {
    "turretbase":            "openmodularturrets:baseTierWood",
    "turretWoodBase":        "openmodularturrets:baseTierWood",
    "turretBaseOne":         "openmodularturrets:baseTierOneBlock",
    "turretBaseTwo":         "openmodularturrets:baseTierTwoBlock",
    "turretBaseThree":       "openmodularturrets:baseTierThreeBlock",
    "turretBaseFour":        "openmodularturrets:baseTierFourBlock",
    "disposableItemTurret":  "openmodularturrets:disposeItemTurret",
    "potatoCannonTurret":    "openmodularturrets:potatoCannonTurret",
    "machineGunTurret":      "openmodularturrets:machineGunTurret",
    "incendiaryTurret":      "openmodularturrets:incendiaryTurret",
    "grenadeTurret":         "openmodularturrets:grenadeTurret",
    "relativisticTurret":    "openmodularturrets:relativisticTurret",
    "rocketTurret":          "openmodularturrets:rocketTurret",
    "teleporterTurret":      "openmodularturrets:teleporterTurret",
    "laserTurret":           "openmodularturrets:laserTurret",
    "railGunTurret":         "openmodularturrets:railGunTurret",
    "expanderPowerTierOne":  "openmodularturrets:expanderPowerTierOne",
    "expanderPowerTierTwo":  "openmodularturrets:expanderPowerTierTwo",
    "expanderPowerTierThree": "openmodularturrets:expanderPowerTierThree",
    "expanderPowerTierFour": "openmodularturrets:expanderPowerTierFour",
    "expanderPowerTierFive": "openmodularturrets:expanderPowerTierFive",
    "expanderInvTierOne":    "openmodularturrets:expanderInvTierOne",
    "expanderInvTierTwo":    "openmodularturrets:expanderInvTierTwo",
    "expanderInvTierThree":  "openmodularturrets:expanderInvTierThree",
    "expanderInvTierFour":   "openmodularturrets:expanderInvTierFour",
    "expanderInvTierFive":   "openmodularturrets:expanderInvTierFive",
    "leverTileEntity":       "openmodularturrets:leverBlock",
}
