"""Główny konwerter Railcraft (1.7.10) → strict 1.18.2 (Create / Steam'n'Rails / IE / Mekanism / Thermal).

Source mapping (1.7.10):
- Bloki: mods/railcraft/common/blocks/RailcraftBlocks.java
- TileEntities: mods/railcraft/common/blocks/*/Tile*.java (writeToNBT/readFromNBT)
- MachineTileRegistery.java (rejestracja TE IDs)

Target mapping (1.18.2, zgodnie z docs/sprawdzenie_codex/cz4):
- Create + Steam'n'Rails — tory, sygnalizacja, niektóre maszyny
- Immersive Engineering — Coke Oven, Blast Furnace
- Mekanism — kable, energy cubes, logistical pipes
- Thermal — dynamo, nullifier, fluid cell
- Placeholder — brak odpowiedników

Kontrakty:
- Wejście: block_id_1710 (string) + metadata + te_nbt_1710 (dict)
- Wyjście: RailcraftBlockConversion z ConversionResult (block_id_1182, nbt_1182, blockstate_props)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from converters.common.conversion_event import ConversionEvent

from .mappings.block_mappings import get_mapping, is_railcraft_block
from .simulations.railcraft_simulation import simulate_railcraft_conversion


@dataclass
class ConversionResult:
    success: bool
    block_id_1182: str | None = None
    blockstate_props: dict[str, str] = field(default_factory=dict)
    nbt_1182: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    event: ConversionEvent | None = None


@dataclass
class RailcraftBlockConversion:
    original_id: str
    original_pos: tuple[int, int, int]
    metadata: int
    converted: ConversionResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_id": self.original_id,
            "original_pos": self.original_pos,
            "metadata": self.metadata,
            "new_id": self.converted.block_id_1182,
            "blockstate_props": self.converted.blockstate_props,
            "nbt": self.converted.nbt_1182,
            "errors": self.converted.errors,
            "warnings": self.converted.warnings,
            "event": self.converted.event.to_dict() if self.converted.event else None,
        }


class RailcraftConverter:
    SOURCE_VERSION = "1.7.10"
    TARGET_VERSION = "1.18.2"
    MOD = "railcraft"

    def __init__(self) -> None:
        self.events: list[ConversionEvent] = []
        self.stats = {"processed": 0, "converted": 0, "failed": 0, "warnings": 0}

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def convert_block(
        self,
        block_id_1710: str,
        metadata: int = 0,
        nbt_1710: dict[str, Any] | None = None,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> RailcraftBlockConversion:
        """Convert a Railcraft block + optional TileEntity NBT to 1.18.2."""
        self.stats["processed"] += 1

        # Sanity check
        if not is_railcraft_block(block_id_1710):
            msg = f"RC-E-NOT-RAILCRAFT: {block_id_1710} is not a Railcraft block"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[msg])
            return RailcraftBlockConversion(block_id_1710, position, metadata, result)

        # Get static mapping
        mapping = get_mapping(block_id_1710, metadata)
        if mapping is None:
            msg = f"RC-E-BLOCK-NOT-MAPPED: {block_id_1710} meta={metadata}"
            self.stats["failed"] += 1
            result = ConversionResult(False, errors=[msg])
            return RailcraftBlockConversion(block_id_1710, position, metadata, result)

        # Run NBT simulation if TE present
        sim_result: dict[str, Any] | None = None
        if nbt_1710:
            sim_result = simulate_railcraft_conversion(block_id_1710, metadata, nbt_1710)

        # Build warnings / errors
        warnings: list[str] = []
        errors: list[str] = []

        if mapping.notes:
            warnings.append(f"RC-W-MAPPING-NOTE: {mapping.notes}")

        if sim_result:
            warnings.extend(sim_result.get("warnings", []))
            errors.extend(sim_result.get("errors", []))
            # If simulation changed target (e.g. RCHiddenTile → air), use simulated target
            simulated_block = sim_result.get("block_id_1182")
            if simulated_block and simulated_block != mapping.target_block_id:
                target_block = simulated_block
            else:
                target_block = mapping.target_block_id
            blockstate = {**(mapping.blockstate_props or {}), **sim_result.get("blockstate_props", {})}
            nbt_out = sim_result.get("nbt_1182")
        else:
            target_block = mapping.target_block_id
            blockstate = dict(mapping.blockstate_props) if mapping.blockstate_props else {}
            nbt_out = None

        success = not errors
        self.stats["converted" if success else "failed"] += 1
        self.stats["warnings"] += len(warnings)

        event = self._make_event(
            source_block_id=block_id_1710,
            metadata=metadata,
            position=position,
            target_block_id=target_block,
            blockstate_props=blockstate,
            nbt_1182=nbt_out,
            warnings=warnings,
            errors=errors,
            nbt_1710=nbt_1710,
        )
        self.events.append(event)

        return RailcraftBlockConversion(
            original_id=block_id_1710,
            original_pos=position,
            metadata=metadata,
            converted=ConversionResult(
                success=success,
                block_id_1182=target_block,
                blockstate_props=blockstate,
                nbt_1182=nbt_out,
                errors=errors,
                warnings=warnings,
                event=event,
            ),
        )

    def convert_tile_entity(
        self,
        te_id: str,
        nbt_1710: dict[str, Any],
        metadata: int = 0,
        position: tuple[int, int, int] = (0, 0, 0),
    ) -> RailcraftBlockConversion:
        """Convert by TileEntity ID.

        In Railcraft 1.7.10 many TE IDs do not directly map to block IDs.
        We use heuristics based on TE ID to guess the block ID and metadata.
        """
        block_id, meta = self._resolve_block_from_te(te_id, metadata)
        return self.convert_block(
            block_id_1710=block_id,
            metadata=meta,
            nbt_1710=nbt_1710,
            position=position,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _resolve_block_from_te(self, te_id: str, metadata: int) -> tuple[str, int]:
        """Map TE ID back to (block_id, metadata) for Railcraft.

        Railcraft uses many different TE IDs across a few block IDs.
        """
        # Tracks
        if te_id in ("RailcraftTrackTile", "RailcraftTrackTESRTile"):
            return "railcraft.track", metadata

        # Hidden / Residual Heat
        if te_id == "RCHiddenTile":
            return "railcraft.residual.heat", 0

        # Detectors
        if te_id == "RCDetectorTile":
            return "railcraft.detector", metadata

        # Signals
        if te_id.startswith("RCTileStructure"):
            return "railcraft.signal", metadata

        # Machines Alpha
        alpha_te = {
            "RCWorldAnchorTile": ("railcraft.machine.alpha", 0),
            "RCSteamTurbineTile": ("railcraft.machine.alpha", 1),
            "RCPersonalAnchorTile": ("railcraft.machine.alpha", 2),
            "RCSteamOvenTile": ("railcraft.machine.alpha", 3),
            "RCAdminAnchorTile": ("railcraft.machine.alpha", 4),
            "RCSmokerTile": ("railcraft.machine.alpha", 5),
            "RCTradeStationTile": ("railcraft.machine.alpha", 6),
            "RCCokeOvenTile": ("railcraft.machine.alpha", 7),
            "RCRollingMachineTile": ("railcraft.machine.alpha", 8),
            "RCSteamTrapManualTile": ("railcraft.machine.alpha", 9),
            "RCSteamTrapAutoTile": ("railcraft.machine.alpha", 10),
            "RCFeedStationTile": ("railcraft.machine.alpha", 11),
            "RCBlastFurnaceTile": ("railcraft.machine.alpha", 12),
            "RCPassiveAnchorTile": ("railcraft.machine.alpha", 13),
            "RCWaterTankTile": ("railcraft.machine.alpha", 14),
            "RCRockCrusherTile": ("railcraft.machine.alpha", 15),
        }
        if te_id in alpha_te:
            return alpha_te[te_id]

        # Machines Beta
        beta_te = {
            "RCIronTankWallTile": ("railcraft.machine.beta", 0),
            "RCIronTankGaugeTile": ("railcraft.machine.beta", 1),
            "RCIronTankValveTile": ("railcraft.machine.beta", 2),
            "RCBoilerTankLowTile": ("railcraft.machine.beta", 3),
            "RCBoilerTankHighTile": ("railcraft.machine.beta", 4),
            "RCBoilerFireboxSoildTile": ("railcraft.machine.beta", 5),
            "RCBoilerFireboxLiquidTile": ("railcraft.machine.beta", 6),
            "RCEngineSteamHobby": ("railcraft.machine.beta", 7),
            "RCEngineSteamLow": ("railcraft.machine.beta", 8),
            "RCEngineSteamHigh": ("railcraft.machine.beta", 9),
            "RCAnchorSentinelTile": ("railcraft.machine.beta", 10),
            "RCVoidChestTile": ("railcraft.machine.beta", 11),
            "RCMetalsChestTile": ("railcraft.machine.beta", 12),
            "RCSteelTankWallTile": ("railcraft.machine.beta", 13),
            "RCSteelTankGaugeTile": ("railcraft.machine.beta", 14),
            "RCSteelTankValveTile": ("railcraft.machine.beta", 15),
        }
        if te_id in beta_te:
            return beta_te[te_id]

        # Machines Gamma
        gamma_te = {
            "RCLoaderTile": ("railcraft.machine.gamma", 0),
            "RCUnloaderTile": ("railcraft.machine.gamma", 1),
            "RCLoaderAdvancedTile": ("railcraft.machine.gamma", 2),
            "RCUnloaderAdvancedTile": ("railcraft.machine.gamma", 3),
            "RCLoaderTileLiquid": ("railcraft.machine.gamma", 4),
            "RCUnloaderTileLiquid": ("railcraft.machine.gamma", 5),
            "RCLoaderTileEnergy": ("railcraft.machine.gamma", 6),
            "RCUnloaderTileEnergy": ("railcraft.machine.gamma", 7),
            "RCMinecartDispenserTile": ("railcraft.machine.gamma", 8),
            "RCTrainDispenserTile": ("railcraft.machine.gamma", 9),
            "RCLoaderTileRF": ("railcraft.machine.gamma", 10),
            "RCUnloaderTileRF": ("railcraft.machine.gamma", 11),
        }
        if te_id in gamma_te:
            return gamma_te[te_id]

        # Machines Delta
        delta_te = {
            "RCWireTile": ("railcraft.machine.delta", 0),
            "RCCageTile": ("railcraft.machine.delta", 1),
        }
        if te_id in delta_te:
            return delta_te[te_id]

        # Machines Epsilon
        epsilon_te = {
            "RCElectricFeederTile": ("railcraft.machine.epsilon", 0),
            "RCElectricFeederAdminTile": ("railcraft.machine.epsilon", 1),
            "RCAdminSteamProducerTile": ("railcraft.machine.epsilon", 2),
            "RCForceTrackEmitterTile": ("railcraft.machine.epsilon", 3),
            "RCFluxTransformerTile": ("railcraft.machine.epsilon", 4),
            "RCEngravingBenchTile": ("railcraft.machine.epsilon", 5),
        }
        if te_id in epsilon_te:
            return epsilon_te[te_id]

        # Aesthetics (slab, stair, post)
        if te_id == "RCSlabTile":
            return "railcraft.slab", metadata
        if te_id == "RCStairTile":
            return "railcraft.stair", metadata
        if te_id == "RCPostEmblemTile":
            return "railcraft.post", metadata

        # Firestone recharge
        if te_id == "RCFirestoneRechargeTile":
            return "railcraft.cube", metadata  # approximate

        # Fallback: use the TE id as block id (won't match mappings, but produces clear error)
        return f"railcraft.{te_id}", metadata

    def _make_event(
        self,
        source_block_id: str,
        metadata: int,
        position: tuple[int, int, int],
        target_block_id: str,
        blockstate_props: dict[str, str],
        nbt_1182: dict[str, Any] | None,
        warnings: list[str],
        errors: list[str],
        nbt_1710: dict[str, Any] | None,
    ) -> ConversionEvent:
        return ConversionEvent(
            mod="railcraft",
            source_version="1.7.10",
            target_version="1.18.2",
            event_type="remap",
            source_block_id=source_block_id,
            source_metadata=metadata,
            target_block_id=target_block_id,
            position=position,
            blockstate_props=blockstate_props,
            nbt_1182=nbt_1182,
            warnings=warnings,
            errors=errors,
            source_nbt=nbt_1710,
        )
