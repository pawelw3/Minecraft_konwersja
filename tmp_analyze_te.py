import json

with open('output/zone_te_discovery.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

te_counts = data['all_te_ids']
sorted_te = sorted(te_counts.items(), key=lambda x: x[1], reverse=True)

# Inicjalizacja
mod_map = {
    'Applied Energistics 2': [],
    'Armourer\'s Workshop': [],
    'Better Storage': [],
    'BiblioCraft': [],
    'Big Reactors': [],
    'Blood Magic': [],
    'BuildCraft': [],
    'Carpenter\'s Blocks': [],
    'Chisel': [],
    'ComputerCraft': [],
    'CustomNPCs': [],
    'EnderStorage': [],
    'Extra Utilities': [],
    'Forestry': [],
    'Growthcraft': [],
    'IC2': [],
    'IC2 Nuclear Control': [],
    'Jammy Furniture': [],
    'Logistics Pipes': [],
    'Mekanism': [],
    'MrCrayfish Furniture': [],
    'Open Modular Turrets': [],
    'Pam\'s HarvestCraft': [],
    'Placeable Items': [],
    'PowerConverters': [],
    'ProjectRed': [],
    'Railcraft': [],
    'Reliquary': [],
    'Statues': [],
    'Thermal Series': [],
    'Thaumcraft': [],
    'Thaumic Energistics': [],
    'Traincraft': [],
    'Witchery': [],
    'Vanilla': [],
    'Other/Unknown': []
}

ae2_blocks = {'BlockCableBus','BlockDenseEnergyCell','BlockEnergyCell','BlockDrive','BlockController','BlockCraftingUnit','BlockInterface','BlockMolecularAssembler','BlockIOPort','BlockCraftingStorage','BlockCraftingMonitor','BlockEnergyAcceptor','BlockSkyChest','BlockCharger','BlockCellWorkbench','BlockSpatialPylon','BlockSpatialIOPort','BlockInscriber','BlockQuartzGrowthAccelerator'}

def classify(te, count):
    t = te
    tl = te.lower()
    if t in ae2_blocks:
        return 'Applied Energistics 2'
    if t.startswith('container.betterstorage'):
        return 'Better Storage'
    if t.startswith('cfm') or t in ['TableTile','seatTile','LampTile','LanternTile','dinnerPlateTile','GenericShelfTile']:
        return 'MrCrayfish Furniture'
    if t.startswith('biblio') or t in ['BookcaseTile','ArmorStandTile','PotionShelfTile','ToolRackTile','WoodLabelTile','WeaponCaseTile','PrintPressTile','WritingDeskTile','fancySignTile','CookieJarTile']:
        return 'BiblioCraft'
    if t.startswith('TileEntityCarpenters'):
        return 'Carpenter\'s Blocks'
    if 'mekanism' in tl or t in ['SalinationTank','SalinationValve','SalinationController','InductionCasing','InductionCell','InductionPort','BoundingBlock','AdvancedBoundingBlock','Bin','EnergyCube','LaserAmplifier','MetallurgicInfuser','OsmiumCompressor','QuantumEntangloporter','DigitalMiner','MekanismTeleporter','Teleporter']:
        return 'Mekanism'
    if 'thermalexpansion' in tl or 'thermaldynamics' in tl or t in ['thermalexpansion.Tesseract','thermalexpansion.Cell','thermalexpansion.Sponge','thermalexpansion.Accumulator','thermalexpansion.Transposer','thermalexpansion.Crucible','thermalexpansion.Smelter','thermalexpansion.Pulverizer','thermalexpansion.Sawmill','thermalexpansion.Furnace','thermalexpansion.Precipitator','thermalexpansion.Extruder','thermalexpansion.Assembler']:
        return 'Thermal Series'
    if 'railcraft' in tl or t.startswith('RC') or t in ['tileTCRail','tileTCRailGag','RCVoidChestTile']:
        return 'Railcraft'
    if t.startswith('witchery:'):
        return 'Witchery'
    if t.startswith('grc.') or t.startswith('grcmilk.'):
        return 'Growthcraft'
    if 'forestry' in tl:
        return 'Forestry'
    if 'buildcraft' in tl:
        return 'BuildCraft'
    if t.startswith('BR') and t not in ['BRCyaniteReprocessor']:
        return 'Big Reactors'
    if t == 'BRCyaniteReprocessor':
        return 'Big Reactors'
    if t in ['computer','wiredmodem','monitor','diskdrive']:
        return 'ComputerCraft'
    if t.startswith('tile.projectred'):
        return 'ProjectRed'
    if 'logisticspipes' in tl:
        return 'Logistics Pipes'
    if t.startswith('te.') and any(x in t for x in ['skinnable','armourLibrary','globalSkinLibrary','skinningTable','hologramProjector','colourMixer','dyeTable','mannequin']):
        return 'Armourer\'s Workshop'
    if t.startswith('TileNPC') or t == 'TileEntityPortal':
        return 'CustomNPCs'
    if 'thaumicenergistics' in tl:
        return 'Thaumic Energistics'
    if 'thaumcraft' in tl or t.startswith('Tile') and any(x in t for x in ['Node','Jar','Crucible','Arcane','Infusion','Research','Warded','Bellows','Deconstruction','Thaumatorium','ManaPod','Nitor','Focal','Essentia','WandPedestal','FluxScrubber','Mirror','AlchemyFurnace','ArcaneLamp','ArcaneWorkbench','AlchemyFurnaceAdvanced']):
        return 'Thaumcraft'
    if t.startswith('container') and any(x in t for x in ['Spell','WritingTable','BellJar','Altar','Pedestal','Plinth','MasterStone','ReagentConduit']):
        return 'Thaumcraft'
    if t in ['EnderChest','Ender Chest','TileEnderPillar','TileEnderConstructor'] or t == 'Ender Tank':
        return 'EnderStorage'
    if 'extrautils' in tl or t in ['TileEntityTransferNodeInventory','TileEntityFilingCabinet','TileEntityTrashCan']:
        return 'Extra Utilities'
    if t.startswith('Pam'):
        return 'Pam\'s HarvestCraft'
    if 'powerconverter' in tl:
        return 'PowerConverters'
    if 'turret' in tl or t in ['Laser','railGunTurret','teleporterTurret']:
        return 'Open Modular Turrets'
    if t in ['Furnace','Chest','Trap','Hopper','Dropper','Beacon','EnchantTable','Skull','FlowerPot','MobSpawner','Sign','Music'] or t == 'DLDetector':
        return 'Vanilla'
    if t in ['Reactor Chamber','Nuclear Reactor'] or t in ['MFSU','MFE','BatBox','CESU','LV-Transformer','MV-Transformer','Chargepad MFSU'] or t in ['Macerator','Extractor','Compressor','Electric Furnace','Induction Furnace','Solar Panel','Generator','Canning Machine','Thermal Centrifuge','Ore Washing Plant','Metal Former','Blast Furnace','Solid Heat Generator','Kinetic Generator','Wind Kinetic Generator','Electric Heat Generator','Electric Kinetic Generator','Crop-Matron','Crop Havester','Electric Pump','Mass Fabricator','Scanner','Pattern Storage','Replicator']:
        return 'IC2'
    if 'traincraft' in tl or t == 'TileTrainWbench':
        return 'Traincraft'
    if 'bloodmagic' in tl or t in ['containerAltar','containerSpellParadigmBlock','containerSpellModifierBlock','containerSpellEffectBlock','containerSpellEnhancementBlock']:
        return 'Blood Magic'
    if t.startswith('eplus:'):
        return 'Other/Unknown'
    if 'placeable' in tl:
        return 'Placeable Items'
    if t == 'autoChisel':
        return 'Chisel'
    if t == 'savedMultipart':
        return 'Other/Unknown'
    if t in ['TileEntityBlockColorData','TileOwned']:
        return 'Other/Unknown'
    if t in ['TileCrystal','TileSiphon','TileVat','TileVatSlave','TileVatConnector','TileVatMatrix','TileLight','TileSoulJar','TileSoulforge','TileSoulSieve']:
        return 'Reliquary'
    if t in ['RCBoilerFireboxLiquidTile','RCBoilerFireboxSoildTile','RCBoilerTankHighTile','RCRollingMachineTile','RCSmokerTile','RCStairTile','RCSlabTile','RCDetectorTile','RCCokeOvenTile','RCBlastFurnaceTile','RCSteelTankWallTile','RCIronTankWallTile']:
        return 'Railcraft'
    if t in ['TileResearchTable','TileDeconstructionTable']:
        return 'Thaumcraft'
    return 'Other/Unknown'

for te, count in sorted_te:
    mod = classify(te, count)
    mod_map[mod].append((te, count))

print('=== PODSUMOWANIE TE NA MAPIE (top 40 modow) ===')
results = []
for mod, items in mod_map.items():
    if items:
        total = sum(c for _, c in items)
        top3 = ', '.join(f'{t}({c})' for t, c in items[:3])
        results.append((total, mod, len(items), top3))

results.sort(reverse=True)
for total, mod, uniq, top3 in results[:40]:
    print(f'{total:>8} | {mod:<35} | {uniq:>3} typow | top: {top3}')

# Zapisz do pliku
with open('tmp_te_summary.json', 'w') as f:
    out = {mod: [{'te': t, 'count': c} for t, c in items] for mod, items in mod_map.items() if items}
    json.dump(out, f, indent=2)
print('\nZapisano tmp_te_summary.json')
