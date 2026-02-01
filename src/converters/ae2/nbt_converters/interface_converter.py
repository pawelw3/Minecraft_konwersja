"""
ME Interface Converter

Konwertuje NBT ME Interface z 1.7.10 do 1.18.2.

UWAGA: W 1.18.2 funkcjonalność Interface została podzielona:
- Interface - tylko storage (9 slotów config + 9 slotów storage)
- Pattern Provider - patterny do craftingu (9 slotów)

W 1.7.10 Interface robiło obie rzeczy na raz.

Źródło 1.7.10:
    - appeng.tile.misc.TileInterface
    - używa DualityInterface do obsługi storage + patternów
    
Źródło 1.18.2:
    - Interface: appeng.blockentity.misc.InterfaceBlockEntity
    - PatternProvider: appeng.blockentity.crafting.PatternProviderBlockEntity
"""

from typing import Dict, Any, List, Optional
from .base_converter import BaseNBTConverter, NBTConversionResult
from .pattern_converter import PatternConverter, PatternData


class InterfaceConverter(BaseNBTConverter):
    """
    Konwerter dla ME Interface.
    
    KLUCZOWA DECYZJA KONWERSYJNA:
    Interface z 1.7.10 musi zostać podzielone na:
    1. Interface (storage) - zachowuje config i storage
    2. Pattern Provider (jeśli ma patterny) - osobny blok w 1.18.2
    
    UWAGA: Orientacja jest w BlockState, nie w NBT!
    """
    
    @property
    def converter_name(self) -> str:
        return "interface"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT Interface.
        
        Zwraca dane dla Interface - patterny są obsługiwane osobno.
        
        Struktura 1.7.10 (appeng.tile.misc.TileInterface):
        {
            "config": [{...}, ...],      # 9 slotów config (ghost items)
            "storage": [{...}, ...],     # 9 slotów storage (real items)
            "patterns": [{...}, ...],    # Patterny (jeśli są)
            "priority": 0,               # int
            "fuzzyMode": 0,              # int enum
            "forward": 2,                # ForgeDirection (teraz w BlockState)
            "up": 1                      # ForgeDirection (teraz w BlockState)
        }
        
        Struktura 1.18.2 (appeng.blockentity.misc.InterfaceBlockEntity):
        {
            "priority": 0,               # int
            "fuzzyMode": "IGNORE_ALL",   # string enum
            "config": [...],             # 9 slotów
            "items": [...]               # 9 slotów storage
            # Orientacja: w BlockState (facing)
        }
        """
        self.reset()
        
        converted = {
            'priority': nbt_1710.get('priority', 0),
        }
        
        # Konwersja config (9 slotów)
        config_1710 = nbt_1710.get('config', [])
        if config_1710:
            converted['config'] = self._convert_config_slots(config_1710)
        
        # Konwersja storage (9 slotów)
        storage_1710 = nbt_1710.get('storage', [])
        if storage_1710:
            converted['items'] = self._convert_storage_slots(storage_1710)
        
        # Konwersja fuzzy mode
        fuzzy_mode = nbt_1710.get('fuzzyMode', 0)
        converted['fuzzyMode'] = self._convert_fuzzy_mode(fuzzy_mode)
        
        # UWAGA: Orientacja jest w BlockState, nie w NBT!
        # Nie dodajemy 'visual' - to był placeholder
        
        # Sprawdź czy są patterny (do osobnej obsługi)
        patterns = nbt_1710.get('patterns', [])
        if patterns:
            self._add_warning(
                f"Interface ma {len(patterns)} patternów - "
                "wymagają Pattern Provider w 1.18.2"
            )
            # Zachowaj patterny w osobnym polu (do przetworzenia)
            patterns_result = self._convert_patterns(patterns)
            if patterns_result:
                converted['__patterns_for_provider'] = patterns_result
        
        return self._create_result(converted)
    
    def convert_to_pattern_provider(self, nbt_1710: Dict[str, Any],
                                     metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje Interface do Pattern Provider.
        
        Wywoływane gdy Interface ma patterny i trzeba stworzyć
        osobny Pattern Provider.
        
        Źródło 1.18.2: appeng.blockentity.crafting.PatternProviderBlockEntity
        
        Struktura:
        {
            "priority": int,
            "items": [...],              # 9 slotów na patterny
            "blockingMode": bool         # Tryb blokujący
            # Orientacja: w BlockState (facing)
        }
        """
        self.reset()
        
        patterns = nbt_1710.get('patterns', [])
        if not patterns:
            return self._create_result(None, success=False)
        
        patterns_converted = self._convert_patterns(patterns)
        if not patterns_converted:
            self._add_error("Nie udało się skonwertować patternów")
            return self._create_result(None, success=False)
        
        converted = {
            'priority': nbt_1710.get('priority', 0),
            'items': patterns_converted,
            'blockingMode': nbt_1710.get('blockingMode', False),
        }
        
        # UWAGA: Orientacja jest w BlockState, nie w NBT!
        
        return self._create_result(converted)
    
    def _convert_config_slots(self, config_1710: List[Dict]) -> List[Dict]:
        """Konwertuje sloty konfiguracyjne (ghost items)"""
        result = []
        for i, slot in enumerate(config_1710):
            if not slot:
                continue
            
            # Config slots to "ghost items" - tylko ID bez count
            converted = {
                'Slot': i,
                'id': self._convert_item_id(slot.get('id', '')),
                'Count': 1
            }
            result.append(converted)
        
        return result
    
    def _convert_storage_slots(self, storage_1710: List[Dict]) -> List[Dict]:
        """Konwertuje sloty storage (rzeczywiste itemy)"""
        result = []
        for slot in storage_1710:
            if not slot:
                continue
            
            converted = self._convert_item_stack(slot)
            if converted:
                converted['Slot'] = slot.get('Slot', 0)
                result.append(converted)
        
        return result
    
    def _convert_patterns(self, patterns_1710: List[Dict]) -> List[Dict]:
        """
        Konwertuje patterny.
        
        Patterny w 1.7.10 to encoded patterns w slotach.
        """
        result = []
        for i, pattern in enumerate(patterns_1710):
            if not pattern:
                continue
            
            converted = self._convert_pattern_item(pattern)
            if converted:
                converted['Slot'] = i
                result.append(converted)
        
        return result
    
    def _convert_pattern_item(self, pattern_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje encoded pattern.
        
        W 1.7.10 (appeng.items.misc.ItemEncodedPattern):
            - NBT: "in" (input list), "out" (output list), "crafting" (bool)
        
        W 1.18.2 (appeng.crafting.pattern.EncodedPattern):
            - NBT zależy od wersji - sprawdzić w źródle!
            
        UWAGA: To jest uproszczona implementacja. W rzeczywistości format
        encoded pattern w 1.18.2 może się różnić i wymaga weryfikacji
        w kodzie źródłowym AE2.
        """
        item_id = pattern_nbt.get('id', '')
        tag = pattern_nbt.get('tag', {})
        
        # Rozróżnij crafting vs processing
        is_crafting = tag.get('crafting', True) if tag else True
        
        # ID patternu w 1.18.2
        pattern_id = 'ae2:crafting_pattern' if is_crafting else 'ae2:processing_pattern'
        
        result = {
            'id': pattern_id,
            'Count': pattern_nbt.get('Count', 1)
        }
        
        if tag:
            # Konwertuj NBT patternu
            new_tag = self._convert_pattern_nbt(tag)
            if new_tag:
                result['tag'] = new_tag
        
        return result
    
    def _convert_pattern_nbt(self, pattern_tag: Dict[str, Any]) -> Dict[str, Any]:
        """
        DEPRECATED: Uzyj PatternConverter.
        
        Zachowane dla kompatybilnosci wstecz.
        """
        converter = PatternConverter()
        pattern_data = converter.convert_pattern(pattern_tag)
        if pattern_data:
            _, component = converter.convert_to_1182(pattern_data)
            return component
        return {}
    
    def _convert_fuzzy_mode(self, fuzzy_mode: int) -> str:
        """
        Konwertuje fuzzy mode z int (1.7.10) na string (1.18.2).
        
        1.7.10: 0-4 (int enum)
        1.18.2: enum FuzzyMode jako string
        """
        modes = {
            0: "IGNORE_ALL",
            1: "PERCENT_25",
            2: "PERCENT_50",
            3: "PERCENT_75",
            4: "PERCENT_99"
        }
        return modes.get(fuzzy_mode, "IGNORE_ALL")
