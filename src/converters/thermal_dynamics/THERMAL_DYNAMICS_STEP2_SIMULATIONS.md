# Thermal Dynamics — Krok 2 (Symulacje kontraktowe)

Symulacje weryfikują reguły konwersji Thermal Dynamics 1.7.10 → 1.18.2 (TD + Mekanism).
Nie symulują pełnego działania modów — sprawdzają tylko kontrakty, które muszą być spełnione
przed napisaniem kodu konwersji (krok 3).

## Wynik

- Status: PASS
- Symulacje zaliczone: 6/6

## Symulacje

| Nazwa | Status | Ostrzezenia |
| --- | --- | --- |
| duct_id_and_target_resolution | PASS | - |
| energy_duct_tier_collapse | PASS | - |
| fluid_duct_windowed_mapping | PASS | - |
| item_duct_to_mekanism_tier | PASS | Mekanism logistical transporters do NOT support Servo/Filter attachments as separate blocks. Pull/push is intrinsic; advanced filtering requires mekanism:logistical_sorter.; Ender Itemduct teleportation (no physical connection) has no equivalent in Mekanism transporters. Elite tier is closest in throughput only.; Flux-Plated Itemduct (item + RF in one block) has no equivalent. Ultimate tier covers item throughput only; RF requires separate universal cable. |
| viaduct_to_teleporter | PASS | Teleporter requires a 4x5 frame of teleporter_frame blocks, power (FE), and frequency configuration. Single Viaduct block does NOT map 1:1 spatially. |
| attachment_loss_warning | PASS | Attachments will be LOST during block conversion. Inventory must be dumped to chests or manually reconstructed with Mekanism:logistical_sorter. |

## Kontrakty dla kroku 3

1. Wszystkie placeable Energy Ducts (meta 0,1,2,4,6 z offsetu 0) MUSZĄ mapować się na `thermal:energy_duct`.
2. Fluid Ducts z meta 6,7 (Super-Laminar) MUSZĄ mapować się na `thermal:fluid_duct_windowed`; pozostałe na `thermal:fluid_duct`.
3. Item Ducts MUSZĄ mapować się na odpowiednie tiery Mekanism Logistical Transporter (basic→advanced→elite→ultimate).
4. Viaducts MUSZĄ mapować się na `mekanism:teleporter`; Viaduct Frame na `mekanism:teleporter_frame`.
5. Structuralduct i Glowstone Illuminator NIE MAJĄ targetu — konwerter musi wyemitować placeholder lub usunąć blok.
6. Załączniki (Servo/Filter/Retriever) z NBT ductu MUSZĄ być zrzucane do skrzyni (lub zignorowane) — nie mają bezpośredniego mapowania blokowego.

## Szczegóły

### duct_id_and_target_resolution

Status: PASS

Checks:
- Leadstone Fluxduct -> thermal:energy_duct
- Hardened Fluxduct -> thermal:energy_duct
- Redstone Energy Fluxduct -> thermal:energy_duct
- Reinforced Fluxduct (empty) -> None (expected crafting item)
- Signalum Fluxduct -> thermal:energy_duct
- Resonant Fluxduct (empty) -> None (expected crafting item)
- Cryo-Stabilized Fluxduct -> thermal:energy_duct
- Cryo-Stabilized Fluxduct (empty) -> None (expected crafting item)
- Temperate Fluiduct -> thermal:fluid_duct
- Temperate Fluiduct (opaque) -> thermal:fluid_duct
- Hardened Fluiduct -> thermal:fluid_duct
- Hardened Fluiduct (opaque) -> thermal:fluid_duct
- Flux-Plated Fluiduct -> thermal:fluid_duct
- Flux-Plated Fluiduct (opaque) -> thermal:fluid_duct
- Super-Laminar Fluiduct -> thermal:fluid_duct_windowed
- Super-Laminar Fluiduct (opaque) -> thermal:fluid_duct_windowed
- Itemduct -> mekanism:basic_logistical_transporter
- Itemduct (opaque) -> mekanism:basic_logistical_transporter
- Impulse Itemduct -> mekanism:advanced_logistical_transporter
- Impulse Itemduct (opaque) -> mekanism:advanced_logistical_transporter
- Ender Itemduct -> mekanism:elite_logistical_transporter
- Ender Itemduct (opaque) -> mekanism:elite_logistical_transporter
- Flux-Plated Itemduct -> mekanism:ultimate_logistical_transporter
- Flux-Plated Itemduct (opaque) -> mekanism:ultimate_logistical_transporter
- Structuralduct -> None (no 1.18.2 equivalent)
- Glowstone Illuminator -> None (no 1.18.2 equivalent)
- Viaduct -> mekanism:teleporter
- Long-Range Viaduct -> mekanism:teleporter
- Accelerated Viaduct -> mekanism:teleporter
- Viaduct Frame -> mekanism:teleporter_frame

