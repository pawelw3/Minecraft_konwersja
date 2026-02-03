"""
Konwerter NBT dla BeeBox (Ul pszczeli)

Mapowanie 1.7.10 -> 1.18.2:
- grcbees:bee_box -> growthcraft:bee_box
- TileEntityBeeBox -> BeeBoxBlockEntity

Zmiany NBT:
- bee_box.bonus_time (int) -> USUNIĘTE
- bee_box.bee_count (int) -> USUNIĘTE (liczone z inventory)
- BeeBox.version (int) -> USUNIĘTE
+ CurrentProcessTicks (int) - nowość w 1.18.2
- items (NBTTagList) -> inventory (CompoundTag)

Zmiany funkcjonalne:
- Konfigurowalny czas procesu (config)
- Szansa na rozmnażanie pszczół (config)
- Szansa na replikację kwiatów (config)
- Obsługa vanillowych plastrów (minecraft:honeycomb)
- Slot 0: pszczoły (musi być w tagu BEE)
- Slot 1-27: plastry (puste/pełne/vanillowe)
"""

from typing import Dict, Any, Optional, List
from .base_converter import BaseGrowthcraftNBTConverter, NBTConversionResult


class BeeBoxNBTConverter(BaseGrowthcraftNBTConverter):
    """
    Konwerter NBT dla ula pszczelego GrowthCraft.
    
    Obsługuje konwersję z TileEntityBeeBox (1.7.10) 
    do BeeBoxBlockEntity (1.18.2).
    
    Ważne: BeeBox ma 28 slotów (slot 0: pszczoły, 1-27: plastry)
    """
    
    # Domyślny czas procesu w tickach
    DEFAULT_PROCESS_TIME = 1200  # 1 minuta
    
    @property
    def converter_name(self) -> str:
        return "BeeBoxNBTConverter"
    
    @property
    def source_te_id(self) -> str:
        return "grcbees:bee_box"
    
    @property
    def target_te_id(self) -> str:
        return "growthcraft:bee_box"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT ula pszczelego z 1.7.10 do 1.18.2.
        
        Args:
            nbt_1710: NBT z wersji 1.7.10
            block_id: ID bloku (opcjonalnie)
            metadata: Metadata bloku (wariant drewna)
            
        Returns:
            NBTConversionResult z przekonwertowanym NBT
        """
        self.reset()
        
        try:
            converted = self._convert_nbt(nbt_1710, metadata)
            return self._create_result(converted, success=True)
            
        except Exception as e:
            self._add_error(f"Błąd konwersji BeeBox: {str(e)}")
            return self._create_result(success=False)
    
    def _convert_nbt(self, nbt_1710: Dict[str, Any], metadata: int = 0) -> Dict[str, Any]:
        """
        Główna logika konwersji NBT.
        """
        converted = {
            "id": self.target_te_id
        }
        
        # === Konwersja danych bee_box ===
        bee_box_data = nbt_1710.get("bee_box", {})
        
        # bonus_time - usunięte w 1.18.2
        bonus_time = bee_box_data.get("bonus_time", 0)
        if bonus_time > 0:
            self._add_warning("bonus_time z 1.7.10 nie jest wspierane w 1.18.2")
        
        # bee_count - usunięte w 1.18.2 (liczone z inventory)
        bee_count = bee_box_data.get("bee_count", 0)
        if bee_count > 0:
            self._add_warning("bee_count z 1.7.10 nie jest wspierane (liczone z inventory w 1.18.2)")
        
        # === CurrentProcessTicks ===
        # W 1.18.2 używane do śledzenia czasu procesu
        # W 1.7.10 nie było bezpośredniego odpowiednika
        # Ustawiamy na 0 (zresetowany timer)
        converted["CurrentProcessTicks"] = 0
        
        # === Konwersja inventory ===
        # 1.7.10: items (28 slotów)
        # 1.18.2: inventory (28 slotów: 0=pszczoły, 1-27=plastry)
        items = nbt_1710.get("items", [])
        converted["inventory"] = self._convert_bee_box_inventory(items)
        
        # === CustomName ===
        custom_name = nbt_1710.get("CustomName")
        if custom_name:
            converted["CustomName"] = custom_name
        
        return converted
    
    def _convert_bee_box_inventory(self, items_list: List[Dict]) -> Dict[str, Any]:
        """
        Konwertuje inventory BeeBox.
        
        Struktura slotów:
        - Slot 0: Pszczoły (ItemBee z tagiem BEE)
        - Slot 1-27: Plastry miodu (puste, pełne, vanillowe)
        
        Mapowanie itemów:
        - grcbees:bee -> growthcraft:bee (z tagiem BEE)
        - grcbees:honey_comb -> growthcraft:honey_comb
        - grcbees:honey_comb_full -> growthcraft:honey_comb_full
        - minecraft:honeycomb -> minecraft:honeycomb (vanilla obsługiwane!)
        """
        items = []
        
        for slot_data in items_list:
            if not slot_data:
                continue
            
            converted = self._convert_item_stack(slot_data)
            if converted:
                slot = slot_data.get('Slot', 0)
                converted['Slot'] = slot
                
                # Specjalna obsługa dla pszczół (slot 0)
                if slot == 0:
                    # Upewnij się że pszczoły mają tag BEE
                    if 'tag' not in converted:
                        converted['tag'] = {}
                    converted['tag']['BEE'] = 1
                
                items.append(converted)
        
        return {
            'Size': 28,
            'Items': items
        }
    
    def _count_bees(self, items_list: List[Dict]) -> int:
        """
        Liczy pszczoły w inventory.
        W 1.7.10 pszczoły są w slocie 0.
        """
        for item in items_list:
            if item.get('Slot', -1) == 0:
                return item.get('Count', 0)
        return 0
    
    def _count_combs(self, items_list: List[Dict]) -> tuple:
        """
        Liczy plastry w inventory.
        Zwraca krotkę (puste, pełne, vanillowe).
        """
        empty = 0
        full = 0
        vanilla = 0
        
        for item in items_list:
            slot = item.get('Slot', -1)
            if slot <= 0:
                continue  # Slot 0 to pszczoły
            
            item_id = item.get('id', '')
            count = item.get('Count', 0)
            
            if 'honey_comb_full' in item_id or 'honeycomb' in item_id:
                full += count
            elif 'honey_comb' in item_id:
                empty += count
        
        return empty, full, vanilla
    
    def convert_back(self, nbt_1182: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje NBT z powrotem z 1.18.2 do 1.7.10.
        """
        converted = {
            "id": self.source_te_id
        }
        
        # bee_box dane
        bee_count = 0
        bonus_time = 0  # Nie ma w 1.18.2
        
        # inventory
        inventory = nbt_1182.get("inventory", {})
        items_1182 = inventory.get("Items", [])
        
        # Policz pszczoły z inventory
        for item in items_1182:
            if item.get('Slot', -1) == 0:
                bee_count = item.get('Count', 0)
                break
        
        converted["bee_box"] = {
            "bee_count": bee_count,
            "bonus_time": bonus_time,
            "version": 3  # Wersja danych z 1.7.10
        }
        
        # Items
        items = []
        for item in items_1182:
            # Konwertuj z powrotem ID
            item_id = item.get('id', '')
            
            # Odwrotne mapowanie
            reverse_mappings = {
                'growthcraft:bee': 'grcbees:bee',
                'growthcraft:honey_comb': 'grcbees:honey_comb',
                'growthcraft:honey_comb_full': 'grcbees:honey_comb_full',
            }
            
            for new_id, old_id in reverse_mappings.items():
                if item_id == new_id:
                    item['id'] = old_id
                    break
            
            items.append(item)
        
        if items:
            converted["items"] = items
        
        # CustomName
        custom_name = nbt_1182.get("CustomName")
        if custom_name:
            converted["CustomName"] = custom_name
        
        return converted
