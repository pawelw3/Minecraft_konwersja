# Logistics Pipes - Zadanie 2: symulacje kontraktowe

Zakres: Logistics Pipes 0.9.3.132 z Minecraft 1.7.10 -> Pretty Pipes 1.12.8 / AE2 / XNet dla Minecraft 1.18.2.
Symulacje sa male i deterministyczne. Ich celem jest zapisanie kontraktow, ktore ma pozniej spelnic kod konwersji.

## Wynik

- Status: PASS
- Symulacje zaliczone: 5/5

## Symulacje

| Nazwa | Status | Ostrzezenia |
| --- | --- | --- |
| provider_request_flow | PASS | - |
| supplier_stockkeeping | PASS | LP pattern supplier target-slot semantics are not 1:1 in Pretty Pipes and must be reported for manual review. |
| crafting_request | PASS | Complex ModuleCrafter NBT with fluids, cleanup inventory or fuzzy matching should route to AE2/manual report. |
| chassis_module_dispatch | PASS | Chassis with more than 3 active modules requires generated conversion event plus manual/XNet/AE2 follow-up. |
| power_and_speed_contract | PASS | LP internal power amount is not a lossless FE value; preserve it in conversion event metadata, not as live Pretty Pipes NBT. |

## Kontrakty dla Zadania 3

1. Provider/request: proste rury provider/request moga przejsc na `prettypipes:pipe` z extraction/filter module oraz terminal jako punkt recznego requestu.
2. Supplier: stockkeeping nalezy modelowac jako retrieval module z lista docelowych itemow; tryb pattern/target-slot wymaga raportu manualnego.
3. Crafting: zwykle receptury itemowe moga isc do Pretty Pipes crafting module albo AE2 pattern provider; fuzzy/fluid/cleanup cases ida do AE2/manual report.
4. Chassis: Pretty pipe ma 3 sloty modulow. Chassis LP z wiecej niz 3 aktywnymi modulami musi emitowac overflow event, nie wolno gubic modulow.
5. Power/speed: LP power junction/RF/EU provider nie jest bezposrednim BE Pretty Pipes. Dla aktywnych sieci generuj rekomendacje `prettypipes:pressurizer` i zachowaj stare energy NBT w evencie.

## Dowody z kodu

- `lp_provider`: PipeItemsProviderLogistics delegates to ModuleProvider, computes canProvide() promises and extracts stacks in fullFill()/sendStack().
- `lp_request`: PipeItemsRequestLogistics calls RequestTree.request(...) for wanted ItemStack requests.
- `lp_supplier`: PipeItemsSupplierLogistics owns ModuleActiveSupplier in-pipe; ModuleActiveSupplier calculates missing stock and requests partial or complete supply.
- `lp_crafting`: PipeItemsCraftingLogistics delegates canProvide(), addCrafting(), fullFill(), read/write NBT and tick behaviour to ModuleCrafter.
- `lp_chassis`: PipeLogisticsChassiMk1..Mk5 expose getChassiSize(): 1, 2, 3, 4, 8; PipeLogisticsChassi forwards provider/crafting calls to installed modules by slot.
- `pretty_modules`: Pretty Pipes PipeBlockEntity stores ItemStackHandler modules with 3 slots and ticks each installed IModule.
- `pretty_request`: Pretty Pipes ItemTerminalBlockEntity.requestItemLater(...) requests from network locations and crafting modules.
- `pretty_crafting`: Pretty Pipes CraftingModuleItem contributes craftables and calls ItemTerminalBlockEntity.requestItemLater for ingredients.
- `pretty_speed`: PipeBlockEntity.getItemSpeed returns 0.05 + module speed + 0.45 when a PressurizerBlockEntity can spend FE; the pressurizer stores energy in NBT key 'energy'.

## Szczegoly

### provider_request_flow

Status: PASS

Checks:
- LP provider promise is bounded by source inventory and requested amount.
- Pretty extraction module can preserve the simple provider/request case.
- Physical target for conversion: prettypipes:pipe with extraction/filter module plus item terminal for manual requests.

### supplier_stockkeeping

Status: PASS

Checks:
- LP active supplier computes missing stock against a target inventory.
- Pretty retrieval module can pull the missing stack when represented as desired stock plus whitelist.

Warnings:
- LP pattern supplier target-slot semantics are not 1:1 in Pretty Pipes and must be reported for manual review.

### crafting_request

Status: PASS

Checks:
- Plain LP crafting pipe/table pattern can become Pretty Pipes crafting module or AE2 pattern provider.
- Ingredients are consumed only after all required stacks are available.
- Fluid crafting and cleanup-inventory cases are rejected from automatic Pretty Pipes conversion.

Warnings:
- Complex ModuleCrafter NBT with fluids, cleanup inventory or fuzzy matching should route to AE2/manual report.

### chassis_module_dispatch

Status: PASS

Checks:
- LP chassis Mk1..Mk4 can fit into one Pretty pipe only up to 3 installed modules.
- LP chassis Mk5 has 8 slots; overflow beyond 3 modules must not be silently dropped.
- Known provider/supplier/crafter modules map to extraction/retrieval/crafting Pretty modules.

Warnings:
- Chassis with more than 3 active modules requires generated conversion event plus manual/XNet/AE2 follow-up.

### power_and_speed_contract

Status: PASS

Checks:
- LP power junction/RF/EU providers do not become Pretty Pipes block entities directly.
- Pretty Pipes acceleration is represented by a nearby prettypipes:pressurizer with FE energy.
- Converted powered LP networks should emit a separate pressurizer placement recommendation.

Warnings:
- LP internal power amount is not a lossless FE value; preserve it in conversion event metadata, not as live Pretty Pipes NBT.