### energy_duct_tier_collapse

Status: PASS

Checks:
- Leadstone Fluxduct -> thermal:energy_duct
- Hardened Fluxduct -> thermal:energy_duct
- Redstone Energy Fluxduct -> thermal:energy_duct
- Reinforced Fluxduct (empty) -> None (crafting item, not placeable)
- Signalum Fluxduct -> thermal:energy_duct
- Resonant Fluxduct (empty) -> None (crafting item, not placeable)
- Cryo-Stabilized Fluxduct -> thermal:energy_duct
- Cryo-Stabilized Fluxduct (empty) -> None (crafting item, not placeable)

### fluid_duct_windowed_mapping

Status: PASS

Checks:
- Temperate Fluiduct -> thermal:fluid_duct
- Temperate Fluiduct (opaque) -> thermal:fluid_duct
- Hardened Fluiduct -> thermal:fluid_duct
- Hardened Fluiduct (opaque) -> thermal:fluid_duct
- Flux-Plated Fluiduct -> thermal:fluid_duct
- Flux-Plated Fluiduct (opaque) -> thermal:fluid_duct
- Super-Laminar Fluiduct -> thermal:fluid_duct_windowed
- Super-Laminar Fluiduct (opaque) -> thermal:fluid_duct_windowed

### item_duct_to_mekanism_tier

Status: PASS

Checks:
- Itemduct -> mekanism:basic_logistical_transporter
- Itemduct (opaque) -> mekanism:basic_logistical_transporter
- Impulse Itemduct -> mekanism:advanced_logistical_transporter
- Impulse Itemduct (opaque) -> mekanism:advanced_logistical_transporter
- Ender Itemduct -> mekanism:elite_logistical_transporter
- Ender Itemduct (opaque) -> mekanism:elite_logistical_transporter
- Flux-Plated Itemduct -> mekanism:ultimate_logistical_transporter
- Flux-Plated Itemduct (opaque) -> mekanism:ultimate_logistical_transporter

Warnings:
- Mekanism logistical transporters do NOT support Servo/Filter attachments as separate blocks. Pull/push is intrinsic; advanced filtering requires mekanism:logistical_sorter.
- Ender Itemduct teleportation (no physical connection) has no equivalent in Mekanism transporters. Elite tier is closest in throughput only.
- Flux-Plated Itemduct (item + RF in one block) has no equivalent. Ultimate tier covers item throughput only; RF requires separate universal cable.

### viaduct_to_teleporter

Status: PASS

Checks:
- Viaduct -> mekanism:teleporter (Viaduct -> teleporter (instant teleport vs pipe travel))
- Long-Range Viaduct -> mekanism:teleporter (Long-Range Viaduct -> teleporter (range irrelevant for teleporter))
- Accelerated Viaduct -> mekanism:teleporter (Accelerated Viaduct -> teleporter (speed irrelevant for teleporter))
- Viaduct Frame -> mekanism:teleporter_frame (Viaduct Frame -> teleporter_frame)

Warnings:
- Teleporter requires a 4x5 frame of teleporter_frame blocks, power (FE), and frequency configuration. Single Viaduct block does NOT map 1:1 spatially.

### attachment_loss_warning

Status: PASS

Checks:
- Servo attachment from 1.7.10 has no direct block equivalent in Mekanism 1.18.2.
- Filter attachment from 1.7.10 has no direct block equivalent in Mekanism 1.18.2.
- Retriever attachment from 1.7.10 has no direct block equivalent in Mekanism 1.18.2.
- Thermal Dynamics 1.18.2 has servo_attachment/filter_attachment items, but they are meant for TD ducts, not Mekanism transporters.

Warnings:
- Attachments will be LOST during block conversion. Inventory must be dumped to chests or manually reconstructed with Mekanism:logistical_sorter.
