"""
Konwerter bloków Jammy Furniture Reborn z 1.7.10 na 1.18.2.

Obsługuje:
- Konwersję bloków (metadata → blockstates)
- Konwersję Tile Entities (inventory, orientacja)
- Mapowanie inventory items
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from .jammy_furniture_mapping import (
    BlockMapping, 
    JAMMY_FURNITURE_MAPPINGS,
    get_mapping,
    generate_target_id
)

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Wynik konwersji pojedynczego bloku."""
    success: bool
    target_block_id: Optional[str] = None
    target_block_state: Optional[Dict[str, Any]] = None
    target_te: Optional[Dict[str, Any]] = None  # Tile Entity data
    error_message: Optional[str] = None


class JammyFurnitureConverter:
    """
    Konwerter bloków Jammy Furniture Reborn.
    
    Konwertuje:
    - jammyfurniture:* (1.7.10) → supplementaries:* / handcrafted:* / mcwfurnitures:* (1.18.2)
    """
    
    # Tile Entity IDs w Jammy Furniture 1.7.10
    JAMMY_TILE_ENTITIES = {
        "TileEntityWoodBlocksOne",   # Crafting Side
        "TileEntityWoodBlocksTwo",   # Kitchen Cupboard, TV, Basket
        "TileEntityWoodBlocksThree", # Chair, Radio
        "TileEntityWoodBlocksFour",  # Wardrobe, Coat Stand
        "TileEntityIronBlocksOne",   # Fridge, Freezer, Cooker, Rubbish Bin
        "TileEntityIronBlocksTwo",   # Dishwasher, Washing Machine
        "TileEntityCeramicBlocksOne", # Bathroom Cupboard, Sinks, Toilet
        "TileEntityBath",            # Bath
        "TileEntityLightsOn",        # Lights
        "TileEntityLightsOff",       # Lights
        "TileEntitySofa",            # ArmChair, Sofa parts
        "TileEntityMobHeads",        # Mob Heads
    }
    
    def __init__(self):
        self.mappings_count = len(JAMMY_FURNITURE_MAPPINGS)
        logger.info(f"JammyFurnitureConverter initialized with {self.mappings_count} mappings")
    
    def convert_block(
        self,
        source_block_name: str,
        source_metadata: int,
        tile_entity: Optional[Dict[str, Any]] = None
    ) -> ConversionResult:
        """
        Konwertuje blok Jammy Furniture na 1.18.2.
        
        Args:
            source_block_name: Nazwa bloku 1.7.10 (np. "jammyfurniture:WoodBlocksOne")
            source_metadata: Metadata bloku 1.7.10 (0-15)
            tile_entity: Opcjonalne dane Tile Entity z NBT
        
        Returns:
            ConversionResult z wynikiem konwersji
        """
        # Usuń prefix "minecraft:" jeśli został dodany przez błąd
        if source_block_name.startswith("minecraft:jammyfurniture:"):
            source_block_name = source_block_name.replace("minecraft:", "")
        
        # Znajdź mapowanie
        mapping = get_mapping(source_block_name, source_metadata)
        
        if not mapping:
            logger.warning(f"No mapping found for {source_block_name}:{source_metadata}")
            return ConversionResult(
                success=False,
                error_message=f"No mapping for {source_block_name}:{source_metadata}"
            )
        
        # Przygotuj wynik
        target_id = generate_target_id(mapping)
        target_te = None
        
        # Konwertuj Tile Entity jeśli wymagane
        if mapping.preserve_inventory and tile_entity:
            target_te = self._convert_tile_entity(
                tile_entity, 
                mapping,
                source_block_name,
                source_metadata
            )
        
        logger.debug(f"Converted {source_block_name}:{source_metadata} -> {target_id}")
        
        return ConversionResult(
            success=True,
            target_block_id=f"{mapping.target_mod}:{mapping.target_block}",
            target_block_state=mapping.target_state,
            target_te=target_te
        )
    
    def _convert_tile_entity(
        self,
        te_data: Dict[str, Any],
        mapping: BlockMapping,
        source_block: str,
        source_meta: int
    ) -> Optional[Dict[str, Any]]:
        """
        Konwertuje Tile Entity Jammy Furniture na format 1.18.2.
        
        Args:
            te_data: Dane Tile Entity z 1.7.10
            mapping: Mapowanie bloku
            source_block: Nazwa bloku źródłowego
            source_meta: Metadata bloku źródłowego
        
        Returns:
            Słownik z danymi Tile Entity dla 1.18.2 lub None
        """
        te_id = te_data.get("id", "")
        
        # Konwertuj inventory w zależności od typu bloku
        if "WoodBlocksTwo" in source_block and source_meta <= 7:
            # Kitchen Cupboard
            return self._convert_kitchen_cupboard_inventory(te_data)
        elif "WoodBlocksFour" in source_block and source_meta <= 7:
            # Wardrobe
            return self._convert_wardrobe_inventory(te_data)
        elif "IronBlocksOne" in source_block and source_meta <= 11:
            # Fridge, Freezer
            return self._convert_fridge_inventory(te_data)
        elif "IronBlocksOne" in source_block and source_meta == 12:
            # Rubbish Bin
            return self._convert_bin_inventory(te_data)
        elif "CeramicBlocksOne" in source_block and source_meta <= 3:
            # Bathroom Cupboard
            return self._convert_bathroom_cupboard_inventory(te_data)
        elif "IronBlocksTwo" in source_block:
            # Dishwasher, Washing Machine
            return self._convert_appliance_inventory(te_data)
        elif source_block == "jammyfurniture:WoodBlocksOne" and source_meta == 13:
            # Crafting Side - zachowaj grid craftingowy
            return self._convert_crafting_inventory(te_data)
        elif source_block == "jammyfurniture:WoodBlocksTwo" and source_meta >= 12:
            # Basket
            return self._convert_basket_inventory(te_data)
        
        # Domyślnie - zwróć podstawowe dane bez inventory
        return None
    
    def _convert_kitchen_cupboard_inventory(
        self, 
        te_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Konwertuje inventory szafki kuchennej.
        
        Jammy 1.7.10: Sloty 0-8 (9 slotów)
        Macaw's 1.18.2: Sloty 0-8 (9 slotów) - bezpośrednie mapowanie
        """
        items = te_data.get("Items", [])
        
        converted_items = []
        for item in items:
            converted_item = self._convert_item_stack(item)
            if converted_item:
                converted_items.append(converted_item)
        
        return {
            "id": "mcwfurnitures:kitchen_cabinet",
            "Items": converted_items
        }
    
    def _convert_wardrobe_inventory(
        self, 
        te_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Konwertuje inventory szafy.
        
        Jammy 1.7.10: Sloty 0-26 (27 slotów - double chest)
        Macaw's 1.18.2: Sloty 0-26 (27 slotów) - bezpośrednie mapowanie
        """
        items = te_data.get("Items", [])
        
        converted_items = []
        for item in items:
            converted_item = self._convert_item_stack(item)
            if converted_item:
                converted_items.append(converted_item)
        
        return {
            "id": "mcwfurnitures:wardrobe",
            "Items": converted_items
        }
    
    def _convert_fridge_inventory(
        self, 
        te_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Konwertuje inventory lodówki/zamrażarki.
        
        Jammy 1.7.10: Sloty 0-8 (9 slotów)
        Macaw's 1.18.2: Sloty 0-8 (9 slotów) - bezpośrednie mapowanie
        """
        items = te_data.get("Items", [])
        
        converted_items = []
        for item in items:
            converted_item = self._convert_item_stack(item)
            if converted_item:
                converted_items.append(converted_item)
        
        return {
            "id": "mcwfurnitures:refrigerator",
            "Items": converted_items
        }
    
    def _convert_bin_inventory(
        self, 
        te_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Konwertuje inventory kosza na śmieci.
        
        Jammy 1.7.10: Sloty 0-8 (9 slotów)
        Macaw's 1.18.2: Trash Can - zazwyczaj 1 slot lub żaden
        """
        items = te_data.get("Items", [])
        
        # Trash can w Macaw's ma ograniczoną pojemność lub usuwa itemy
        # Zachowaj tylko pierwszy slot lub zignoruj
        converted_items = []
        if items:
            converted_item = self._convert_item_stack(items[0])
            if converted_item:
                converted_items.append(converted_item)
        
        return {
            "id": "mcwfurnitures:trash_can",
            "Items": converted_items
        }
    
    def _convert_bathroom_cupboard_inventory(
        self, 
        te_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Konwertuje inventory szafki łazienkowej.
        """
        items = te_data.get("Items", [])
        
        converted_items = []
        for item in items:
            converted_item = self._convert_item_stack(item)
            if converted_item:
                converted_items.append(converted_item)
        
        return {
            "id": "mcwfurnitures:bathroom_cabinet",
            "Items": converted_items
        }
    
    def _convert_appliance_inventory(
        self, 
        te_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Konwertuje inventory zmywarki/pralki.
        
        UWAGA: Brak bezpośrednich odpowiedników w Macaw's Furniture.
        Inventory zostanie zachowane w placeholderze (szafce).
        """
        items = te_data.get("Items", [])
        
        converted_items = []
        for item in items:
            converted_item = self._convert_item_stack(item)
            if converted_item:
                converted_items.append(converted_item)
        
        return {
            "id": "mcwfurnitures:kitchen_cabinet",  # Placeholder
            "Items": converted_items,
            "_placeholder_note": "Original: Dishwasher/Washing Machine"
        }
    
    def _convert_crafting_inventory(
        self, 
        te_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Konwertuje inventory stołu craftingowego.
        
        Jammy 1.7.10: Crafting grid 3x3 + wynik
        Minecraft 1.18.2: Crafting Table nie przechowuje inventory
        
        Zwróć inventory jako "ghost items" lub zachowaj w osobnym kontenerze.
        """
        items = te_data.get("Items", [])
        
        # Crafting Table w vanilla nie ma TE w 1.18.2
        # Można rozważyć użycie Supplementaries Safe lub innego bloku z inventory
        converted_items = []
        for item in items:
            converted_item = self._convert_item_stack(item)
            if converted_item:
                converted_items.append(converted_item)
        
        # Zapisz inventory w osobnym miejscu lub jako dropped items
        return {
            "id": "minecraft:crafting_table",
            "_saved_inventory": converted_items,
            "_note": "Original crafting grid items saved"
        }
    
    def _convert_basket_inventory(
        self, 
        te_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Konwertuje inventory kosza.
        
        Jammy 1.7.10: Basket
        Handcrafted 1.18.2: Basket
        """
        items = te_data.get("Items", [])
        
        converted_items = []
        for item in items:
            converted_item = self._convert_item_stack(item)
            if converted_item:
                converted_items.append(converted_item)
        
        return {
            "id": "handcrafted:basket",
            "Items": converted_items
        }
    
    def _convert_item_stack(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Konwertuje item stack z 1.7.10 na 1.18.2.
        
        Args:
            item: Słownik z danymi itemu (id, Count, Damage, tag)
        
        Returns:
            Skonwertowany item lub None
        """
        if not item:
            return None
        
        item_id = item.get("id", "")
        count = item.get("Count", 1)
        damage = item.get("Damage", 0)
        tag = item.get("tag", {})
        
        # Konwersja ID itemu (tu trzeba dodać mapowanie ID itemów)
        # Na razie przepisz bez zmian - zakładając że item converter obsłuży
        converted_id = self._convert_item_id(item_id)
        
        result = {
            "id": converted_id,
            "Count": count
        }
        
        # Dodaj Damage jeśli > 0 (dla narzędzi)
        if damage > 0:
            result["Damage"] = damage
        
        # Przepisz tagi NBT (lore, enchanty, nazwy)
        if tag:
            result["tag"] = self._convert_item_tag(tag)
        
        return result
    
    def _convert_item_id(self, item_id: str) -> str:
        """
        Konwertuje ID itemu z 1.7.10 na 1.18.2.
        
        TODO: Rozszerzyć o pełne mapowanie itemów
        """
        # Usuń cyfry na początku (stare numeryczne ID)
        if item_id.isdigit():
            # To jest stare numeryczne ID - wymaga mapowania
            # Na razie zwróć placeholder
            logger.warning(f"Numeric item ID encountered: {item_id}")
            return f"minecraft:stone  # TODO: Map numeric ID {item_id}"
        
        # Usuń prefix "minecraft:" jeśli istnieje dwa razy
        if item_id.count("minecraft:") > 1:
            item_id = item_id.replace("minecraft:", "", 1)
        
        # Mapowanie znanych zmian ID
        id_mappings = {
            # Dodaj mapowania itemów które się zmieniły
        }
        
        return id_mappings.get(item_id, item_id)
    
    def _convert_item_tag(self, tag: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje tagi NBT itemu.
        
        Obsługuje:
        - display (nazwa, lore)
        - ench (enchanty)
        - StoredEnchantments (książki)
        """
        result = {}
        
        # Konwertuj display
        if "display" in tag:
            result["display"] = tag["display"]
        
        # Konwertuj enchanty
        if "ench" in tag:
            result["Enchantments"] = [
                {
                    "id": e.get("id", ""),
                    "lvl": e.get("lvl", 0)
                }
                for e in tag["ench"]
            ]
        
        # Konwertuj stored enchantments (książki)
        if "StoredEnchantments" in tag:
            result["StoredEnchantments"] = tag["StoredEnchantments"]
        
        # Inne tagi przepisz bez zmian
        for key in ["RepairCost", "AttributeModifiers", "CustomPotionEffects"]:
            if key in tag:
                result[key] = tag[key]
        
        return result
    
    def is_jammy_tile_entity(self, te_id: str) -> bool:
        """Sprawdza czy dane TE należy do Jammy Furniture."""
        # Usuń prefix "minecraft:" jeśli istnieje
        te_id = te_id.replace("minecraft:", "")
        return any(te_id.startswith(jammy_te) for jammy_te in self.JAMMY_TILE_ENTITIES)
    
    def get_stats(self) -> Dict[str, int]:
        """Zwraca statystyki konwertera."""
        return {
            "total_mappings": self.mappings_count,
            "blocks_with_inventory": sum(1 for m in JAMMY_FURNITURE_MAPPINGS if m.preserve_inventory),
            "target_mods": len(set(m.target_mod for m in JAMMY_FURNITURE_MAPPINGS))
        }


# Singleton instance
_converter_instance: Optional[JammyFurnitureConverter] = None


def get_converter() -> JammyFurnitureConverter:
    """Zwraca singleton instance konwertera."""
    global _converter_instance
    if _converter_instance is None:
        _converter_instance = JammyFurnitureConverter()
    return _converter_instance


def convert_jammy_block(
    block_name: str,
    metadata: int,
    tile_entity: Optional[Dict[str, Any]] = None
) -> ConversionResult:
    """
    Funkcja pomocnicza do konwersji pojedynczego bloku.
    
    Args:
        block_name: Nazwa bloku 1.7.10
        metadata: Metadata 1.7.10
        tile_entity: Opcjonalne dane TE
    
    Returns:
        ConversionResult
    """
    converter = get_converter()
    return converter.convert_block(block_name, metadata, tile_entity)
