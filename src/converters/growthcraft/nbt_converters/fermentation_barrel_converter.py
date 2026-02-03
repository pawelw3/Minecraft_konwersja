"""
Konwerter NBT dla FermentationBarrel (Beczka fermentacyjna)

Mapowanie 1.7.10 -> 1.18.2:
- grccellar:ferment_barrel -> growthcraft:fermentation_barrel
- TileEntityFermentBarrel -> FermentationBarrelBlockEntity

Zmiany NBT:
- time (int) -> CurrentProcessTicks (int)
- Tank (NBTTagCompound) -> fluid_tank_input_0 (CompoundTag)
- lid_on (boolean) -> USUNIĘTE (brak pokrywki w 1.18.2)
- items (NBTTagList) -> inventory (CompoundTag)
+ MaxProcessTicks (int) - nowość w 1.18.2

Zmiany funkcjonalne:
- Pojemność: 3000 mB -> 4000 mB
- System mnożnika wyjściowego zależny od ilości płynu
"""

from typing import Dict, Any, Optional, List
from .base_converter import BaseGrowthcraftNBTConverter, NBTConversionResult


class FermentationBarrelNBTConverter(BaseGrowthcraftNBTConverter):
    """
    Konwerter NBT dla beczki fermentacyjnej GrowthCraft.
    
    Obsługuje konwersję z TileEntityFermentBarrel (1.7.10) 
    do FermentationBarrelBlockEntity (1.18.2).
    """
    
    # Domyślny czas fermentacji w tickach (2 minuty = 2400 ticków)
    DEFAULT_PROCESSING_TIME = 2400
    
    @property
    def converter_name(self) -> str:
        return "FermentationBarrelNBTConverter"
    
    @property
    def source_te_id(self) -> str:
        return "grccellar:ferment_barrel"
    
    @property
    def target_te_id(self) -> str:
        return "growthcraft:fermentation_barrel"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT beczki fermentacyjnej z 1.7.10 do 1.18.2.
        
        Args:
            nbt_1710: NBT z wersji 1.7.10
            block_id: ID bloku (opcjonalnie)
            metadata: Metadata bloku
            
        Returns:
            NBTConversionResult z przekonwertowanym NBT
        """
        self.reset()
        
        try:
            converted = self._convert_nbt(nbt_1710)
            return self._create_result(converted, success=True)
            
        except Exception as e:
            self._add_error(f"Błąd konwersji FermentationBarrel: {str(e)}")
            return self._create_result(success=False)
    
    def _convert_nbt(self, nbt_1710: Dict[str, Any]) -> Dict[str, Any]:
        """
        Główna logika konwersji NBT.
        """
        converted = {
            "id": self.target_te_id
        }
        
        # === Konwersja czasu procesu ===
        # 1.7.10: time (int) - aktualny czas
        # 1.18.2: CurrentProcessTicks (int)
        current_time = nbt_1710.get("time", 0)
        converted["CurrentProcessTicks"] = current_time
        
        # Oblicz MaxProcessTicks na podstawie ilości płynu
        # W 1.18.2 mnożnik zależy od ilości płynu
        max_time = self._calculate_max_process_ticks(nbt_1710)
        converted["MaxProcessTicks"] = max_time
        
        # === Konwersja zbiornika płynu ===
        # 1.7.10: Tank (NBTTagCompound)
        # 1.18.2: fluid_tank_input_0 (CompoundTag)
        tank_data = nbt_1710.get("Tank")
        if tank_data:
            converted["fluid_tank_input_0"] = self._convert_fluid_stack(tank_data)
        
        # === Konwersja inventory ===
        # 1.7.10: items (NBTTagList) - slot 0: katalizator
        # 1.18.2: inventory (CompoundTag)
        items = nbt_1710.get("items", [])
        if items:
            converted["inventory"] = self._convert_inventory(items)
        else:
            # Pusty inventory dla kompatybilności
            converted["inventory"] = {"Size": 1, "Items": []}
        
        # === Uwaga o pokrywce ===
        # lid_on w 1.7.10 jest ignorowane - w 1.18.2 nie ma pokrywki
        if nbt_1710.get("lid_on"):
            self._add_warning("Pokrywka (lid_on) z 1.7.10 nie jest wspierana w 1.18.2")
        
        return converted
    
    def _calculate_max_process_ticks(self, nbt_1710: Dict[str, Any]) -> int:
        """
        Oblicza MaxProcessTicks na podstawie danych z 1.7.10.
        
        W 1.18.2 czas procesu zależy od ilości płynu (mnożnik).
        Domyślnie: co 1000 mB = 2400 ticków (2 minuty)
        """
        tank_data = nbt_1710.get("Tank", {})
        fluid_amount = tank_data.get("Amount", 0)
        
        if fluid_amount <= 0:
            return self.DEFAULT_PROCESSING_TIME
        
        # Mnożnik: co 1000 mB = 1x czas
        multiplier = max(1, fluid_amount // 1000)
        return self.DEFAULT_PROCESSING_TIME * multiplier
    
    def _convert_inventory(self, items_list: List[Dict]) -> Dict[str, Any]:
        """
        Konwertuje inventory dla FermentationBarrel.
        
        1.7.10: items[0] = katalizator (np. drożdże)
        1.18.2: inventory.Items[0] = katalizator
        """
        items = []
        for slot_data in items_list:
            if not slot_data:
                continue
            
            converted = self._convert_item_stack(slot_data)
            if converted:
                # Zachowaj oryginalny slot
                slot = slot_data.get('Slot', 0)
                converted['Slot'] = slot
                items.append(converted)
        
        return {
            'Size': max(1, len(items)),
            'Items': items
        }
    
    def convert_back(self, nbt_1182: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje NBT z powrotem z 1.18.2 do 1.7.10.
        
        Używane do testów i weryfikacji.
        """
        converted = {
            "id": self.source_te_id
        }
        
        # CurrentProcessTicks -> time
        converted["time"] = nbt_1182.get("CurrentProcessTicks", 0)
        
        # fluid_tank_input_0 -> Tank
        fluid_tank = nbt_1182.get("fluid_tank_input_0")
        if fluid_tank:
            converted["Tank"] = fluid_tank
        
        # inventory -> items
        inventory = nbt_1182.get("inventory", {})
        items = inventory.get("Items", [])
        if items:
            converted["items"] = items
        
        # lid_on domyślnie false (nie ma w 1.18.2)
        converted["lid_on"] = False
        
        return converted
