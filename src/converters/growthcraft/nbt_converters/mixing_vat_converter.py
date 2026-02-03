"""
Konwerter NBT dla MixingVat (Kadź do sera)

WAŻNE: W 1.7.10 nazywa się CheeseVat, w 1.18.2 MixingVat!

Mapowanie 1.7.10 -> 1.18.2:
- grcmilk:cheese_vat -> growthcraft:mixing_vat
- TileEntityCheeseVat -> MixingVatBlockEntity

Zmiany NBT:
- progress (float) -> CurrentProcessTicks (int)
- progress_max (int) -> MaxProcessTicks (int)
- vat_state (String) -> USUNIĘTE (wnioskowane z stanu)
- heat_component.heat_multiplier (float) -> RequiresHeatSource (boolean)
- TankPrimary (NBTTagCompound) -> InputFluidTank (CompoundTag)
- TankRennet (NBTTagCompound) -> USUNIĘTE (sloty inventory)
- TankWaste (NBTTagCompound) -> ReagentFluidTank (CompoundTag)
- TankRecipe (NBTTagCompound) -> USUNIĘTE (sloty inventory)
- items (NBTTagList) -> inventory (CompoundTag)
+ IsActivated (boolean) - **NOWOŚĆ - KLUCZOWA ZMIANA!**
+ ActivationTool (CompoundTag) - **NOWOŚĆ**
+ ResultActivationTool (CompoundTag) - **NOWOŚĆ**

Zmiany funkcjonalne w 1.18.2:
1. **System aktywacji**: Proces WYMAGA aktywacji narzędziem (np. mieczem)!
2. **Dwa typy receptur**:
   - MixingVatFluidRecipe - wynikiem jest płyn (curds, ricotta)
   - MixingVatItemRecipe - wynikiem jest item (blok sera)
3. **Sloty inventory**:
   - Slot 0-2: składniki (sól, kultura, itp.)
   - Slot 3: wynik (tylko dla ItemRecipe)
4. **Narzędzia**:
   - ActivationTool: Narzędzie do rozpoczęcia procesu (miecz)
   - ResultActivationTool: Narzędzie do pobrania wyniku (cheese_cloth)
"""

from typing import Dict, Any, Optional, List
from .base_converter import BaseGrowthcraftNBTConverter, NBTConversionResult


