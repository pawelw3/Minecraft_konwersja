"""
Symulacja rytuału Well of Suffering - Blood Magic 1.7.10 vs 1.18.2

Source mapping:
- 1.7.10: WayofTime/alchemicalWizardry/common/rituals/RitualEffectWellOfSuffering.java
  - performEffect: linie 28-109
  - getCostPerRefresh: linie 111-116
  - getRitualComponentList: linie 118-158
  
- 1.18.2: wayoftime/bloodmagic/ritual/types/RitualWellOfSuffering.java (lub podobna klasa)

Kluczowe parametry rytuału:
- timeDelay: 25 ticków (co 1.25 sekundy)
- amount: 10 LP za każdego moba
- Zasięg horyzontalny: 10 bloków
- Zasięg wertykalny: 10 bloków (20 z Potentia Reagent)
- Koszt: 5000 LP (zazwyczaj z konfiguracji)

Reagenty (tylko 1.7.10):
- Tennebrae: podwaja ilość LP (drain=5)
- Potentia: podwaja zasięg wertykalny (drain=10)
- Offensa: podwaja obrażenia i LP (drain=3)

W 1.18.2 reagenty zostały zastąpione przez Demon Will system.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
import math


@dataclass
class MobEntity:
    """Reprezentacja moba do symulacji"""
    entity_id: str
    x: float
    y: float
    z: float
    health: float
    max_health: float
    is_alive: bool = True


@dataclass
class ReagentStatus:
    """Status reagentów (tylko 1.7.10)"""
    tennebrae: bool = False
    potentia: bool = False
    offensa: bool = False


@dataclass
class AltarPosition:
    """Pozycja ołtarza względem rytuału"""
    x: int
    y: int
    z: int


class WellOfSufferingSimulation:
    """
    Symulacja rytuału Well of Suffering
    
    Rytuał zadaje obrażenia mobom w zasięgu i generuje LP w podłączonym ołtarzu.
    """
    
    # Stałe z kodu źródłowego
    TIME_DELAY = 25  # ticków między aktywacjami
    BASE_LP_PER_MOB = 10
    HORIZONTAL_RANGE = 10
    BASE_VERTICAL_RANGE = 10
    POTENTIA_VERTICAL_RANGE = 20
    
    # Koszty reagentów (1.7.10)
    TENNEBRAE_DRAIN = 5
    POTENTIA_DRAIN = 10
    OFFENSA_DRAIN = 3
    
    def __init__(self, version: str = "1.7.10"):
        """
        Args:
            version: "1.7.10" lub "1.18.2"
        """
        self.version = version
        self.mobs: List[MobEntity] = []
        self.altar: Optional[AltarPosition] = None
        self.reagents = ReagentStatus()
        
    def set_altar_position(self, rel_x: int, rel_y: int, rel_z: int) -> None:
        """Ustaw pozycję ołtarza względem rytuału"""
        self.altar = AltarPosition(rel_x, rel_y, rel_z)
    
    def add_mob(self, mob: MobEntity) -> None:
        """Dodaj moba do symulacji"""
        self.mobs.append(mob)
    
    def set_reagents(self, tennebrae: bool = False, potentia: bool = False, offensa: bool = False) -> None:
        """Ustaw aktywne reagenty (tylko 1.7.10)"""
        self.reagents.tennebrae = tennebrae
        self.reagents.potentia = potentia
        self.reagents.offensa = offensa
    
    def simulate_tick(self, tick: int, soul_network_lp: int) -> Dict[str, Any]:
        """
        Symuluj jeden tick rytuału
        
        Source 1.7.10: RitualEffectWellOfSuffering.performEffect()
        
        Args:
            tick: Numer ticku
            soul_network_lp: Aktualna ilość LP w sieci właściciela
            
        Returns:
            Dict z wynikami symulacji
        """
        result = {
            "activated": False,
            "lp_generated": 0,
            "mobs_damaged": 0,
            "soul_network_cost": 0,
            "error": None,
        }
        
        # Sprawdź czy to czas aktywacji (co TIME_DELAY ticków)
        if tick % self.TIME_DELAY != 0:
            return result
        
        # Sprawdź czy jest ołtarz
        if not self.altar:
            result["error"] = "Brak ołtarza w zasięgu"
            return result
        
        # Oblicz zasięg
        vertical_range = self.POTENTIA_VERTICAL_RANGE if self.reagents.potentia else self.BASE_VERTICAL_RANGE
        
        # Znajdź moby w zasięgu
        mobs_in_range = self._get_mobs_in_range(vertical_range)
        
        # Sprawdź czy mamy wystarczająco LP w sieci
        base_cost = self._get_base_cost()
        total_cost = base_cost * len(mobs_in_range)
        
        if soul_network_lp < total_cost:
            result["error"] = f"Niewystarczająca ilość LP (potrzeba: {total_cost}, dostępne: {soul_network_lp})"
            return result
        
        # Zadaj obrażenia mobom i generuj LP
        result["activated"] = True
        lp_per_mob = self.BASE_LP_PER_MOB
        
        # Zastosuj mnożniki z reagentów
        if self.reagents.tennebrae:
            lp_per_mob *= 2
        if self.reagents.offensa:
            lp_per_mob *= 2
        
        for mob in mobs_in_range:
            # Obrażenia
            damage = 2 if self.reagents.offensa else 1
            
            # Symulacja obrażeń
            if mob.health > damage:
                mob.health -= damage
                result["mobs_damaged"] += 1
                result["lp_generated"] += lp_per_mob
            else:
                mob.is_alive = False
        
        result["soul_network_cost"] = total_cost
        
        return result
    
    def _get_mobs_in_range(self, vertical_range: int) -> List[MobEntity]:
        """Znajdź moby w zasięgu rytuału"""
        in_range = []
        
        for mob in self.mobs:
            if not mob.is_alive:
                continue
            
            # Sprawdź odległość horyzontalną
            h_dist = math.sqrt(mob.x ** 2 + mob.z ** 2)
            
            # Sprawdź odległość wertykalną
            v_dist = abs(mob.y)
            
            if h_dist <= self.HORIZONTAL_RANGE and v_dist <= vertical_range:
                in_range.append(mob)
        
        return in_range
    
    def _get_base_cost(self) -> int:
        """Pobierz podstawowy koszt rytuału"""
        # W 1.7.10 koszt zależy od konfiguracji, domyślnie 5000
        # W 1.18.2 może być inny
        if self.version == "1.7.10":
            return 5000  # AlchemicalWizardry.ritualCostSuffering[1]
        return 5000
    
    def get_ritual_structure(self) -> List[Tuple[int, int, int, str]]:
        """
        Zwróć wymaganą strukturę rytuału
        
        Source 1.7.10: RitualEffectWellOfSuffering.getRitualComponentList()
        """
        return [
            # Pierścień wewnętrzny - FIRE
            (1, 0, 1, "FIRE"),
            (-1, 0, 1, "FIRE"),
            (1, 0, -1, "FIRE"),
            (-1, 0, -1, "FIRE"),
            (2, -1, 2, "FIRE"),
            (2, -1, -2, "FIRE"),
            (-2, -1, 2, "FIRE"),
            (-2, -1, -2, "FIRE"),
            # Środkowe - EARTH
            (0, -1, 2, "EARTH"),
            (2, -1, 0, "EARTH"),
            (0, -1, -2, "EARTH"),
            (-2, -1, 0, "EARTH"),
            # Rogi - DUSK
            (-3, -1, -3, "DUSK"),
            (3, -1, -3, "DUSK"),
            (-3, -1, 3, "DUSK"),
            (3, -1, 3, "DUSK"),
            # Zewnętrzne - WATER
            (2, -1, 4, "WATER"),
            (4, -1, 2, "WATER"),
            (-2, -1, 4, "WATER"),
            (4, -1, -2, "WATER"),
            (2, -1, -4, "WATER"),
            (-4, -1, 2, "WATER"),
            (-2, -1, -4, "WATER"),
            (-4, -1, -2, "WATER"),
            (1, 0, 4, "WATER"),
            (4, 0, 1, "WATER"),
            (1, 0, -4, "WATER"),
            (-4, 0, 1, "WATER"),
            (-1, 0, 4, "WATER"),
            (4, 0, -1, "WATER"),
            (-1, 0, -4, "WATER"),
            (-4, 0, -1, "WATER"),
            # Góra - AIR
            (4, 1, 0, "AIR"),
            (0, 1, 4, "AIR"),
            (-4, 1, 0, "AIR"),
            (0, 1, -4, "AIR"),
        ]
    
    def simulate_long_term(self, duration_ticks: int, initial_lp: int, 
                          mob_spawn_rate: float = 0.1) -> Dict[str, Any]:
        """
        Symulacja długoterminowa rytuału
        
        Args:
            duration_ticks: Czas symulacji w tickach
            initial_lp: Początkowa ilość LP w sieci
            mob_spawn_rate: Szansa na spawn moba na tick
            
        Returns:
            Podsumowanie symulacji
        """
        current_lp = initial_lp
        total_lp_generated = 0
        total_mobs_damaged = 0
        total_cost = 0
        activations = 0
        
        for tick in range(duration_ticks):
            # Symulacja spawnu mobów
            import random
            if random.random() < mob_spawn_rate:
                # Spawn moba w losowej pozycji w zasięgu
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, self.HORIZONTAL_RANGE)
                x = radius * math.cos(angle)
                z = radius * math.sin(angle)
                y = random.uniform(-5, 5)
                
                self.add_mob(MobEntity(
                    entity_id=f"zombie_{tick}",
                    x=x, y=y, z=z,
                    health=20.0,
                    max_health=20.0
                ))
            
            # Symulacja rytuału
            result = self.simulate_tick(tick, current_lp)
            
            if result["activated"]:
                activations += 1
                total_lp_generated += result["lp_generated"]
                total_mobs_damaged += result["mobs_damaged"]
                total_cost += result["soul_network_cost"]
                current_lp -= result["soul_network_cost"]
        
        return {
            "duration_ticks": duration_ticks,
            "activations": activations,
            "total_lp_generated": total_lp_generated,
            "total_mobs_damaged": total_mobs_damaged,
            "total_lp_cost": total_cost,
            "net_lp_gain": total_lp_generated - total_cost,
            "final_soul_network_lp": current_lp,
            "mobs_remaining": len([m for m in self.mobs if m.is_alive]),
        }


def test_well_of_suffering_simulation():
    """Test symulacji Well of Suffering"""
    print("=== Test symulacji Well of Suffering ===\n")
    
    # Utwórz symulację
    ritual = WellOfSufferingSimulation("1.7.10")
    
    # Ustaw ołtarz na pozycji (0, -5, 0) - 5 bloków poniżej
    ritual.set_altar_position(0, -5, 0)
    
    # Dodaj kilka mobów w zasięgu
    mobs = [
        MobEntity("zombie_1", 3.0, 2.0, 4.0, 20.0, 20.0),
        MobEntity("zombie_2", -5.0, 0.0, 2.0, 20.0, 20.0),
        MobEntity("skeleton_1", 8.0, 1.0, -3.0, 20.0, 20.0),
        MobEntity("creeper_1", 0.0, -8.0, 0.0, 20.0, 20.0),  # Poza zasięgiem wertykalnym
        MobEntity("spider_1", 15.0, 0.0, 0.0, 16.0, 16.0),   # Poza zasięgiem horyzontalnym
    ]
    
    for mob in mobs:
        ritual.add_mob(mob)
    
    print(f"Dodano {len(ritual.mobs)} mobów do symulacji")
    
    # Test aktywacji
    print("\n=== Test pojedynczej aktywacji ===")
    soul_network_lp = 50000
    
    result = ritual.simulate_tick(0, soul_network_lp)  # Tick 0 - aktywacja
    print(f"Aktywowana: {result['activated']}")
    print(f"Wygenerowano LP: {result['lp_generated']}")
    print(f"Mobów obrażonych: {result['mobs_damaged']}")
    print(f"Koszt sieci: {result['soul_network_cost']}")
    
    # Test z reagentami
    print("\n=== Test z reagentami ===")
    ritual2 = WellOfSufferingSimulation("1.7.10")
    ritual2.set_altar_position(0, -5, 0)
    
    for mob in mobs:
        ritual2.add_mob(MobEntity(mob.entity_id, mob.x, mob.y, mob.z, 20.0, 20.0))
    
    # Aktywuj reagenty
    ritual2.set_reagents(tennebrae=True, offensa=True)
    
    result2 = ritual2.simulate_tick(0, soul_network_lp)
    print(f"Z Tennebrae + Offensa:")
    print(f"  Wygenerowano LP: {result2['lp_generated']} (x4 mnożnik)")
    print(f"  Mobów obrażonych: {result2['mobs_damaged']}")
    
    # Struktura rytuału
    print("\n=== Struktura rytuału ===")
    structure = ritual.get_ritual_structure()
    print(f"Wymaga {len(structure)} Ritual Stones:")
    
    type_counts = {}
    for x, y, z, rtype in structure:
        type_counts[rtype] = type_counts.get(rtype, 0) + 1
    
    for rtype, count in sorted(type_counts.items()):
        print(f"  {rtype}: {count}")
    
    # Długoterminowa symulacja
    print("\n=== Symulacja 5-minutowa (6000 ticków) ===")
    ritual3 = WellOfSufferingSimulation("1.7.10")
    ritual3.set_altar_position(0, -5, 0)
    
    summary = ritual3.simulate_long_term(
        duration_ticks=6000,  # 5 minut
        initial_lp=100000,
        mob_spawn_rate=0.05   # 5% szans na spawn co tick
    )
    
    print(f"Aktywacje rytuału: {summary['activations']}")
    print(f"Całkowicie wygenerowano LP: {summary['total_lp_generated']}")
    print(f"Całkowity koszt: {summary['total_lp_cost']}")
    print(f"Netto zysk LP: {summary['net_lp_gain']}")
    print(f"Mobów obrażonych: {summary['total_mobs_damaged']}")
    print(f"Mobów pozostało: {summary['mobs_remaining']}")
    print(f"Finalny stan LP: {summary['final_soul_network_lp']}")


if __name__ == "__main__":
    test_well_of_suffering_simulation()
