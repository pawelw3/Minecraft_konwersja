"""
Konwerter NBT dla BrewKettle (Kocioł warzelny)

Mapowanie 1.7.10 -> 1.18.2:
- grccellar:brew_kettle -> growthcraft:brew_kettle
- TileEntityBrewKettle -> BrewKettleBlockEntity

Zmiany NBT:
- brew_kettle.time (float) -> CurrentProcessTicks (int)
- brew_kettle.time_max (float) -> MaxProcessTicks (int)
- brew_kettle.heat_multiplier (float) -> USUNIĘTE (sprawdzane dynamicznie)
- TankInput (NBTTagCompound) -> fluid_tank_input_0 (CompoundTag)
- TankOutput (NBTTagCompound) -> fluid_tank_output_0 (CompoundTag)
- items[0] (input) -> inventory.Items[1] (slot 1)
- items[1] (byproduct) -> inventory.Items[2] (slot 2)
+ inventory.Items[0] - NOWOŚĆ: slot na pokrywkę (lid)

Zmiany funkcjonalne:
- NOWOŚĆ: Slot na pokrywkę (BrewKettleLid) - wymagany dla niektórych receptur
- System byproduct z szansą (0-100%)
- Automatyczne wykrywanie ciepła (BlockStateUtils.isHeated)
"""

from typing import Dict, Any, Optional, List
from .base_converter import BaseGrowthcraftNBTConverter, NBTConversionResult


