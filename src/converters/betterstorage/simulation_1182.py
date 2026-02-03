"""
Symulacja weryfikacji konwersji Better Storage -> 1.18.2

Sprawdza czy przekonwertowane dane NBT są zgodne z formatem 1.18.2.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Wynik walidacji BlockEntity 1.18.2"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class BlockEntityValidator1182:
    """
    Walidator BlockEntity dla Minecraft 1.18.2
    
    Sprawdza czy dane NBT są zgodne z formatem 1.18.2.
    """
    
    # Walidatory dla konkretnych typów BlockEntity
    VALIDATORS = {
        'minecraft:chest': '_validate_chest',
        'minecraft:barrel': '_validate_barrel',
        'ironchest:iron_chest': '_validate_iron_chest',
        'ironchest:copper_chest': '_validate_iron_chest',
        'packingtape:packed': '_validate_packed',
        'craftingstation:crafting_station': '_validate_crafting_station',
        'minecraft:armor_stand': '_validate_armor_stand',
        'minecraft:ender_chest': '_validate_ender_chest',
    }
    
    def validate(self, block_id: str, nbt: Dict[str, Any]) -> ValidationResult:
        """
        Waliduje BlockEntity 1.18.2
        
        Args:
            block_id: ID bloku docelowego (np. 'minecraft:chest')
            nbt: Dane NBT BlockEntity
            
        Returns:
            ValidationResult z wynikiem walidacji
        """
        errors = []
        warnings = []
        
        # Sprawdź czy mamy walidator dla tego typu
        validator_name = self.VALIDATORS.get(block_id)
        
        if validator_name:
            validator = getattr(self, validator_name)
            result = validator(nbt)
            errors.extend(result.errors)
            warnings.extend(result.warnings)
        else:
            warnings.append(f"Brak walidatora dla {block_id} - uzywam generycznej walidacji")
            result = self._validate_generic_inventory(nbt)
            errors.extend(result.errors)
            warnings.extend(result.warnings)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_chest(self, nbt: Dict[str, Any]) -> ValidationResult:
        """Waliduje Vanilla Chest 1.18.2"""
        errors = []
        warnings = []
        
        # Chest w 1.18.2:
        # - Items: lista ItemStack (max 27 slotów)
        # - CustomName: opcjonalny string (JSON)
        
        items = nbt.get('Items', [])
        if len(items) > 27:
            errors.append(f"Za duzo itemow w Chest: {len(items)} (max 27)")
        
        # Sprawdź poprawność itemów
        for item in items:
            item_result = self._validate_item_stack(item)
            errors.extend(item_result.errors)
            warnings.extend(item_result.warnings)
        
        # CustomName powinien być stringiem JSON
        custom_name = nbt.get('CustomName')
        if custom_name and not isinstance(custom_name, str):
            warnings.append(f"CustomName powinien byc stringiem, jest {type(custom_name)}")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_barrel(self, nbt: Dict[str, Any]) -> ValidationResult:
        """Waliduje Barrel 1.18.2"""
        errors = []
        warnings = []
        
        # Barrel ma tę samą strukturę co Chest (27 slotów)
        items = nbt.get('Items', [])
        if len(items) > 27:
            errors.append(f"Za duzo itemow w Barrel: {len(items)} (max 27)")
        
        for item in items:
            item_result = self._validate_item_stack(item)
            errors.extend(item_result.errors)
            warnings.extend(item_result.warnings)
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_iron_chest(self, nbt: Dict[str, Any]) -> ValidationResult:
        """Waliduje Iron Chest 1.18.2"""
        errors = []
        warnings = []
        
        # Iron Chests ma różne pojemności:
        # - Copper: 45 slotów
        # - Iron: 54 slotów
        # - Gold: 81 slotów
        # - Diamond/Crystal/Obsidian: 108 slotów
        
        items = nbt.get('Items', [])
        # Akceptujemy do 108 slotów (diamond)
        if len(items) > 108:
            errors.append(f"Za duzo itemow w Iron Chest: {len(items)} (max 108)")
        elif len(items) > 54:
            warnings.append(f"Duza liczba itemow: {len(items)} - upewnij sie ze to odpowiedni typ skrzyni")
        
        for item in items:
            item_result = self._validate_item_stack(item)
            errors.extend(item_result.errors)
            warnings.extend(item_result.warnings)
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_crafting_station(self, nbt: Dict[str, Any]) -> ValidationResult:
        """Waliduje Crafting Station 1.18.2"""
        errors = []
        warnings = []
        
        # Crafting Station w 1.18.2:
        # - Items: 10 slotów (9 crafting + 1 wynik)
        
        items = nbt.get('Items', [])
        if len(items) > 10:
            errors.append(f"Za duzo itemow w Crafting Station: {len(items)} (max 10)")
        
        for item in items:
            item_result = self._validate_item_stack(item)
            errors.extend(item_result.errors)
            warnings.extend(item_result.warnings)
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_armor_stand(self, nbt: Dict[str, Any]) -> ValidationResult:
        """Waliduje Armor Stand 1.18.2"""
        errors = []
        warnings = []
        
        # Vanilla Armor Stand w 1.18.2:
        # - NIE ma pola Items (to jest entity, nie BlockEntity!)
        # - Zbroja jest w polach ArmorItems, HandItems
        
        if 'Items' in nbt:
            warnings.append("Armor Stand w 1.18.2 nie powinien miec pola Items - to entity, nie BlockEntity")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_ender_chest(self, nbt: Dict[str, Any]) -> ValidationResult:
        """Waliduje Ender Chest 1.18.2"""
        errors = []
        warnings = []
        
        # Ender Chest w 1.18.2:
        # - NIE przechowuje Items w BlockEntity!
        # - Dane są per-player w osobnym storage
        
        if 'Items' in nbt:
            warnings.append("Ender Chest w 1.18.2 nie przechowuje Items w BlockEntity")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_packed(self, nbt: Dict[str, Any]) -> ValidationResult:
        """Waliduje Packed block (Packing Tape) 1.18.2"""
        errors = []
        warnings = []
        
        # Packing Tape w 1.18.2:
        # - Przechowuje zawartość bloku
        # - Struktura zależy od spakowanego bloku
        
        if not nbt.get('packed'):
            warnings.append("Brak flagi 'packed' - moze to byc niekompletna konwersja")
        
        # Sprawdź czy są itemy
        if 'Items' in nbt:
            items = nbt['Items']
            for item in items:
                item_result = self._validate_item_stack(item)
                errors.extend(item_result.errors)
                warnings.extend(item_result.warnings)
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_generic_inventory(self, nbt: Dict[str, Any]) -> ValidationResult:
        """Generyczna walidacja inventory"""
        errors = []
        warnings = []
        
        if 'Items' in nbt:
            items = nbt['Items']
            if not isinstance(items, list):
                errors.append(f"Items powinno byc lista, jest {type(items)}")
            else:
                for item in items:
                    item_result = self._validate_item_stack(item)
                    errors.extend(item_result.errors)
                    warnings.extend(item_result.warnings)
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_item_stack(self, item: Dict[str, Any]) -> ValidationResult:
        """
        Waliduje ItemStack 1.18.2
        
        Format 1.18.2:
        {
            id: string (np. "minecraft:stone")
            Count: byte
            Slot: byte (opcjonalnie)
            tag: compound (opcjonalnie)
        }
        """
        errors = []
        warnings = []
        
        if not isinstance(item, dict):
            errors.append(f"Item powinien byc slownikiem, jest {type(item)}")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        # Sprawdź ID
        item_id = item.get('id')
        if not item_id:
            errors.append("Item bez ID")
        elif not isinstance(item_id, str):
            warnings.append(f"ID itemu powinien byc stringiem, jest {type(item_id)}")
        
        # Sprawdź Count
        count = item.get('Count', 1)
        if not isinstance(count, int):
            warnings.append(f"Count powinien byc int, jest {type(count)}")
        elif count < 1 or count > 64:
            warnings.append(f"Count poza zakresem 1-64: {count}")
        
        # Sprawdź Slot
        slot = item.get('Slot')
        if slot is not None and not isinstance(slot, int):
            warnings.append(f"Slot powinien byc int, jest {type(slot)}")
        
        # Sprawdź tagi
        if 'tag' in item:
            tag = item['tag']
            if not isinstance(tag, dict):
                errors.append(f"Tag powinien byc slownikiem, jest {type(tag)}")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


class ConversionSimulator1182:
    """
    Symulator działania przekonwertowanych bloków w 1.18.2
    
    Sprawdza czy konwersja z 1.7.10 działa poprawnie w 1.18.2.
    """
    
    def __init__(self):
        self.validator = BlockEntityValidator1182()
    
    def simulate_conversion(self, original_block: str, converted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Symuluje działanie przekonwertowanego bloku w 1.18.2
        
        Args:
            original_block: Oryginalny ID bloku BS
            converted: Wynik konwersji (block_id, nbt, warnings, overflow)
            
        Returns:
            {
                'simulation_passed': bool,
                'validation': ValidationResult,
                'differences_from_1182': List[str],
                'can_be_accepted': bool,
                'notes': List[str],
            }
        """
        block_id = converted.get('block_id', 'minecraft:air')
        nbt = converted.get('nbt', {})
        warnings = converted.get('warnings', [])
        overflow = converted.get('overflow', [])
        
        notes = []
        differences = []
        
        # Walidacja formatu 1.18.2
        validation = self.validator.validate(block_id, nbt)
        
        # Analiza różnic między 1.7.10 a 1.18.2
        if original_block == 'betterstorage:armorStand':
            differences.append("Armor Stand: BS ma GUI (4 sloty), vanilla nie ma GUI")
            differences.append("Zawartosc musi byc umieszczona w skrzyni obok (overflow)")
            notes.append("Overflow zawiera zawartosc Armor Stand do umieszczenia w skrzyni")
        
        elif original_block == 'betterstorage:enderBackpack':
            differences.append("Ender Backpack -> Ender Chest: ten sam vanilla Ender Chest")
            notes.append("Gracz zachowuje dostep do Ender Chest - brak migracji danych")
        
        elif original_block == 'betterstorage:crate':
            differences.append("Crate Pile: wiele crate'ow dzielilo inventory w 1.7.10")
            differences.append("Po konwersji: kazdy crate to osobna skrzynia")
            notes.append("Itemy zostaly rozdzielone proporcjonalnie miedzy skrzynie")
        
        elif original_block == 'betterstorage:cardboardBox':
            differences.append("Cardboard Box: zuzywanie blok (uses) w 1.7.10")
            differences.append("Packing Tape: zuzywanie tasmy (nie blok)")
            notes.append("System zuzywania sie zmienia - inny mechanizm")
        
        elif original_block == 'betterstorage:reinforcedChest':
            differences.append("Reinforced Chest: pojemnosc zalezna od configu (27/33/39)")
            differences.append("Iron Chest: stala pojemnosc (45/54/81/108)")
            notes.append("Material (iron/gold/diamond) jest tylko kosmetyczny w BS")
        
        elif original_block == 'betterstorage:locker':
            differences.append("Locker: pionowy, 36 slotow")
            differences.append("Barrel: pionowy, 27 slotow")
            notes.append("Jesli >27 itemow, uzyto Iron Chest zamiast Barrel")
        
        # Sprawdź czy można zaakceptować konwersję
        can_be_accepted = validation.valid and len(differences) < 5
        
        # Symulacja "przeszła" jeśli walidacja jest OK
        simulation_passed = validation.valid
        
        return {
            'simulation_passed': simulation_passed,
            'validation': validation,
            'differences_from_1182': differences,
            'can_be_accepted': can_be_accepted,
            'notes': notes + warnings,
            'overflow_count': len(overflow),
        }
    
    def compare_with_native_1182(self, block_id: str, nbt: Dict[str, Any]) -> List[str]:
        """
        Porównuje przekonwertowane dane z natywnym formatem 1.18.2
        
        Zwraca listę różnic które mogą wpłynąć na działanie.
        """
        differences = []
        
        # Sprawdź typowe różnice między skonwertowanymi a natywnymi danymi
        
        if block_id == 'minecraft:chest':
            # Natywny chest w 1.18.2
            if 'facing' not in nbt:
                differences.append("Brak 'facing' - chest moze miec domyslna orientacje")
        
        elif block_id == 'minecraft:barrel':
            # Barrel wymaga facing
            if 'facing' not in nbt:
                differences.append("Brak 'facing' - barrel wymaga orientacji")
        
        elif 'ironchest:' in block_id:
            # Iron Chests może mieć dodatkowe pola
            if 'facing' not in nbt:
                differences.append("Brak 'facing' - Iron Chest moze miec domyslna orientacje")
        
        return differences


