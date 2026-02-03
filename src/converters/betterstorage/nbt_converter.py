"""
Główny konwerter NBT dla modu Better Storage 1.7.10 → 1.18.2

Obsługuje konwersję wszystkich Tile Entities z Better Storage:
- TileEntityCrate (z Crate Pile)
- TileEntityReinforcedChest
- TileEntityLocker / TileEntityReinforcedLocker
- TileEntityCardboardBox
- TileEntityCraftingStation
- TileEntityArmorStand
- TileEntityBackpack
- TileEntityEnderBackpack
- TileEntityPresent
- TileEntityLockableDoor
- TileEntityFlintBlock
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .mapping import (
    BLOCK_MAPPING, ITEM_MAPPING, 
    convert_orientation, convert_color_to_dye_color,
    get_iron_chest_type_for_capacity, get_material_info,
    get_reinforced_chest_capacity, get_container_slots
)
from .crate_pile_simulation import CratePileLoader, CratePileConverter


class BetterStorageConverter:
    """
    Konwerter Tile Entities z Better Storage 1.7.10 na 1.18.2
    
    Usage:
        converter = BetterStorageConverter(world_path='mapa_1710')
        result = converter.convert_tile_entity('betterstorage:reinforcedChest', nbt_data)
    """
    
    def __init__(self, world_path: Optional[str] = None):
        """
        Args:
            world_path: Ścieżka do świata 1.7.10 (wymagana dla Crate Pile)
        """
        self.world_path = world_path
        self.crate_loader: Optional[CratePileLoader] = None
        self.crate_converter: Optional[CratePileConverter] = None
        
        if world_path:
            self.crate_loader = CratePileLoader(world_path)
            self.crate_converter = CratePileConverter(self.crate_loader)
    
    def convert_tile_entity(
        self, 
        block_id: str, 
        nbt_data: Dict[str, Any],
        x: int = 0, 
        y: int = 0, 
        z: int = 0
    ) -> Dict[str, Any]:
        """
        Konwertuje TileEntity Better Storage na BlockEntity 1.18.2
        
        Args:
            block_id: ID bloku (np. 'betterstorage:reinforcedChest')
            nbt_data: Dane NBT TileEntity
            x, y, z: Współrzędne bloku (wymagane dla Crate)
            
        Returns:
            {
                'block_id': str,  # Nowe ID bloku
                'nbt': Dict,      # Nowe dane NBT
                'warnings': List[str],  # Ostrzeżenia
                'overflow': List[Dict], # Itemy które się nie zmieściły
            }
        """
        warnings = []
        
        # Mapowanie na target block
        if block_id not in BLOCK_MAPPING:
            warnings.append(f"Nieznany blok: {block_id}")
            return {
                'block_id': 'minecraft:chest',
                'nbt': self._convert_generic_items(nbt_data),
                'warnings': warnings,
                'overflow': []
            }
        
        target_block, params = BLOCK_MAPPING[block_id]
        
        # Wybieramy odpowiedni konwerter na podstawie typu
        if 'crate' in block_id.lower():
            return self._convert_crate(nbt_data, x, y, z, warnings)
        
        elif 'reinforcedChest' in block_id:
            return self._convert_reinforced_chest(nbt_data, warnings)
        
        elif 'reinforcedLocker' in block_id:
            return self._convert_reinforced_locker(nbt_data, warnings)
        
        elif 'locker' in block_id.lower():
            return self._convert_locker(nbt_data, warnings)
        
        elif 'cardboardBox' in block_id:
            return self._convert_cardboard_box(nbt_data, warnings)
        
        elif 'craftingStation' in block_id:
            return self._convert_crafting_station(nbt_data, warnings)
        
        elif 'armorStand' in block_id:
            return self._convert_armor_stand(nbt_data, warnings)
        
        elif 'enderBackpack' in block_id:
            return self._convert_ender_backpack(nbt_data, warnings)
        
        elif 'present' in block_id.lower():
            return self._convert_present(nbt_data, warnings)
        
        elif 'flintBlock' in block_id:
            return self._convert_flint_block(nbt_data, warnings)
        
        else:
            # Generic conversion
            return {
                'block_id': target_block,
                'nbt': self._convert_generic_items(nbt_data),
                'warnings': warnings + [f"Generyczna konwersja dla {block_id}"],
                'overflow': []
            }
    
    def _convert_crate(
        self, 
        nbt: Dict, 
        x: int, 
        y: int, 
        z: int, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """
        Konwertuje Crate z Crate Pile.
        
        UWAGA: Zawartość jest w osobnym pliku data/crates/<id>.dat
        """
        warnings.append("Crate używa Crate Pile - zawartość z osobnego pliku")
        
        crate_id = nbt.get('crateId', -1)
        
        if crate_id < 0:
            warnings.append("Crate bez crateId - zwracam pustą skrzynię")
            return {
                'block_id': 'minecraft:chest',
                'nbt': {'Items': []},
                'warnings': warnings,
                'overflow': []
            }
        
        if self.crate_converter:
            # Używamy CratePileConverter
            result = self.crate_converter.convert_crate(x, y, z)
            result['warnings'] = warnings + result.get('warnings', [])
            return result
        else:
            # Brak loadera - nie możemy odczytać danych
            warnings.append("Brak CratePileLoader - nie można odczytać zawartości crate pile")
            return {
                'block_id': 'minecraft:chest',
                'nbt': {'Items': []},
                'warnings': warnings,
                'overflow': []
            }
    
    def _convert_reinforced_chest(
        self, 
        nbt: Dict, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """
        Konwertuje Reinforced Chest na Iron Chests.
        
        UWAGA: Materiał jest TYLKO kosmetyczny!
        Pojemność zależy od configu (27/33/39), NIE od materiału.
        """
        # Pobieramy materiał (informacyjnie)
        material = nbt.get('Material', 'iron')
        mat_info = get_material_info(material)
        
        if mat_info.get('warning'):
            warnings.append(f"Materiał {material}: {mat_info['warning']}")
        
        # Domyślnie zakładamy config z 13 kolumnami = 39 slotów
        # W prawdziwej konwersji trzeba sprawdzić config serwera
        bs_capacity = 39  # TODO: Odczytać z configu
        
        # Wybieramy odpowiedni Iron Chest
        target_block = get_iron_chest_type_for_capacity(bs_capacity)
        
        # Konwertujemy itemy
        items = nbt.get('Items', [])
        converted_items = self._convert_item_list(items)
        
        # Sprawdzamy overflow
        max_slots = get_container_slots(target_block)
        fitting_items = converted_items[:max_slots]
        overflow = converted_items[max_slots:]
        
        if overflow:
            warnings.append(f"{len(overflow)} itemów nie zmieściło się w skrzyni")
        
        # Budujemy NBT
        new_nbt = {'Items': fitting_items}
        
        # Zachowujemy nazwę custom + dodajemy info o materiale
        custom_name = nbt.get('CustomName')
        if custom_name:
            new_nbt['CustomName'] = f"{custom_name} ({material})"
        elif material != 'iron':
            new_nbt['CustomName'] = f"Reinforced Chest ({material})"
        
        # Konwertujemy orientację
        orientation = nbt.get('orientation')
        if orientation is not None:
            new_nbt['facing'] = convert_orientation(orientation)
        
        return {
            'block_id': target_block,
            'nbt': new_nbt,
            'warnings': warnings,
            'overflow': overflow
        }
    
    def _convert_reinforced_locker(
        self, 
        nbt: Dict, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """Konwertuje Reinforced Locker na Iron Chests lub Barrel"""
        material = nbt.get('Material', 'iron')
        
        # Reinforced Locker ma stałe 36 slotów
        # Iron Chest ma 54, więc się zmieści
        target_block = 'ironchest:iron_chest'
        
        items = nbt.get('Items', [])
        converted_items = self._convert_item_list(items)
        
        new_nbt = {'Items': converted_items}
        
        custom_name = nbt.get('CustomName')
        if custom_name:
            new_nbt['CustomName'] = f"{custom_name} ({material})"
        
        orientation = nbt.get('orientation')
        if orientation is not None:
            new_nbt['facing'] = convert_orientation(orientation)
        
        # Ignorujemy mirror - nie ma odpowiednika
        if nbt.get('mirror'):
            warnings.append("Locker 'mirror' nie ma odpowiednika w 1.18.2")
        
        return {
            'block_id': target_block,
            'nbt': new_nbt,
            'warnings': warnings,
            'overflow': []
        }
    
    def _convert_locker(
        self, 
        nbt: Dict, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """
        Konwertuje Locker na Barrel lub Chest.
        
        Barrel jest pionowy jak Locker, więc pasuje lepiej wizualnie.
        """
        # Locker ma 36 slotów, Barrel ma 27
        # Używamy Iron Chest (54) jeśli pełny
        items = nbt.get('Items', [])
        converted_items = self._convert_item_list(items)
        
        if len(converted_items) > 27:
            target_block = 'ironchest:iron_chest'
            warnings.append("Locker ma >27 itemów - użyto Iron Chest zamiast Barrel")
        else:
            target_block = 'minecraft:barrel'
        
        new_nbt = {'Items': converted_items[:get_container_slots(target_block)]}
        
        if nbt.get('CustomName'):
            new_nbt['CustomName'] = nbt['CustomName']
        
        orientation = nbt.get('orientation')
        if orientation is not None:
            new_nbt['facing'] = convert_orientation(orientation)
        
        if nbt.get('mirror'):
            warnings.append("Locker 'mirror' nie ma odpowiednika w 1.18.2")
        
        return {
            'block_id': target_block,
            'nbt': new_nbt,
            'warnings': warnings,
            'overflow': converted_items[get_container_slots(target_block):]
        }
    
    def _convert_cardboard_box(
        self, 
        nbt: Dict, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """
        Konwertuje Cardboard Box na Packing Tape lub Chest.
        
        UWAGA: Inny system zużywania (taśma vs blok)
        """
        uses = nbt.get('uses', -1)
        items = nbt.get('Items', [])
        
        if uses == 0:
            # Zużyty - wypakowujemy zawartość
            warnings.append("Cardboard Box zużyty (uses=0) - wypakowano zawartość")
            return {
                'block_id': 'minecraft:chest',
                'nbt': {'Items': self._convert_item_list(items)},
                'warnings': warnings,
                'overflow': []
            }
        
        # Konwertujemy na Packed block (Packing Tape)
        # Packing Tape zużywa taśmę, nie blok
        converted_items = self._convert_item_list(items)
        
        new_nbt = {
            'Items': converted_items,
            # Packing Tape ma inne tagi - tu tylko placeholder
            'packed': True,
        }
        
        # Kolor
        color = nbt.get('color', -1)
        if color >= 0:
            dye_color = convert_color_to_dye_color(color)
            if dye_color:
                new_nbt['color'] = dye_color
        
        warnings.append("Cardboard Box → Packing Tape: zużywanie się zmienia (taśma vs blok)")
        
        return {
            'block_id': 'packingtape:packed',
            'nbt': new_nbt,
            'warnings': warnings,
            'overflow': []
        }
    
    def _convert_crafting_station(
        self, 
        nbt: Dict, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """
        Konwertuje Crafting Station.
        
        To ten sam mod, więc NBT powinno być kompatybilne,
        ale trzeba zweryfikować.
        """
        items = nbt.get('Items', [])
        
        # 10 slotów: 0-8 crafting, 9 wynik
        if len(items) > 10:
            warnings.append(f"Crafting Station ma {len(items)} itemów - oczekiwano max 10")
        
        converted_items = self._convert_item_list(items)
        
        new_nbt = {'Items': converted_items}
        
        warnings.append("Crafting Station: NBT do weryfikacji kompatybilności")
        
        return {
            'block_id': 'craftingstation:crafting_station',
            'nbt': new_nbt,
            'warnings': warnings,
            'overflow': []
        }
    
    def _convert_armor_stand(
        self, 
        nbt: Dict, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """
        Konwertuje Armor Stand na Vanilla Armor Stand.
        
        UWAGA: BS ma GUI z 4 slotami, vanilla nie ma GUI!
        Itemy muszą być wypakowane.
        """
        items = nbt.get('Items', [])
        converted_items = self._convert_item_list(items)
        
        # Vanilla Armor Stand przechowuje zbroję w inny sposób
        # (nie w Inventory, ale w polach ArmorItems)
        #
        # Dla uproszczenia zwracamy itemy jako overflow
        # W prawdziwej konwersji trzeba by stworzyć skrzynię obok
        
        warnings.append(
            "Armor Stand: BS ma GUI, vanilla nie ma! "
            "Zawartość wypakowana do overflow (do umieszczenia w skrzyni obok)"
        )
        
        # Vanilla Armor Stand - pusty lub z ekspozycją
        return {
            'block_id': 'minecraft:armor_stand',
            'nbt': {},  # Vanilla armor stand nie ma Items
            'warnings': warnings,
            'overflow': converted_items  # Te itemy trzeba umieścić gdzie indziej
        }
    
    def _convert_ender_backpack(
        self, 
        nbt: Dict, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """
        Konwertuje Ender Backpack na Vanilla Ender Chest.
        
        UWAGA: Ender Backpack używa vanilla ender chest inventory!
        Nie ma tu własnych danych do konwersji.
        """
        warnings.append(
            "Ender Backpack używa vanilla ender chest - "
            "gracz zachowuje dostęp do tego samego inventory"
        )
        
        return {
            'block_id': 'minecraft:ender_chest',
            'nbt': {},  # Ender chest nie przechowuje danych w BE
            'warnings': warnings,
            'overflow': []
        }
    
    def _convert_present(
        self, 
        nbt: Dict, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """Konwertuje Present na Vanilla Chest"""
        items = nbt.get('Items', [])
        converted_items = self._convert_item_list(items)
        
        new_nbt = {'Items': converted_items}
        
        # Kolor (ozdobny)
        color = nbt.get('color', -1)
        if color >= 0:
            dye_color = convert_color_to_dye_color(color)
            custom_name = f"Present ({dye_color or 'unknown'})"
            new_nbt['CustomName'] = custom_name
        
        warnings.append("Present: funkcja ozdobna tracona - użyto zwykłej skrzyni")
        
        return {
            'block_id': 'minecraft:chest',
            'nbt': new_nbt,
            'warnings': warnings,
            'overflow': []
        }
    
    def _convert_flint_block(
        self, 
        nbt: Dict, 
        warnings: List[str]
    ) -> Dict[str, Any]:
        """Konwertuje Flint Block na Stone"""
        return {
            'block_id': 'minecraft:stone',
            'nbt': {},
            'warnings': warnings + ["Flint Block → Stone (placeholder)"],
            'overflow': []
        }
    
    def _convert_generic_items(self, nbt: Dict) -> Dict[str, Any]:
        """Generyczna konwersja itemów z NBT"""
        new_nbt = {}
        
        if 'Items' in nbt:
            new_nbt['Items'] = self._convert_item_list(nbt['Items'])
        
        if 'CustomName' in nbt:
            new_nbt['CustomName'] = nbt['CustomName']
        
        return new_nbt
    
    def _convert_item_list(self, items: List[Dict]) -> List[Dict]:
        """Konwertuje listę ItemStacków"""
        return [self._convert_item(item) for item in items]
    
    def _convert_item(self, item: Dict) -> Dict:
        """
        Konwertuje ItemStack 1.7.10 → 1.18.2
        
        Zmiany:
        - Damage (short) → przeniesione do tag.Damage
        - ID może wymagać mapowania
        """
        converted = {
            'id': self._convert_item_id(item.get('id', 'minecraft:air')),
            'Count': item.get('Count', 1),
            'Slot': item.get('Slot', 0)
        }
        
        # Konwertujemy tagi
        if 'tag' in item:
            converted['tag'] = self._convert_item_tags(item['tag'])
        
        # Damage w 1.7.10 jest osobnym polem, w 1.18.2 w tagu
        damage = item.get('Damage', 0)
        if damage != 0:
            if 'tag' not in converted:
                converted['tag'] = {}
            converted['tag']['Damage'] = damage
        
        return converted
    
    def _convert_item_id(self, item_id: str) -> str:
        """Konwertuje ID itemu jeśli wymaga mapowania"""
        if item_id in ITEM_MAPPING:
            mapped, params = ITEM_MAPPING[item_id]
            if mapped and not params.get('skip'):
                return mapped
        
        # Domyślnie zwracamy oryginalne ID
        # (zakładając że inne konwertery zajmą się resztą)
        return item_id
    
    def _convert_item_tags(self, tags: Dict) -> Dict:
        """Konwertuje tagi itemu"""
        new_tags = {}
        
        for key, value in tags.items():
            # Enchanty BS (170-176) nie mają odpowiedników - pomijamy
            if key == 'ench':
                new_enchants = []
                for enchant in value:
                    id_ = enchant.get('id', 0)
                    if 170 <= id_ <= 176:
                        # Enchant BS - pomijamy
                        continue
                    new_enchants.append(enchant)
                if new_enchants:
                    new_tags['Enchantments'] = new_enchants
            else:
                new_tags[key] = value
        
        return new_tags


# Helper functions dla szybkiej konwersji
def convert_single_block(
    block_id: str,
    nbt_data: Dict[str, Any],
    world_path: Optional[str] = None,
    x: int = 0,
    y: int = 0,
    z: int = 0
) -> Dict[str, Any]:
    """
    Szybka konwersja pojedynczego bloku.
    
    Usage:
        result = convert_single_block('betterstorage:crate', nbt, 'mapa_1710', x, y, z)
        new_block_id = result['block_id']
        new_nbt = result['nbt']
    """
    converter = BetterStorageConverter(world_path)
    return converter.convert_tile_entity(block_id, nbt_data, x, y, z)