class BrewKettleNBTConverter(BaseGrowthcraftNBTConverter):
    """
    Konwerter NBT dla kocioła warzelnego GrowthCraft.
    
    Obsługuje konwersję z TileEntityBrewKettle (1.7.10) 
    do BrewKettleBlockEntity (1.18.2).
    """
    
    # Domyślny czas warzenia w tickach (1 minuta = 1200 ticków)
    DEFAULT_PROCESSING_TIME = 1200
    
    @property
    def converter_name(self) -> str:
        return "BrewKettleNBTConverter"
    
    @property
    def source_te_id(self) -> str:
        return "grccellar:brew_kettle"
    
    @property
    def target_te_id(self) -> str:
        return "growthcraft_cellar:brew_kettle"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT kocioła warzelnego z 1.7.10 do 1.18.2.
        
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
            self._add_error(f"Błąd konwersji BrewKettle: {str(e)}")
            return self._create_result(success=False)
    
    def _convert_nbt(self, nbt_1710: Dict[str, Any]) -> Dict[str, Any]:
        """
        Główna logika konwersji NBT.
        """
        converted = {
            "id": self.target_te_id
        }
        
        # === Konwersja danych brew_kettle ===
        brew_kettle_data = nbt_1710.get("brew_kettle", {})
        
        # time (float) -> CurrentProcessTicks (int)
        current_time = int(brew_kettle_data.get("time", 0))
        converted["CurrentProcessTicks"] = current_time
        
        # time_max (float) -> MaxProcessTicks (int)
        max_time = int(brew_kettle_data.get("time_max", self.DEFAULT_PROCESSING_TIME))
        converted["MaxProcessTicks"] = max_time
        
        # heat_multiplier - usunięte w 1.18.2 (sprawdzane dynamicznie)
        heat_multiplier = brew_kettle_data.get("heat_multiplier", 0.0)
        if heat_multiplier > 0:
            self._add_warning("heat_multiplier nie jest używane w 1.18.2 (sprawdzane dynamicznie)")
        
        # grain (float) - starsze wersje, ignorowane w 1.18.2
        if "grain" in brew_kettle_data:
            self._add_warning("Pole 'grain' z 1.7.10 nie jest wspierane w 1.18.2")
        
        # === Konwersja zbiorników płynu ===
        # TankInput -> fluid_tank_input_0
        tank_input = nbt_1710.get("TankInput")
        if tank_input:
            converted["fluid_tank_input_0"] = self._convert_fluid_stack(tank_input)
        
        # TankOutput -> fluid_tank_output_0
        tank_output = nbt_1710.get("TankOutput")
        if tank_output:
            converted["fluid_tank_output_0"] = self._convert_fluid_stack(tank_output)
        
        # === Konwersja inventory ===
        # 1.7.10: items[0] = input, items[1] = byproduct
        # 1.18.2: slot 0 = lid, slot 1 = input, slot 2 = byproduct
        items = nbt_1710.get("items", [])
        converted["inventory"] = self._convert_inventory_with_lid(items)
        
        # === CustomName ===
        custom_name = nbt_1710.get("CustomName")
        if custom_name:
            converted["CustomName"] = custom_name
        
        return converted
    
    def _convert_inventory_with_lid(self, items_list: List[Dict]) -> Dict[str, Any]:
        """
        Konwertuje inventory z mapowaniem slotów.
        
        Mapowanie slotów:
        1.7.10 -> 1.18.2:
        - items[0] (input) -> Items[1] (slot 1)
        - items[1] (byproduct) -> Items[2] (slot 2)
        - NOWOŚĆ: slot 0 na pokrywkę (pusty przy konwersji)
        """
        # Mapowanie slotów: stary -> nowy
        slot_mapping = {
            0: 1,  # input -> slot 1
            1: 2   # byproduct -> slot 2
        }
        
        items = []
        
        # Slot 0 na pokrywkę - zostawiamy pusty
        # (gracz musi dodać pokrywkę ręcznie jeśli receptura wymaga)
        
        for slot_data in items_list:
            if not slot_data:
                continue
            
            converted = self._convert_item_stack(slot_data)
            if converted:
                old_slot = slot_data.get('Slot', 0)
                new_slot = slot_mapping.get(old_slot, old_slot + 1)
                converted['Slot'] = new_slot
                items.append(converted)
        
        return {
            'Size': 3,  # 3 sloty: lid (0), input (1), byproduct (2)
            'Items': items
        }
    
    def _detect_lid_requirement(self, nbt_1710: Dict[str, Any]) -> bool:
        """
        Sprawdza czy receptura wymaga pokrywki.
        
        W 1.7.10 nie było slotu na pokrywkę, więc nie możemy tego wykryć
        bezpośrednio. Możemy spróbować wykryć na podstawie typu płynu.
        
        Returns:
            True jeśli receptura prawdopodobnie wymaga pokrywki
        """
        tank_input = nbt_1710.get("TankInput", {})
        fluid_name = tank_input.get("FluidName", "")
        
        # Receptury wymagające pokrywki (przykładowe)
        lid_required_fluids = [
            "grccellar:wort",
            "grccellar:young_wort",
        ]
        
        return any(req in fluid_name for req in lid_required_fluids)
    
    def convert_back(self, nbt_1182: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje NBT z powrotem z 1.18.2 do 1.7.10.
        """
        converted = {
            "id": self.source_te_id
        }
        
        # CurrentProcessTicks -> brew_kettle.time
        current_ticks = nbt_1182.get("CurrentProcessTicks", 0)
        max_ticks = nbt_1182.get("MaxProcessTicks", self.DEFAULT_PROCESSING_TIME)
        
        converted["brew_kettle"] = {
            "time": float(current_ticks),
            "time_max": float(max_ticks),
            "heat_multiplier": 1.0  # Domyślna wartość
        }
        
        # fluid_tank_input_0 -> TankInput
        fluid_input = nbt_1182.get("fluid_tank_input_0")
        if fluid_input:
            converted["TankInput"] = fluid_input
        
        # fluid_tank_output_0 -> TankOutput
        fluid_output = nbt_1182.get("fluid_tank_output_0")
        if fluid_output:
            converted["TankOutput"] = fluid_output
        
        # inventory -> items (odwrotne mapowanie slotów)
        inventory = nbt_1182.get("inventory", {})
        items_1182 = inventory.get("Items", [])
        
        items = []
        for item in items_1182:
            slot = item.get('Slot', 0)
            # Odwrotne mapowanie: 1 -> 0, 2 -> 1
            if slot == 1:
                item['Slot'] = 0
                items.append(item)
            elif slot == 2:
                item['Slot'] = 1
                items.append(item)
            # Slot 0 (pokrywka) jest pomijany w 1.7.10
        
        if items:
            converted["items"] = items
        
        # CustomName
        custom_name = nbt_1182.get("CustomName")
        if custom_name:
            converted["CustomName"] = custom_name
        
        return converted
