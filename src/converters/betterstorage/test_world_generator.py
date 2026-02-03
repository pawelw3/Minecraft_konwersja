"""
Generator testowej mapy 1.7.10 dla Better Storage.
Tworzy wszystkie typy bloków BS z różnymi stanami i inventory.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


class BetterStorageTestWorldGenerator:
    """Generator testowej mapy z wszystkimi blokami Better Storage."""
    
    # ID bloków Better Storage (numeryczne dla 1.7.10)
    # Te wartości będą dynamiczne - w praktyce trzeba sprawdzić na mapie
    # Używamy placeholderów - właściwe ID będą ustawione przez mod
    BS_BLOCK_IDS = {
        'crate': 0,  # Będzie ustawione przez TE
        'reinforcedChest': 0,
        'reinforcedLocker': 0,
        'locker': 0,
        'cardboardBox': 0,
        'craftingStation': 0,
        'armorStand': 0,
        'backpack': 0,
        'enderBackpack': 0,
        'present': 0,
        'lockableDoor': 0,
        'flintBlock': 0,
        'thaumiumChest': 0,
        'thaumcraftBackpack': 0,
    }
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.edits: List[Dict[str, Any]] = []
        self.crate_pile_data: Dict[int, Dict] = {}
        self.crate_counter = 0
        
    def generate_all_blocks(self):
        """Generuje wszystkie typy bloków BS."""
        base_x, base_y, base_z = 0, 64, 0
        
        # 1. Crate (pojedynczy i stos)
        self._generate_crates(base_x, base_y, base_z)
        base_x += 10
        
        # 2. Reinforced Chest (z różnymi materiałami)
        self._generate_reinforced_chests(base_x, base_y, base_z)
        base_x += 10
        
        # 3. Locker
        self._generate_lockers(base_x, base_y, base_z)
        base_x += 10
        
        # 4. Reinforced Locker
        self._generate_reinforced_lockers(base_x, base_y, base_z)
        base_x += 10
        
        # 5. Cardboard Box
        self._generate_cardboard_boxes(base_x, base_y, base_z)
        base_x += 10
        
        # 6. Crafting Station
        self._generate_crafting_stations(base_x, base_y, base_z)
        base_x += 10
        
        # 7. Armor Stand
        self._generate_armor_stands(base_x, base_y, base_z)
        base_x += 10
        
        # 8. Backpack
        self._generate_backpacks(base_x, base_y, base_z)
        base_x += 10
        
        # 9. Ender Backpack
        self._generate_ender_backpacks(base_x, base_y, base_z)
        base_x += 10
        
        # 10. Present
        self._generate_presents(base_x, base_y, base_z)
        base_x += 10
        
        # 11. Lockable Door
        self._generate_lockable_doors(base_x, base_y, base_z)
        base_x += 10
        
        # 12. Flint Block
        self._generate_flint_blocks(base_x, base_y, base_z)
        base_x += 10
        
        # 13. Thaumium Chest
        self._generate_thaumium_chests(base_x, base_y, base_z)
        base_x += 10
        
        # 14. Thaumcraft Backpack
        self._generate_thaumcraft_backpacks(base_x, base_y, base_z)
        
    def _generate_crates(self, base_x: int, base_y: int, base_z: int):
        """Generuje Crates - pojedynczy i stos."""
        # Pojedynczy crate
        self._add_block(base_x, base_y, base_z, 'betterstorage:crate')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.crate', {
            'crateId': -1  # Nowy crate
        })
        
        # Stos 2x2 crate (crate pile)
        pile_id = self.crate_counter
        self.crate_counter += 1
        
        # Dodaj 4 craty w stosie
        crate_positions = [
            (base_x + 2, base_y, base_z),
            (base_x + 3, base_y, base_z),
            (base_x + 2, base_y + 1, base_z),
            (base_x + 3, base_y + 1, base_z),
        ]
        
        for i, (x, y, z) in enumerate(crate_positions):
            self._add_block(x, y, z, 'betterstorage:crate')
            self._add_te(x, y, z, 'container.betterstorage.crate', {
                'crateId': pile_id
            })
        
        # Zapisz dane crate pile
        self.crate_pile_data[pile_id] = {
            'items': [
                {'Slot': 0, 'id': 'minecraft:stone', 'Count': 64, 'Damage': 0},
                {'Slot': 1, 'id': 'minecraft:dirt', 'Count': 32, 'Damage': 0},
                {'Slot': 2, 'id': 'minecraft:diamond', 'Count': 16, 'Damage': 0},
                {'Slot': 3, 'id': 'minecraft:iron_ingot', 'Count': 48, 'Damage': 0},
            ],
            'numCrates': 4
        }
        
    def _generate_reinforced_chests(self, base_x: int, base_y: int, base_z: int):
        """Generuje Reinforced Chests z różnymi materiałami i zawartością."""
        materials = ['iron', 'gold', 'diamond', 'emerald', 'copper']
        
        for i, material in enumerate(materials):
            x = base_x + i * 2
            z = base_z
            
            self._add_block(x, base_y, z, 'betterstorage:reinforcedChest')
            
            # Inventory z różnymi itemami
            items = [
                {'Slot': 0, 'id': 'minecraft:stone', 'Count': 64, 'Damage': 0},
                {'Slot': 1, 'id': 'minecraft:planks', 'Count': 32, 'Damage': 0},
                {'Slot': 5, 'id': f'minecraft:{material}_ingot' if material != 'emerald' else 'minecraft:emerald', 
                 'Count': 16, 'Damage': 0},
            ]
            
            self._add_te(x, base_y, z, 'container.betterstorage.reinforcedChest', {
                'Items': items,
                'Material': material,
                'orientation': 2,  # North
            })
            
        # Podwójny reinforced chest
        x = base_x
        z = base_z + 2
        
        for i in range(2):
            self._add_block(x + i, base_y, z, 'betterstorage:reinforcedChest')
            self._add_te(x + i, base_y, z, 'container.betterstorage.reinforcedChest', {
                'Items': [
                    {'Slot': i * 10, 'id': 'minecraft:gold_ingot', 'Count': 32, 'Damage': 0},
                ],
                'Material': 'gold',
                'orientation': 3,  # South
            })
            
    def _generate_lockers(self, base_x: int, base_y: int, base_z: int):
        """Generuje Lockery."""
        # Pojedynczy locker
        self._add_block(base_x, base_y, base_z, 'betterstorage:locker')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.locker', {
            'Items': [
                {'Slot': 0, 'id': 'minecraft:iron_helmet', 'Count': 1, 'Damage': 0},
                {'Slot': 1, 'id': 'minecraft:iron_chestplate', 'Count': 1, 'Damage': 0},
            ],
            'orientation': 2,
            'mirror': False,
        })
        
        # Podwójny locker (pionowy)
        for y in range(2):
            self._add_block(base_x + 2, base_y + y, base_z, 'betterstorage:locker')
            self._add_te(base_x + 2, base_y + y, base_z, 'container.betterstorage.locker', {
                'Items': [{'Slot': y * 12, 'id': 'minecraft:wooden_sword', 'Count': 1, 'Damage': 0}],
                'orientation': 4,  # West
                'mirror': True,
            })
            
    def _generate_reinforced_lockers(self, base_x: int, base_y: int, base_z: int):
        """Generuje Reinforced Lockery."""
        materials = ['iron', 'diamond']
        
        for i, material in enumerate(materials):
            x = base_x + i * 2
            self._add_block(x, base_y, base_z, 'betterstorage:reinforcedLocker')
            self._add_te(x, base_y, base_z, 'container.betterstorage.reinforcedLocker', {
                'Items': [
                    {'Slot': 0, 'id': 'minecraft:diamond', 'Count': 8, 'Damage': 0},
                    {'Slot': 5, 'id': 'minecraft:emerald', 'Count': 16, 'Damage': 0},
                ],
                'Material': material,
                'orientation': 2,
            })
            
    def _generate_cardboard_boxes(self, base_x: int, base_y: int, base_z: int):
        """Generuje Cardboard Boxy."""
        # Zwykły
        self._add_block(base_x, base_y, base_z, 'betterstorage:cardboardBox')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.cardboardBox', {
            'Items': [
                {'Slot': 0, 'id': 'minecraft:paper', 'Count': 16, 'Damage': 0},
            ],
            'uses': 3,
            'color': -1,
        })
        
        # Pokolorowany
        self._add_block(base_x + 2, base_y, base_z, 'betterstorage:cardboardBox')
        self._add_te(base_x + 2, base_y, base_z, 'container.betterstorage.cardboardBox', {
            'Items': [],
            'uses': 5,
            'color': 14,  # Red
        })
        
    def _generate_crafting_stations(self, base_x: int, base_y: int, base_z: int):
        """Generuje Crafting Stations."""
        # Pusta
        self._add_block(base_x, base_y, base_z, 'betterstorage:craftingStation')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.craftingStation', {
            'Items': [],
        })
        
        # Z zawartością
        self._add_block(base_x + 2, base_y, base_z, 'betterstorage:craftingStation')
        self._add_te(base_x + 2, base_y, base_z, 'container.betterstorage.craftingStation', {
            'Items': [
                {'Slot': 0, 'id': 'minecraft:planks', 'Count': 1, 'Damage': 0},  # Crafting grid slot 0
                {'Slot': 1, 'id': 'minecraft:planks', 'Count': 1, 'Damage': 0},  # Crafting grid slot 1
                {'Slot': 9, 'id': 'minecraft:stick', 'Count': 4, 'Damage': 0},   # Output
            ],
        })
        
    def _generate_armor_stands(self, base_x: int, base_y: int, base_z: int):
        """Generuje Armor Stand."""
        self._add_block(base_x, base_y, base_z, 'betterstorage:armorStand')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.armorStand', {
            'Items': [
                {'Slot': 0, 'id': 'minecraft:diamond_helmet', 'Count': 1, 'Damage': 0},
                {'Slot': 1, 'id': 'minecraft:diamond_chestplate', 'Count': 1, 'Damage': 0},
                {'Slot': 2, 'id': 'minecraft:diamond_leggings', 'Count': 1, 'Damage': 0},
                {'Slot': 3, 'id': 'minecraft:diamond_boots', 'Count': 1, 'Damage': 0},
            ],
        })
        
    def _generate_backpacks(self, base_x: int, base_y: int, base_z: int):
        """Generuje Backpacki."""
        # Zwykły
        self._add_block(base_x, base_y, base_z, 'betterstorage:backpack')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.backpack', {
            'Items': [
                {'Slot': 0, 'id': 'minecraft:torch', 'Count': 64, 'Damage': 0},
                {'Slot': 1, 'id': 'minecraft:cobblestone', 'Count': 64, 'Damage': 0},
            ],
            'color': -1,
        })
        
        # Pokolorowany
        self._add_block(base_x + 2, base_y, base_z, 'betterstorage:backpack')
        self._add_te(base_x + 2, base_y, base_z, 'container.betterstorage.backpack', {
            'Items': [{'Slot': 0, 'id': 'minecraft:golden_apple', 'Count': 1, 'Damage': 0}],
            'color': 4,  # Yellow
        })
        
    def _generate_ender_backpacks(self, base_x: int, base_y: int, base_z: int):
        """Generuje Ender Backpacki."""
        self._add_block(base_x, base_y, base_z, 'betterstorage:enderBackpack')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.enderBackpack', {})
        
    def _generate_presents(self, base_x: int, base_y: int, base_z: int):
        """Generuje Presenty."""
        self._add_block(base_x, base_y, base_z, 'betterstorage:present')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.present', {
            'Items': [
                {'Slot': 0, 'id': 'minecraft:cake', 'Count': 1, 'Damage': 0},
                {'Slot': 1, 'id': 'minecraft:cookie', 'Count': 16, 'Damage': 0},
            ],
            'color': 1,  # Orange
        })
        
    def _generate_lockable_doors(self, base_x: int, base_y: int, base_z: int):
        """Generuje Lockable Doors."""
        # Dolna część drzwi
        self._add_block(base_x, base_y, base_z, 'betterstorage:lockableDoor')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.lockableDoor', {
            # Zamek
        })
        
        # Górna część drzwi
        self._add_block(base_x, base_y + 1, base_z, 'betterstorage:lockableDoor')
        self._add_te(base_x, base_y + 1, base_z, 'container.betterstorage.lockableDoor', {})
        
    def _generate_flint_blocks(self, base_x: int, base_y: int, base_z: int):
        """Generuje Flint Blocks."""
        self._add_block(base_x, base_y, base_z, 'betterstorage:flintBlock')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.flintBlock', {})
        
    def _generate_thaumium_chests(self, base_x: int, base_y: int, base_z: int):
        """Generuje Thaumium Chests."""
        self._add_block(base_x, base_y, base_z, 'betterstorage:thaumiumChest')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.thaumiumChest', {
            'Items': [
                {'Slot': 0, 'id': 'Thaumcraft:ItemResource', 'Count': 16, 'Damage': 2},  # Thaumium ingot
            ],
            'Material': 'thaumium',
            'orientation': 2,
        })
        
    def _generate_thaumcraft_backpacks(self, base_x: int, base_y: int, base_z: int):
        """Generuje Thaumcraft Backpacks."""
        self._add_block(base_x, base_y, base_z, 'betterstorage:thaumcraftBackpack')
        self._add_te(base_x, base_y, base_z, 'container.betterstorage.thaumcraftBackpack', {
            'Items': [
                {'Slot': 0, 'id': 'Thaumcraft:ItemShard', 'Count': 8, 'Damage': 0},  # Air shard
            ],
            'color': -1,
        })
        
    def _add_block(self, x: int, y: int, z: int, block_id: str):
        """Dodaje blok do edycji."""
        # Używamy stone jako placeholder - właściwe ID będzie ustawione przez mod w runtime
        self.edits.append({
            'op': 'set_block',
            'x': x,
            'y': y,
            'z': z,
            'id': 1,  # Stone placeholder
            'meta': 0,
            'bs_block_id': block_id,  # Metadata dla nas
        })
        
    def _add_te(self, x: int, y: int, z: int, te_id: str, nbt_data: Dict):
        """Dodaje Tile Entity do edycji."""
        te_nbt = {
            'id': te_id,
            'x': x,
            'y': y,
            'z': z,
            **nbt_data
        }
        self.edits.append({
            'op': 'set_te',
            'x': x,
            'y': y,
            'z': z,
            'nbt': te_nbt,
        })
        
    def save_patch(self, filename: str = 'betterstorage_test_patch.json'):
        """Zapisuje patch JSON."""
        patch = {
            'edits': self.edits,
            'metadata': {
                'mod': 'Better Storage',
                'version': '1.7.10',
                'description': 'Testowa mapa ze wszystkimi blokami BS',
                'blocks_count': len([e for e in self.edits if e['op'] == 'set_block']),
                'te_count': len([e for e in self.edits if e['op'] == 'set_te']),
            }
        }
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(patch, f, indent=2, ensure_ascii=False)
            
        print(f"Zapisano patch: {output_path}")
        print(f"  Bloki: {patch['metadata']['blocks_count']}")
        print(f"  Tile Entities: {patch['metadata']['te_count']}")
        
        return output_path
        
    def save_crate_files(self):
        """Zapisuje pliki crate pile."""
        crates_dir = self.output_dir / 'data' / 'crates'
        crates_dir.mkdir(parents=True, exist_ok=True)
        
        for crate_id, data in self.crate_pile_data.items():
            crate_file = crates_dir / f'{crate_id}.dat'
            
            # NBT format dla crate pile
            nbt_data = {
                'Data': data['items'],
                'NumCrates': data['numCrates'],
            }
            
            with open(crate_file, 'w', encoding='utf-8') as f:
                json.dump(nbt_data, f, indent=2)
                
            print(f"Zapisano crate pile: {crate_file}")
            
    def generate_summary(self) -> str:
        """Generuje podsumowanie testowej mapy."""
        blocks = {}
        for edit in self.edits:
            if edit['op'] == 'set_block':
                bs_id = edit.get('bs_block_id', 'unknown')
                blocks[bs_id] = blocks.get(bs_id, 0) + 1
                
        summary = [
            "=" * 60,
            "TESTOWA MAPA BETTER STORAGE - PODSUMOWANIE",
            "=" * 60,
            "",
            "Wygenerowane bloki:",
        ]
        
        for block_id, count in sorted(blocks.items()):
            summary.append(f"  {block_id}: {count}")
            
        summary.extend([
            "",
            f"Crate piles: {len(self.crate_pile_data)}",
            "",
            "Testowe scenariusze:",
            "  - Pojedynczy crate",
            "  - Stos 4 crate z wspólnym inventory",
            "  - Reinforced Chest (5 materiałów)",
            "  - Podwójny Reinforced Chest",
            "  - Locker (pojedynczy i podwójny)",
            "  - Reinforced Locker (2 materiały)",
            "  - Cardboard Box (zwykły i pokolorowany)",
            "  - Crafting Station (pusta i z itemami)",
            "  - Armor Stand (z zbroją)",
            "  - Backpack (zwykły i pokolorowany)",
            "  - Ender Backpack",
            "  - Present (z prezentami)",
            "  - Lockable Door",
            "  - Flint Block",
            "  - Thaumium Chest",
            "  - Thaumcraft Backpack",
            "=" * 60,
        ])
        
        return '\n'.join(summary)


def main():
    """Główna funkcja generująca testową mapę."""
    output_dir = Path('lightweigh_map_templates/1710/betterstorage_test')
    
    generator = BetterStorageTestWorldGenerator(output_dir)
    generator.generate_all_blocks()
    
    patch_path = generator.save_patch()
    generator.save_crate_files()
    
    summary = generator.generate_summary()
    print('\n' + summary)
    
    # Zapisz podsumowanie do pliku
    summary_path = output_dir / 'test_map_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"\nPodsumowanie zapisane: {summary_path}")
    
    return patch_path


if __name__ == '__main__':
    main()
