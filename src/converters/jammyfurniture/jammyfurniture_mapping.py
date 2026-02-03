"""
Tabela remapowania ID bloków Jammy Furniture Reborn (1.7.10) na mody 1.18.2.

Mody docelowe:
- Supplementaries (supplementaries:*) - meble funkcjonalne
- Handcrafted (handcrafted:*) - meble wypoczynkowe  
- Macaw's Furniture (mcwfurnitures:*) - meble kuchenne i łazienkowe
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Any


@dataclass
class BlockMapping:
    """Pojedyncze mapowanie bloku."""
    source_block: str           # Nazwa bloku 1.7.10 (bez metadata)
    source_meta: int            # Metadata 1.7.10
    target_mod: str             # Mod docelowy 1.18.2
    target_block: str           # Nazwa bloku 1.18.2
    target_state: Dict[str, Any]  # Blockstate 1.18.2
    notes: str = ""             # Uwagi dotyczące konwersji
    preserve_inventory: bool = False  # Czy zachować inventory
    

# =============================================================================
# JAMMY FURNITURE -> MODY 1.18.2
# =============================================================================

JAMMY_FURNITURE_MAPPINGS: List[BlockMapping] = [
    # =========================================================================
    # WOOD BLOCKS ONE - Zegar, Rolety, Stół craftingowy, Blat kuchenny, Stół
    # =========================================================================
    # Clock Base (dekoracja)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=0,
        target_mod="supplementaries",
        target_block="clock_block",
        target_state={},
        notes="Baza zegara - dekoracja"
    ),
    # Clock Middle (środek zegara)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=1,
        target_mod="supplementaries",
        target_block="clock_block",
        target_state={},
        notes="Środek zegara (orientacja N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=2,
        target_mod="supplementaries",
        target_block="clock_block",
        target_state={},
        notes="Środek zegara (orientacja E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=3,
        target_mod="supplementaries",
        target_block="clock_block",
        target_state={},
        notes="Środek zegara (orientacja S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=4,
        target_mod="supplementaries",
        target_block="clock_block",
        target_state={},
        notes="Środek zegara (orientacja W)"
    ),
    # Clock Top (wierzchołek zegara)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=5,
        target_mod="supplementaries",
        target_block="clock_block",
        target_state={},
        notes="Wierzchołek zegara (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=6,
        target_mod="supplementaries",
        target_block="clock_block",
        target_state={},
        notes="Wierzchołek zegara (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=7,
        target_mod="supplementaries",
        target_block="clock_block",
        target_state={},
        notes="Wierzchołek zegara (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=8,
        target_mod="supplementaries",
        target_block="clock_block",
        target_state={},
        notes="Wierzchołek zegara (W)"
    ),
    # Blinds (Rolety)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=9,
        target_mod="mcwfurnitures",
        target_block="oak_blinds",
        target_state={"facing": "north", "open": "false"},
        notes="Rolety zamknięte (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=10,
        target_mod="mcwfurnitures",
        target_block="oak_blinds",
        target_state={"facing": "east", "open": "false"},
        notes="Rolety zamknięte (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=11,
        target_mod="mcwfurnitures",
        target_block="oak_blinds",
        target_state={"facing": "south", "open": "false"},
        notes="Rolety zamknięte (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=12,
        target_mod="mcwfurnitures",
        target_block="oak_blinds",
        target_state={"facing": "west", "open": "false"},
        notes="Rolety zamknięte (W)"
    ),
    # Crafting Side (stół craftingowy)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=13,
        target_mod="minecraft",
        target_block="crafting_table",
        target_state={},
        notes="Stół craftingowy - zachować inventory z TE",
        preserve_inventory=True
    ),
    # Kitchen Side (blat kuchenny)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=14,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={},
        notes="Blat kuchenny"
    ),
    # Table (stół)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksOne",
        source_meta=15,
        target_mod="handcrafted",
        target_block="table",
        target_state={"wood_type": "oak"},
        notes="Stół drewniany"
    ),
    
    # =========================================================================
    # WOOD BLOCKS TWO - Szafki kuchenne, TV, Kosz
    # =========================================================================
    # Kitchen Cupboard (szafka kuchenna zamknięta)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "north"},
        notes="Szafka kuchenna (N) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=1,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "east"},
        notes="Szafka kuchenna (E) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=2,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "south"},
        notes="Szafka kuchenna (S) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=3,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "west"},
        notes="Szafka kuchenna (W) - zachować inventory",
        preserve_inventory=True
    ),
    # Kitchen Cupboard Shelf (szafka otwarta)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_drawer",
        target_state={"facing": "north"},
        notes="Szafka kuchenna otwarta (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=5,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_drawer",
        target_state={"facing": "east"},
        notes="Szafka kuchenna otwarta (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=6,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_drawer",
        target_state={"facing": "south"},
        notes="Szafka kuchenna otwarta (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=7,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_drawer",
        target_state={"facing": "west"},
        notes="Szafka kuchenna otwarta (W)"
    ),
    # Television
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=8,
        target_mod="supplementaries",
        target_block="blackboard",
        target_state={"facing": "north"},
        notes="Telewizor (placeholder - blackboard)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=9,
        target_mod="supplementaries",
        target_block="blackboard",
        target_state={"facing": "east"},
        notes="Telewizor (placeholder - blackboard)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=10,
        target_mod="supplementaries",
        target_block="blackboard",
        target_state={"facing": "south"},
        notes="Telewizor (placeholder - blackboard)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=11,
        target_mod="supplementaries",
        target_block="blackboard",
        target_state={"facing": "west"},
        notes="Telewizor (placeholder - blackboard)"
    ),
    # Basket
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=12,
        target_mod="handcrafted",
        target_block="basket",
        target_state={},
        notes="Kosz - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=13,
        target_mod="handcrafted",
        target_block="basket",
        target_state={},
        notes="Kosz - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=14,
        target_mod="handcrafted",
        target_block="basket",
        target_state={},
        notes="Kosz - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksTwo",
        source_meta=15,
        target_mod="handcrafted",
        target_block="basket",
        target_state={},
        notes="Kosz - zachować inventory",
        preserve_inventory=True
    ),
    
    # =========================================================================
    # WOOD BLOCKS THREE - Krzesło, Radio
    # =========================================================================
    # Chair (krzesło)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksThree",
        source_meta=0,
        target_mod="handcrafted",
        target_block="chair",
        target_state={"wood_type": "oak", "facing": "north"},
        notes="Krzesło (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksThree",
        source_meta=1,
        target_mod="handcrafted",
        target_block="chair",
        target_state={"wood_type": "oak", "facing": "east"},
        notes="Krzesło (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksThree",
        source_meta=2,
        target_mod="handcrafted",
        target_block="chair",
        target_state={"wood_type": "oak", "facing": "south"},
        notes="Krzesło (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksThree",
        source_meta=3,
        target_mod="handcrafted",
        target_block="chair",
        target_state={"wood_type": "oak", "facing": "west"},
        notes="Krzesło (W)"
    ),
    # Radio
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksThree",
        source_meta=4,
        target_mod="supplementaries",
        target_block="speaker_block",
        target_state={},
        notes="Radio (placeholder)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksThree",
        source_meta=5,
        target_mod="supplementaries",
        target_block="speaker_block",
        target_state={},
        notes="Radio (placeholder)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksThree",
        source_meta=6,
        target_mod="supplementaries",
        target_block="speaker_block",
        target_state={},
        notes="Radio (placeholder)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksThree",
        source_meta=7,
        target_mod="supplementaries",
        target_block="speaker_block",
        target_state={},
        notes="Radio (placeholder)"
    ),
    
    # =========================================================================
    # WOOD BLOCKS FOUR - Szafa, Wieszak
    # =========================================================================
    # Wardrobe (szafa)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="oak_wardrobe",
        target_state={"facing": "north"},
        notes="Szafa dolna (N) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=1,
        target_mod="mcwfurnitures",
        target_block="oak_wardrobe",
        target_state={"facing": "east"},
        notes="Szafa dolna (E) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=2,
        target_mod="mcwfurnitures",
        target_block="oak_wardrobe",
        target_state={"facing": "south"},
        notes="Szafa dolna (S) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=3,
        target_mod="mcwfurnitures",
        target_block="oak_wardrobe",
        target_state={"facing": "west"},
        notes="Szafa dolna (W) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="oak_drawer",
        target_state={"facing": "north"},
        notes="Szafa górna (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=5,
        target_mod="mcwfurnitures",
        target_block="oak_drawer",
        target_state={"facing": "east"},
        notes="Szafa górna (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=6,
        target_mod="mcwfurnitures",
        target_block="oak_drawer",
        target_state={"facing": "south"},
        notes="Szafa górna (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=7,
        target_mod="mcwfurnitures",
        target_block="oak_drawer",
        target_state={"facing": "west"},
        notes="Szafa górna (W)"
    ),
    # Coat Stand (wieszak)
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=8,
        target_mod="mcwfurnitures",
        target_block="oak_coffee_table",  # Placeholder - najbliższy mebel
        target_state={},
        notes="Wieszak (placeholder)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=9,
        target_mod="mcwfurnitures",
        target_block="oak_coffee_table",
        target_state={},
        notes="Wieszak (placeholder)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=10,
        target_mod="mcwfurnitures",
        target_block="oak_coffee_table",
        target_state={},
        notes="Wieszak (placeholder)"
    ),
    BlockMapping(
        source_block="jammyfurniture:WoodBlocksFour",
        source_meta=11,
        target_mod="mcwfurnitures",
        target_block="oak_coffee_table",
        target_state={},
        notes="Wieszak (placeholder)"
    ),
    
    # =========================================================================
    # IRON BLOCKS ONE - Lodówka, Zamrażarka, Kuchenka, Kosz
    # =========================================================================
    # Fridge (lodówka dolna)
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="refrigerator",
        target_state={"facing": "north", "part": "lower"},
        notes="Lodówka dolna (N) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=1,
        target_mod="mcwfurnitures",
        target_block="refrigerator",
        target_state={"facing": "east", "part": "lower"},
        notes="Lodówka dolna (E) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=2,
        target_mod="mcwfurnitures",
        target_block="refrigerator",
        target_state={"facing": "south", "part": "lower"},
        notes="Lodówka dolna (S) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=3,
        target_mod="mcwfurnitures",
        target_block="refrigerator",
        target_state={"facing": "west", "part": "lower"},
        notes="Lodówka dolna (W) - zachować inventory",
        preserve_inventory=True
    ),
    # Freezer (lodówka górna/zamrażarka)
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="refrigerator",
        target_state={"facing": "north", "part": "upper"},
        notes="Zamrażarka (N) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=5,
        target_mod="mcwfurnitures",
        target_block="refrigerator",
        target_state={"facing": "east", "part": "upper"},
        notes="Zamrażarka (E) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=6,
        target_mod="mcwfurnitures",
        target_block="refrigerator",
        target_state={"facing": "south", "part": "upper"},
        notes="Zamrażarka (S) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=7,
        target_mod="mcwfurnitures",
        target_block="refrigerator",
        target_state={"facing": "west", "part": "upper"},
        notes="Zamrażarka (W) - zachować inventory",
        preserve_inventory=True
    ),
    # Cooker (kuchenka)
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=8,
        target_mod="mcwfurnitures",
        target_block="stove",
        target_state={"facing": "north", "lit": "false"},
        notes="Kuchenka (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=9,
        target_mod="mcwfurnitures",
        target_block="stove",
        target_state={"facing": "east", "lit": "false"},
        notes="Kuchenka (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=10,
        target_mod="mcwfurnitures",
        target_block="stove",
        target_state={"facing": "south", "lit": "false"},
        notes="Kuchenka (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=11,
        target_mod="mcwfurnitures",
        target_block="stove",
        target_state={"facing": "west", "lit": "false"},
        notes="Kuchenka (W)"
    ),
    # Rubbish Bin (kosz na śmieci)
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=12,
        target_mod="mcwfurnitures",
        target_block="trash_can",
        target_state={},
        notes="Kosz na śmieci - zachować inventory",
        preserve_inventory=True
    ),
    # Coffee Table (stolik kawowy)
    BlockMapping(
        source_block="jammyfurniture:IronBlocksOne",
        source_meta=13,
        target_mod="mcwfurnitures",
        target_block="oak_coffee_table",
        target_state={},
        notes="Stolik kawowy"
    ),
    
    # =========================================================================
    # IRON BLOCKS TWO - Zmywarka, Pralka
    # =========================================================================
    # Dishwasher (zmywarka)
    BlockMapping(
        source_block="jammyfurniture:IronBlocksTwo",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",  # Placeholder
        target_state={"facing": "north"},
        notes="Zmywarka (N) - brak bezpośredniego odpowiednika",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksTwo",
        source_meta=1,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "east"},
        notes="Zmywarka (E) - brak bezpośredniego odpowiednika",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksTwo",
        source_meta=2,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "south"},
        notes="Zmywarka (S) - brak bezpośredniego odpowiednika",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksTwo",
        source_meta=3,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "west"},
        notes="Zmywarka (W) - brak bezpośredniego odpowiednika",
        preserve_inventory=True
    ),
    # Washing Machine (pralka)
    BlockMapping(
        source_block="jammyfurniture:IronBlocksTwo",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",  # Placeholder
        target_state={"facing": "north"},
        notes="Pralka (N) - brak bezpośredniego odpowiednika",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksTwo",
        source_meta=5,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "east"},
        notes="Pralka (E) - brak bezpośredniego odpowiednika",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksTwo",
        source_meta=6,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "south"},
        notes="Pralka (S) - brak bezpośredniego odpowiednika",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:IronBlocksTwo",
        source_meta=7,
        target_mod="mcwfurnitures",
        target_block="oak_kitchen_cabinet",
        target_state={"facing": "west"},
        notes="Pralka (W) - brak bezpośredniego odpowiednika",
        preserve_inventory=True
    ),
    
    # =========================================================================
    # CERAMIC BLOCKS ONE - Szafka łazienkowa, Umywalka, Zlew, Toaleta
    # =========================================================================
    # Bathroom Cupboard (szafka łazienkowa)
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="bathroom_cabinet",
        target_state={"facing": "north"},
        notes="Szafka łazienkowa (N) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=1,
        target_mod="mcwfurnitures",
        target_block="bathroom_cabinet",
        target_state={"facing": "east"},
        notes="Szafka łazienkowa (E) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=2,
        target_mod="mcwfurnitures",
        target_block="bathroom_cabinet",
        target_state={"facing": "south"},
        notes="Szafka łazienkowa (S) - zachować inventory",
        preserve_inventory=True
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=3,
        target_mod="mcwfurnitures",
        target_block="bathroom_cabinet",
        target_state={"facing": "west"},
        notes="Szafka łazienkowa (W) - zachować inventory",
        preserve_inventory=True
    ),
    # Bathroom Sink (umywalka łazienkowa)
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="sink",
        target_state={"facing": "north"},
        notes="Umywalka (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=5,
        target_mod="mcwfurnitures",
        target_block="sink",
        target_state={"facing": "east"},
        notes="Umywalka (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=6,
        target_mod="mcwfurnitures",
        target_block="sink",
        target_state={"facing": "south"},
        notes="Umywalka (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=7,
        target_mod="mcwfurnitures",
        target_block="sink",
        target_state={"facing": "west"},
        notes="Umywalka (W)"
    ),
    # Kitchen Sink (zlew kuchenny)
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=8,
        target_mod="mcwfurnitures",
        target_block="kitchen_sink",
        target_state={"facing": "north"},
        notes="Zlew kuchenny (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=9,
        target_mod="mcwfurnitures",
        target_block="kitchen_sink",
        target_state={"facing": "east"},
        notes="Zlew kuchenny (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=10,
        target_mod="mcwfurnitures",
        target_block="kitchen_sink",
        target_state={"facing": "south"},
        notes="Zlew kuchenny (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=11,
        target_mod="mcwfurnitures",
        target_block="kitchen_sink",
        target_state={"facing": "west"},
        notes="Zlew kuchenny (W)"
    ),
    # Toilet (toaleta)
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=12,
        target_mod="mcwfurnitures",
        target_block="toilet",
        target_state={"facing": "north"},
        notes="Toaleta (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=13,
        target_mod="mcwfurnitures",
        target_block="toilet",
        target_state={"facing": "east"},
        notes="Toaleta (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=14,
        target_mod="mcwfurnitures",
        target_block="toilet",
        target_state={"facing": "south"},
        notes="Toaleta (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:CeramicBlocksOne",
        source_meta=15,
        target_mod="mcwfurnitures",
        target_block="toilet",
        target_state={"facing": "west"},
        notes="Toaleta (W)"
    ),
    
    # =========================================================================
    # BATH - Wanna
    # =========================================================================
    BlockMapping(
        source_block="jammyfurniture:Bath",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="bathtub",
        target_state={"facing": "north"},
        notes="Wanna (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:Bath",
        source_meta=1,
        target_mod="mcwfurnitures",
        target_block="bathtub",
        target_state={"facing": "east"},
        notes="Wanna (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:Bath",
        source_meta=2,
        target_mod="mcwfurnitures",
        target_block="bathtub",
        target_state={"facing": "south"},
        notes="Wanna (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:Bath",
        source_meta=3,
        target_mod="mcwfurnitures",
        target_block="bathtub",
        target_state={"facing": "west"},
        notes="Wanna (W)"
    ),
    
    # =========================================================================
    # LIGHTS - Oświetlenie
    # =========================================================================
    # Lights On
    BlockMapping(
        source_block="jammyfurniture:LightsOn",
        source_meta=0,
        target_mod="supplementaries",
        target_block="sconce",
        target_state={"lit": "true"},
        notes="Światło sufitowe włączone"
    ),
    BlockMapping(
        source_block="jammyfurniture:LightsOn",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="modern_lamp",
        target_state={"lit": "true"},
        notes="Lampa zewnętrzna włączona"
    ),
    BlockMapping(
        source_block="jammyfurniture:LightsOn",
        source_meta=8,
        target_mod="mcwfurnitures",
        target_block="modern_lamp",
        target_state={"lit": "true"},
        notes="Lampa stołowa włączona"
    ),
    # Lights Off
    BlockMapping(
        source_block="jammyfurniture:LightsOff",
        source_meta=0,
        target_mod="supplementaries",
        target_block="sconce",
        target_state={"lit": "false"},
        notes="Światło sufitowe wyłączone"
    ),
    BlockMapping(
        source_block="jammyfurniture:LightsOff",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="modern_lamp",
        target_state={"lit": "false"},
        notes="Lampa zewnętrzna wyłączona"
    ),
    BlockMapping(
        source_block="jammyfurniture:LightsOff",
        source_meta=8,
        target_mod="mcwfurnitures",
        target_block="modern_lamp",
        target_state={"lit": "false"},
        notes="Lampa stołowa wyłączona"
    ),
    
    # =========================================================================
    # ARMCHAIR - Fotel
    # =========================================================================
    BlockMapping(
        source_block="jammyfurniture:ArmChair",
        source_meta=0,
        target_mod="handcrafted",
        target_block="couch",
        target_state={"color": "red", "facing": "north"},  # Couch jako najbliższy odpowiednik
        notes="Fotel (N) - w Handcrafted można siedzieć na couch"
    ),
    BlockMapping(
        source_block="jammyfurniture:ArmChair",
        source_meta=4,
        target_mod="handcrafted",
        target_block="couch",
        target_state={"color": "red", "facing": "east"},
        notes="Fotel (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:ArmChair",
        source_meta=8,
        target_mod="handcrafted",
        target_block="couch",
        target_state={"color": "red", "facing": "south"},
        notes="Fotel (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:ArmChair",
        source_meta=12,
        target_mod="handcrafted",
        target_block="couch",
        target_state={"color": "red", "facing": "west"},
        notes="Fotel (W)"
    ),
    
    # =========================================================================
    # SOFA PARTS - Części sofy
    # =========================================================================
    # Sofa Left
    BlockMapping(
        source_block="jammyfurniture:SofaLeft",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "north", "shape": "left"},
        notes="Sofa lewa (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaLeft",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "east", "shape": "left"},
        notes="Sofa lewa (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaLeft",
        source_meta=8,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "south", "shape": "left"},
        notes="Sofa lewa (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaLeft",
        source_meta=12,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "west", "shape": "left"},
        notes="Sofa lewa (W)"
    ),
    # Sofa Right
    BlockMapping(
        source_block="jammyfurniture:SofaRight",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "north", "shape": "right"},
        notes="Sofa prawa (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaRight",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "east", "shape": "right"},
        notes="Sofa prawa (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaRight",
        source_meta=8,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "south", "shape": "right"},
        notes="Sofa prawa (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaRight",
        source_meta=12,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "west", "shape": "right"},
        notes="Sofa prawa (W)"
    ),
    # Sofa Center
    BlockMapping(
        source_block="jammyfurniture:SofaCenter",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "north", "shape": "straight"},
        notes="Sofa środek (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaCenter",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "east", "shape": "straight"},
        notes="Sofa środek (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaCenter",
        source_meta=8,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "south", "shape": "straight"},
        notes="Sofa środek (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaCenter",
        source_meta=12,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "west", "shape": "straight"},
        notes="Sofa środek (W)"
    ),
    # Sofa Corner
    BlockMapping(
        source_block="jammyfurniture:SofaCorner",
        source_meta=0,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "north", "shape": "inner_left"},
        notes="Sofa narożnik (N)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaCorner",
        source_meta=4,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "east", "shape": "inner_left"},
        notes="Sofa narożnik (E)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaCorner",
        source_meta=8,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "south", "shape": "inner_left"},
        notes="Sofa narożnik (S)"
    ),
    BlockMapping(
        source_block="jammyfurniture:SofaCorner",
        source_meta=12,
        target_mod="mcwfurnitures",
        target_block="sofa",
        target_state={"facing": "west", "shape": "inner_left"},
        notes="Sofa narożnik (W)"
    ),
    
    # =========================================================================
    # ROOFING BLOCKS - Dachówki
    # =========================================================================
    BlockMapping(
        source_block="jammyfurniture:RoofingBlocksOne",
        source_meta=0,
        target_mod="minecraft",
        target_block="brick_stairs",
        target_state={"facing": "north"},
        notes="Dachówka - schody (N)"
    ),
    # ... pozostałe dachówki - uproszczone do schodów
    
    # =========================================================================
    # MISC BLOCKS - Różne (komin, piecek, choinka)
    # =========================================================================
    BlockMapping(
        source_block="jammyfurniture:MiscBlocksOne",
        source_meta=0,
        target_mod="supplementaries",
        target_block="chimney",
        target_state={},
        notes="Komin"
    ),
    BlockMapping(
        source_block="jammyfurniture:MiscBlocksOne",
        source_meta=4,
        target_mod="minecraft",
        target_block="stone_bricks",
        target_state={},
        notes="Półka nad kominkiem - placeholder"
    ),
    BlockMapping(
        source_block="jammyfurniture:MiscBlocksOne",
        source_meta=8,
        target_mod="minecraft",
        target_block="spruce_leaves",
        target_state={},
        notes="Choinka świąteczna - placeholder"
    ),
]


# =============================================================================
# FUNKCJE POMOCNICZE
# =============================================================================

def get_mapping(source_block: str, source_meta: int) -> Optional[BlockMapping]:
    """Znajduje mapowanie dla danego bloku i metadata."""
    for mapping in JAMMY_FURNITURE_MAPPINGS:
        if mapping.source_block == source_block and mapping.source_meta == source_meta:
            return mapping
    return None


def get_all_mappings_for_block(source_block: str) -> List[BlockMapping]:
    """Zwraca wszystkie mapowania dla danego bloku."""
    return [m for m in JAMMY_FURNITURE_MAPPINGS if m.source_block == source_block]


def generate_target_id(mapping: BlockMapping) -> str:
    """Generuje pełne ID bloku docelowego."""
    state_str = ",".join(f"{k}={v}" for k, v in mapping.target_state.items())
    if state_str:
        return f"{mapping.target_mod}:{mapping.target_block}[{state_str}]"
    return f"{mapping.target_mod}:{mapping.target_block}"


def print_mapping_table():
    """Drukuje tabelę mapowania w formacie czytelnym dla człowieka."""
    print("=" * 100)
    print("JAMMY FURNITURE REBORN - TABELA REMAPOWANIA ID")
    print("=" * 100)
    print(f"{'Blok 1.7.10':<35} {'Meta':<6} {'->':<4} {'Blok 1.18.2':<50}")
    print("-" * 100)
    
    for mapping in JAMMY_FURNITURE_MAPPINGS:
        source = f"{mapping.source_block}:{mapping.source_meta}"
        target = generate_target_id(mapping)
        print(f"{mapping.source_block:<35} {mapping.source_meta:<6} {'->':<4} {target:<50}")
    
    print("-" * 100)
    print(f"Łącznie mapowań: {len(JAMMY_FURNITURE_MAPPINGS)}")


if __name__ == "__main__":
    print_mapping_table()
