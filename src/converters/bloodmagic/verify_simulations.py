"""
Weryfikacja zgodności symulacji Blood Magic z kodem 1.18.2

Sprawdza czy symulacje poprawnie odwzorowują:
1. Strukturę NBT w 1.18.2
2. Konwersję danych z 1.7.10
3. Zachowanie funkcjonalności
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from converters.bloodmagic.simulations.blood_altar_sim import (
    BloodAltarSimulation, AltarTier, BloodRuneType, SAMPLE_RECIPES
)
from converters.bloodmagic.simulations.ritual_stone_sim import (
    MasterRitualStoneSimulation, RitualType
)
from converters.bloodmagic.simulations.soul_network_sim import (
    SoulNetworkSimulation, BloodOrbSimulation, BloodOrb
)
from converters.bloodmagic.converter import BloodMagicConverter


class SimulationVerifier:
    """Weryfikator zgodności symulacji z kodem 1.18.2"""
    
    def __init__(self):
        self.warnings = []
        self.errors = []
        
    def verify_all(self):
        """Uruchom wszystkie weryfikacje"""
        print("=" * 70)
        print("WERYFIKACJA ZGODNOŚCI SYMULACJI BLOOD MAGIC Z 1.18.2")
        print("=" * 70)
        
        self.verify_blood_altar_simulation()
        self.verify_ritual_stone_simulation()
        self.verify_soul_network_simulation()
        self.verify_converter_integration()
        
        return self._generate_report()
    
    def verify_blood_altar_simulation(self):
        """Weryfikacja symulacji Blood Altar"""
        print("\n--- Weryfikacja Blood Altar ---")
        
        # Test 1: Konwersja tieru
        print("  Test 1: Konwersja tieru int -> string")
        altar_sim = BloodAltarSimulation("1.7.10")
        nbt_1710 = {
            "currentEssence": 5000,
            "upgradeLevel": 3,  # Tier 3 w 1.7.10
            "isActive": False,
            "progress": 0,
            "liquidRequired": 0,
            "canBeFilled": False,
        }
        altar_sim.load_from_nbt_1710(nbt_1710)
        
        # Konwersja do 1.18.2
        nbt_1182 = altar_sim.convert_to_1182_nbt()
        
        # Weryfikacja
        tier = nbt_1182.get("altarTier")
        if tier == "THREE":
            print(f"    [OK] Tier 3 poprawnie przekonwertowany na '{tier}'")
        else:
            self.errors.append(f"Blood Altar: Tier powinien być 'THREE', jest '{tier}'")
            print(f"    [ERROR] Tier powinien być 'THREE', jest '{tier}'")
        
        # Test 2: Zachowanie LP
        print("  Test 2: Zachowanie ilości LP")
        essence = nbt_1182.get("currentEssence")
        if essence == 5000:
            print(f"    [OK] LP poprawnie zachowane: {essence}")
        else:
            self.errors.append(f"Blood Altar: LP powinno być 5000, jest {essence}")
            print(f"    [ERROR] LP powinno być 5000, jest {essence}")
        
        # Test 3: Nowe pola w 1.18.2
        print("  Test 3: Inicjalizacja nowych pól 1.18.2")
        required_fields = [
            "chargeRate", "chargeFrequency", "totalCharge", 
            "maxCharge", "cooldownAfterCrafting"
        ]
        all_present = all(field in nbt_1182 for field in required_fields)
        if all_present:
            print(f"    [OK] Wszystkie nowe pola obecne")
        else:
            missing = [f for f in required_fields if f not in nbt_1182]
            self.warnings.append(f"Blood Altar: Brakujące nowe pola: {missing}")
            print(f"    [WARNING] Brakujące pola: {missing}")
        
        # Test 4: Symulacja craftingu
        print("  Test 4: Symulacja craftingu")
        altar_1182 = BloodAltarSimulation("1.18.2")
        altar_1182.load_from_nbt_1182({"bloodAltar": nbt_1182})
        
        recipe = SAMPLE_RECIPES["blank_slate"]
        if altar_1182.start_crafting_cycle(recipe):
            print(f"    [OK] Crafting może się rozpocząć (tier {altar_1182.state.tier.name})")
        else:
            self.errors.append(f"Blood Altar: Nie można rozpocząć craftingu")
            print(f"    [ERROR] Nie można rozpocząć craftingu")
    
    def verify_ritual_stone_simulation(self):
        """Weryfikacja symulacji Master Ritual Stone"""
        print("\n--- Weryfikacja Master Ritual Stone ---")
        
        # Test 1: Konwersja ID rytuału
        print("  Test 1: Konwersja ID rytuału")
        ritual_sim = MasterRitualStoneSimulation("1.7.10")
        nbt_1710 = {
            "ritualType": "suffering",  # 1.7.10
            "owner": "TestPlayer",
            "isActive": False,
            "cooldown": 0,
            "runningTime": 0,
        }
        ritual_sim.load_from_nbt_1710(nbt_1710)
        
        from uuid import uuid4
        test_uuid = uuid4()
        nbt_1182 = ritual_sim.convert_to_1182_nbt(test_uuid)
        
        # Weryfikacja
        ritual_id = nbt_1182.get("ritualID")
        expected_id = "bloodmagic:well_of_suffering"
        if ritual_id == expected_id:
            print(f"    [OK] Rytuał 'suffering' -> '{ritual_id}'")
        else:
            self.errors.append(f"Ritual: ID powinno być '{expected_id}', jest '{ritual_id}'")
            print(f"    [ERROR] ID powinno być '{expected_id}', jest '{ritual_id}'")
        
        # Test 2: Konwersja właściciela
        print("  Test 2: Konwersja właściciela (nazwa -> UUID)")
        owner_uuid = nbt_1182.get("ownerUUID")
        if owner_uuid == str(test_uuid):
            print(f"    [OK] UUID właściciela poprawnie ustawione")
        else:
            self.errors.append(f"Ritual: UUID właściciela niepoprawne")
            print(f"    [ERROR] UUID właściciela niepoprawne")
        
        # Test 3: Symulacja aktywacji
        print("  Test 3: Symulacja aktywacji")
        ritual_1182 = MasterRitualStoneSimulation("1.18.2")
        ritual_1182.load_from_nbt_1182(nbt_1182)
        
        success, msg = ritual_1182.simulate_activation(10000)
        if success:
            print(f"    [OK] Rytuał aktywowany: {msg}")
        else:
            self.warnings.append(f"Ritual: Nie udało się aktywować: {msg}")
            print(f"    [WARNING] Nie udało się aktywować: {msg}")
    
    def verify_soul_network_simulation(self):
        """Weryfikacja symulacji Soul Network"""
        print("\n--- Weryfikacja Soul Network ---")
        
        # Test 1: Konwersja danych sieci
        print("  Test 1: Konwersja danych sieci")
        network_sim = SoulNetworkSimulation("1.7.10")
        nbt_1710 = {
            "currentEssence": 50000,
            "maxOrb": 3,  # Magician Blood Orb
        }
        network_sim.load_from_nbt_1710(nbt_1710, "TestPlayer")
        
        from uuid import uuid4
        test_uuid = uuid4()
        nbt_1182 = network_sim.convert_to_1182_nbt(test_uuid)
        
        # Weryfikacja
        essence = nbt_1182.get("currentEssence")
        orb_tier = nbt_1182.get("orbTier")
        
        if essence == 50000:
            print(f"    [OK] LP zachowane: {essence}")
        else:
            self.errors.append(f"SoulNetwork: LP powinno być 50000, jest {essence}")
            print(f"    [ERROR] LP powinno być 50000, jest {essence}")
        
        if orb_tier == 3:
            print(f"    [OK] Orb tier zachowany: {orb_tier}")
        else:
            self.errors.append(f"SoulNetwork: Orb tier powinien być 3, jest {orb_tier}")
            print(f"    [ERROR] Orb tier powinien być 3, jest {orb_tier}")
        
        # Test 2: Konwersja Blood Orb
        print("  Test 2: Konwersja Blood Orb (item)")
        orb_sim = BloodOrbSimulation()
        
        orb_1710 = {"id": "AWWayofTime:apprenticeBloodOrb", "Count": 1}
        orb_1710_bound = orb_sim.bind_orb_1710(orb_1710, "TestPlayer")
        orb_1182 = orb_sim.convert_orb_binding(orb_1710_bound, test_uuid)
        
        expected_id = "bloodmagic:apprentice_blood_orb"
        actual_id = orb_1182.get("id")
        if actual_id == expected_id:
            print(f"    [OK] ID orba poprawnie przekonwertowane: {actual_id}")
        else:
            self.errors.append(f"BloodOrb: ID powinno być '{expected_id}', jest '{actual_id}'")
            print(f"    [ERROR] ID powinno być '{expected_id}', jest '{actual_id}'")
        
        binding = orb_1182.get("tag", {}).get("binding", {})
        if binding.get("ownerUUID") == str(test_uuid):
            print(f"    [OK] Binding zawiera UUID")
        else:
            self.errors.append(f"BloodOrb: Binding nie zawiera poprawnego UUID")
            print(f"    [ERROR] Binding nie zawiera poprawnego UUID")
    
    def verify_converter_integration(self):
        """Weryfikacja integracji konwertera"""
        print("\n--- Weryfikacja integracji konwertera ---")
        
        converter = BloodMagicConverter()
        
        # Test 1: Konwersja bloku Blood Altar
        print("  Test 1: Konwersja bloku Altar")
        result = converter.convert_block(
            block_id_1710="AWWayofTime:Altar",
            metadata=0,
            te_nbt_1710={
                "id": "containerAltar",
                "currentEssence": 10000,
                "upgradeLevel": 2,
                "isActive": False,
            },
            pos=(100, 64, 200)
        )
        
        if result.converted and result.block_id_1182 == "bloodmagic:altar":
            print(f"    [OK] Blok Altar poprawnie przekonwertowany")
        else:
            self.errors.append(f"Converter: Altar nie został poprawnie przekonwertowany")
            print(f"    [ERROR] Altar nie został poprawnie przekonwertowany")
        
        if result.be_nbt_1182 and "bloodAltar" in result.be_nbt_1182:
            print(f"    [OK] NBT BlockEntity zawiera 'bloodAltar'")
        else:
            self.errors.append(f"Converter: Brak 'bloodAltar' w NBT")
            print(f"    [ERROR] Brak 'bloodAltar' w NBT")
        
        # Test 2: Konwersja runy
        print("  Test 2: Konwersja Blood Rune")
        result = converter.convert_block(
            block_id_1710="AWWayofTime:bloodRune",
            metadata=1,  # Dislocation
        )
        
        if result.converted and "dislocation" in result.block_id_1182:
            print(f"    [OK] Runa przekonwertowana: {result.block_id_1182}")
        else:
            self.errors.append(f"Converter: Rune nie została poprawnie przekonwertowana")
            print(f"    [ERROR] Rune nie została poprawnie przekonwertowana")
        
        # Test 3: Obsługiwane bloki
        print("  Test 3: Lista obsługiwanych bloków")
        supported = converter.get_supported_blocks()
        required_blocks = [
            "AWWayofTime:Altar",
            "AWWayofTime:bloodRune",
            "AWWayofTime:masterStone",
        ]
        
        missing = [b for b in required_blocks if b not in supported]
        if not missing:
            print(f"    [OK] Wszystkie wymagane bloki obsługiwane")
        else:
            self.warnings.append(f"Converter: Brakujące bloki: {missing}")
            print(f"    [WARNING] Brakujące bloki: {missing}")
    
    def _generate_report(self):
        """Generuj raport weryfikacji"""
        print("\n" + "=" * 70)
        print("PODSUMOWANIE WERYFIKACJI")
        print("=" * 70)
        
        total_tests = 13  # Oszacowana liczba testów
        passed = total_tests - len(self.errors) - len(self.warnings)
        
        print(f"\nWyniki:")
        print(f"  Testy zdane: {passed}/{total_tests}")
        print(f"  Błędy: {len(self.errors)}")
        print(f"  Ostrzeżenia: {len(self.warnings)}")
        
        if self.errors:
            print(f"\nBŁĘDY:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\nOSTRZEŻENIA:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\nZgodność z kodem 1.18.2: {success_rate:.1f}%")
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "success_rate": success_rate,
            "error_details": self.errors,
            "warning_details": self.warnings,
        }


def main():
    """Główna funkcja weryfikacji"""
    verifier = SimulationVerifier()
    report = verifier.verify_all()
    
    # Zapisz raport
    import json
    output_path = Path("output/bloodmagic_simulation_verification.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nRaport zapisano do: {output_path}")
    
    return report


if __name__ == "__main__":
    main()