def run_simulation_tests():
    """Uruchamia testy symulacji 1.18.2"""
    from .nbt_converter import BetterStorageConverter
    
    print("=" * 70)
    print("SYMULACJA 1.18.2 - WERYFIKACJA KONWERSJI")
    print("=" * 70)
    
    simulator = ConversionSimulator1182()
    converter = BetterStorageConverter()
    
    test_cases = [
        {
            'name': 'Reinforced Locker (znaleziony na mapie)',
            'block_id': 'betterstorage:reinforcedLocker',
            'nbt': {
                'Items': [
                    {'id': 'minecraft:stone', 'Count': 32, 'Slot': 0},
                    {'id': 'minecraft:dirt', 'Count': 16, 'Slot': 1},
                ],
                'Material': 'iron',
                'orientation': 2,
            },
        },
        {
            'name': 'Crate (pusty)',
            'block_id': 'betterstorage:crate',
            'nbt': {
                'crateId': 17111,
            },
        },
        {
            'name': 'Locker (pelny)',
            'block_id': 'betterstorage:locker',
            'nbt': {
                'Items': [
                    {'id': 'minecraft:cobblestone', 'Count': 64, 'Slot': i}
                    for i in range(36)
                ],
                'orientation': 3,
            },
        },
        {
            'name': 'Armor Stand',
            'block_id': 'betterstorage:armorStand',
            'nbt': {
                'Items': [
                    {'id': 'minecraft:iron_helmet', 'Count': 1, 'Slot': 0},
                    {'id': 'minecraft:iron_chestplate', 'Count': 1, 'Slot': 1},
                    {'id': 'minecraft:iron_leggings', 'Count': 1, 'Slot': 2},
                    {'id': 'minecraft:iron_boots', 'Count': 1, 'Slot': 3},
                ],
            },
        },
        {
            'name': 'Ender Backpack',
            'block_id': 'betterstorage:enderBackpack',
            'nbt': {},
        },
        {
            'name': 'Thaumium Chest (Thaumcraft)',
            'block_id': 'betterstorage:thaumiumChest',
            'nbt': {
                'Items': [
                    {'id': 'Thaumcraft:ItemResource', 'Count': 16, 'Slot': 0},
                    {'id': 'minecraft:gold_ingot', 'Count': 32, 'Slot': 1},
                ],
                'Material': 'thaumium',
                'orientation': 2,
            },
        },
        {
            'name': 'Thaumcraft Backpack',
            'block_id': 'betterstorage:thaumcraftBackpack',
            'nbt': {
                'Items': [
                    {'id': 'Thaumcraft:ItemThaumonomicon', 'Count': 1, 'Slot': 0},
                    {'id': 'minecraft:ender_pearl', 'Count': 8, 'Slot': 1},
                ],
            },
        },
        {
            'name': 'Crafting Station',
            'block_id': 'betterstorage:craftingStation',
            'nbt': {
                'Items': [
                    {'id': 'minecraft:stick', 'Count': 4, 'Slot': 0},
                    {'id': 'minecraft:planks', 'Count': 2, 'Slot': 1},
                ],
            },
        },
    ]
    
    all_passed = True
    
    for test in test_cases:
        print(f"\n--- Test: {test['name']} ---")
        
        # Konwersja
        result = converter.convert_tile_entity(
            test['block_id'],
            test['nbt'],
            x=100, y=64, z=200
        )
        
        print(f"Konwersja: {test['block_id']} -> {result['block_id']}")
        
        # Symulacja 1.18.2
        sim_result = simulator.simulate_conversion(test['block_id'], result)
        
        print(f"Walidacja 1.18.2: {'OK' if sim_result['validation'].valid else 'BLAD'}")
        
        if sim_result['validation'].errors:
            print(f"  Bledy: {sim_result['validation'].errors}")
        
        if sim_result['validation'].warnings:
            print(f"  Ostrzezenia: {sim_result['validation'].warnings}")
        
        if sim_result['differences_from_1182']:
            print(f"  Roznice od 1.18.2:")
            for diff in sim_result['differences_from_1182']:
                print(f"    - {diff}")
        
        print(f"  Moze byc zaakceptowane: {'TAK' if sim_result['can_be_accepted'] else 'NIE'}")
        
        if not sim_result['simulation_passed']:
            all_passed = False
    
    print("\n" + "=" * 70)
    print(f"Wynik: {'WSZYSTKIE TESTY OK' if all_passed else 'SA BLEDY'}")
    print("=" * 70)
    
    return all_passed


if __name__ == '__main__':
    run_simulation_tests()