class MixingVatNBTConverter(BaseGrowthcraftNBTConverter):
    """
    Konwerter NBT dla kadzi do sera GrowthCraft.
    
    Obsługuje konwersję z TileEntityCheeseVat (1.7.10) 
    do MixingVatBlockEntity (1.18.2).
    
    UWAGA: W 1.18.2 proces wymaga aktywacji narzędziem!
    """
    
    # Domyślny czas procesu w tickach (2 minuty)
    DEFAULT_PROCESSING_TIME = 2400
    
    @property
    def converter_name(self) -> str:
        return "MixingVatNBTConverter"
    
    @property
    def source_te_id(self) -> str:
        return "grcmilk:cheese_vat"
    
    @property
    def target_te_id(self) -> str:
        return "growthcraft:mixing_vat"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT kadzi do sera z 1.7.10 do 1.18.2.
        
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
            self._add_error(f"Błąd konwersji MixingVat: {str(e)}")
            return self._create_result(success=False)
    
    def _convert_nbt(self, nbt_1710: Dict[str, Any]) -> Dict[str, Any]:
        """
        Główna logika konwersji NBT.
        """
        converted = {
            "id": self.target_te_id
        }
        
        # === Konwersja postępu ===
        # progress (float) -> CurrentProcessTicks (int)
        progress = nbt_1710.get("progress", 0.0)
        converted["CurrentProcessTicks"] = int(progress)
        
        # progress_max (int) -> MaxProcessTicks (int)
        progress_max = nbt_1710.get("progress_max", self.DEFAULT_PROCESSING_TIME)
        converted["MaxProcessTicks"] = progress_max
        
        # === vat_state (String) ===
        # Stan w 1.7.10: "idle", "preparing_curds", "preparing_cheese", "preparing_ricotta"
        vat_state = nbt_1710.get("vat_state", "idle")
        
        # === heat_component ===
        heat_component = nbt_1710.get("heat_component", {})
        heat_multiplier = heat_component.get("heat_multiplier", 0.0)
        
        # heat_multiplier (float) -> RequiresHeatSource (boolean)
        converted["RequiresHeatSource"] = heat_multiplier > 0
        
        # === Konwersja zbiorników płynu ===
        # TankPrimary -> InputFluidTank
        tank_primary = nbt_1710.get("TankPrimary")
        if tank_primary:
            converted["InputFluidTank"] = self._convert_fluid_stack(tank_primary)
        
        # TankRennet -> USUNIĘTE (teraz w slotach inventory)
        tank_rennet = nbt_1710.get("TankRennet")
        if tank_rennet:
            self._add_warning("TankRennet przeniesiony do slotów inventory w 1.18.2")
        
        # TankWaste -> ReagentFluidTank
        tank_waste = nbt_1710.get("TankWaste")
        if tank_waste:
            converted["ReagentFluidTank"] = self._convert_fluid_stack(tank_waste)
        
        # TankRecipe -> USUNIĘTE (teraz w slotach inventory)
        tank_recipe = nbt_1710.get("TankRecipe")
        if tank_recipe:
            self._add_warning("TankRecipe przeniesiony do slotów inventory w 1.18.2")
        
        # === Konwersja inventory ===
        items = nbt_1710.get("items", [])
        converted["inventory"] = self._convert_inventory(items)
        
        # === System aktywacji (NOWOŚĆ w 1.18.2!) ===
        # W 1.18.2 proces musi być aktywowany narzędziem
        # Automatycznie aktywujemy jeśli mamy składniki i ciepło
        should_activate = self._should_auto_activate(nbt_1710, vat_state)
        converted["IsActivated"] = should_activate
        
        if should_activate:
            # Domyślne narzędzie aktywacji: drewniany miecz
            converted["ActivationTool"] = {
                "id": "minecraft:wooden_sword",
                "Count": 1
            }
            
            # Narzędzie do pobrania wyniku
            converted["ResultActivationTool"] = {
                "id": "growthcraft:cheese_cloth",
                "Count": 1
            }
            
            self._add_warning(
                "Automatycznie aktywowano proces. "
                "Gracz musi użyć wooden_sword aby rozpocząć i cheese_cloth aby zakończyć."
            )
        
        # === CustomName ===
        custom_name = nbt_1710.get("CustomName")
        if custom_name:
            converted["CustomName"] = custom_name
        
        return converted
    
    def _should_auto_activate(self, nbt_1710: Dict[str, Any], vat_state: str) -> bool:
        """
        Decyduje czy proces powinien być automatycznie aktywowany.
        
        Aktywujemy jeśli:
        1. vat_state != "idle" (proces w toku)
        2. Mamy płyn w TankPrimary
        3. Mamy ciepło
        """
        if vat_state == "idle":
            return False
        
        tank_primary = nbt_1710.get("TankPrimary", {})
        if not tank_primary or tank_primary.get("Amount", 0) <= 0:
            return False
        
        heat_component = nbt_1710.get("heat_component", {})
        if heat_component.get("heat_multiplier", 0) <= 0:
            return False
        
        return True
    
    def _convert_inventory(self, items_list: List[Dict]) -> Dict[str, Any]:
        """
        Konwertuje inventory dla MixingVat.
        
        1.7.10: items[0-2] = składniki
        1.18.2: slot 0-2 = składniki, slot 3 = wynik (dla ItemRecipe)
        """
        items = []
        
        for slot_data in items_list:
            if not slot_data:
                continue
            
            converted = self._convert_item_stack(slot_data)
            if converted:
                slot = slot_data.get('Slot', 0)
                
                # Specjalna obsługa dla podpuszczki (rennet)
                # W 1.7.10 była w TankRennet, w 1.18.2 w slotach
                item_id = converted.get('id', '')
                if 'rennet' in item_id:
                    self._add_warning(
                        f"Podpuszczka ({item_id}) powinna być w slotach inventory w 1.18.2"
                    )
                
                converted['Slot'] = slot
                items.append(converted)
        
        return {
            'Size': 4,  # 4 sloty: 0-2 składniki, 3 wynik
            'Items': items
        }
    
    def _detect_recipe_type(self, nbt_1710: Dict[str, Any]) -> str:
        """
        Wykrywa typ receptury na podstawie stanu.
        
        Returns:
            "fluid" dla MixingVatFluidRecipe (curds, ricotta)
            "item" dla MixingVatItemRecipe (blok sera)
        """
        vat_state = nbt_1710.get("vat_state", "idle")
        
        if vat_state == "preparing_cheese":
            return "item"
        elif vat_state in ["preparing_curds", "preparing_ricotta"]:
            return "fluid"
        
        return "unknown"
    
    def convert_back(self, nbt_1182: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje NBT z powrotem z 1.18.2 do 1.7.10.
        """
        converted = {
            "id": self.source_te_id
        }
        
        # CurrentProcessTicks -> progress
        current_ticks = nbt_1182.get("CurrentProcessTicks", 0)
        converted["progress"] = float(current_ticks)
        
        # MaxProcessTicks -> progress_max
        max_ticks = nbt_1182.get("MaxProcessTicks", self.DEFAULT_PROCESSING_TIME)
        converted["progress_max"] = max_ticks
        
        # Wnioskowanie vat_state z IsActivated i płynów
        is_activated = nbt_1182.get("IsActivated", False)
        input_tank = nbt_1182.get("InputFluidTank", {})
        input_fluid = input_tank.get("FluidName", "")
        
        if is_activated:
            if "curds" in input_fluid or "ricotta" in input_fluid:
                converted["vat_state"] = "preparing_curds"
            else:
                converted["vat_state"] = "preparing_cheese"
        else:
            converted["vat_state"] = "idle"
        
        # RequiresHeatSource -> heat_component
        requires_heat = nbt_1182.get("RequiresHeatSource", False)
        converted["heat_component"] = {
            "heat_multiplier": 1.0 if requires_heat else 0.0
        }
        
        # InputFluidTank -> TankPrimary
        input_tank = nbt_1182.get("InputFluidTank")
        if input_tank:
            converted["TankPrimary"] = input_tank
        
        # ReagentFluidTank -> TankWaste
        reagent_tank = nbt_1182.get("ReagentFluidTank")
        if reagent_tank:
            converted["TankWaste"] = reagent_tank
        
        # TankRennet i TankRecipe nie ma w 1.18.2 (w slotach)
        # Zostawiamy puste
        
        # inventory -> items
        inventory = nbt_1182.get("inventory", {})
        items_1182 = inventory.get("Items", [])
        
        if items_1182:
            converted["items"] = items_1182
        
        # CustomName
        custom_name = nbt_1182.get("CustomName")
        if custom_name:
            converted["CustomName"] = custom_name
        
        # Uwaga o aktywacji
        if is_activated:
            activation_tool = nbt_1182.get("ActivationTool", {})
            tool_id = activation_tool.get("id", "unknown")
            self._add_warning(
                f"Proces był aktywowany narzędziem {tool_id} w 1.18.2"
            )
        
        return converted
