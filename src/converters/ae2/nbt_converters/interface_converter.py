"""
ME Interface Converter

Konwertuje NBT ME Interface z 1.7.10 do 1.18.2.

UWAGA: W 1.18.2 funkcjonalność Interface została podzielona:
- Interface - tylko storage (9 slotów config + 9 slotów storage)
- Pattern Provider - patterny do craftingu (9 slotów)

W 1.7.10 Interface robiło obie rzeczy na raz.
"""

from typing import Dict, Any, List
from .base_converter import BaseNBTConverter, NBTConversionResult


class InterfaceConverter(BaseNBTConverter):
    """
    Konwerter dla ME Interface.
    
    KLUCZOWA DECYZJA KONWERSYJNA:
    Interface z 1.7.10 musi zostać podzielone na:
    1. Interface (storage) - zachowuje config i storage
    2. Pattern Provider (jeśli ma patterny) - osobny blok w 1.18.2
    """
    
    @property
    def converter_name(self) -> str:
        return "interface"
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None) -> NBTConversionResult:
        """
        Konwertuje NBT Interface.
        
        Zwraca dane dla Interface - patterny są obsłiwane osobno.
        
        Struktura 1.7.10 (uproszczona):
        {
            "config": [{...}, ...],  # 9 slotów config
            "storage": [{...}, ...],  # 9 slotów storage
            "patterns": [{...}, ...],  # Patterny (jeśli są)
            "priority": 0,
            "fuzzyMode": 0,
            "forward": 2,
            "up": 1
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
        
        # Orientacja
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
        # Sprawdź czy są patterny (do osobnej obsługi)
        patterns = nbt_1710.get('patterns', [])
        if patterns:
            self._add_warning(
                f"Interface ma {len(patterns)} patternów - "
                "wymagają Pattern Provider w 1.18.2"
            )
            # Zachowaj patterny w osobnym polu (do przetworzenia)
            converted['__patterns_for_provider'] = self._convert_patterns(patterns)
        
        return self._create_result(converted)
    
    def convert_to_pattern_provider(self, nbt_1710: Dict[str, Any]) -> NBTConversionResult:
        """
        Konwertuje Interface do Pattern Provider.
        
        Wywoływane gdy Interface ma patterny i trzeba stworzyć
        osobny Pattern Provider.
        
        Zwraca None jeśli nie ma patternów.
        """
        self.reset()
        
        patterns = nbt_1710.get('patterns', [])
        if not patterns:
            return self._create_result(None, success=False)
        
        converted = {
            'priority': nbt_1710.get('priority', 0),
            'items': self._convert_patterns(patterns),
            'blockingMode': nbt_1710.get('blockingMode', False),
        }
        
        # Orientacja - Pattern Provider powinien być zwrócony
        # w stronę Molecular Assemblera
        orientation = self._get_orientation(nbt_1710)
        if orientation:
            converted['visual'] = {'rotation': orientation.get('facing', 'north')}
        
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
        
        W 1.7.10 pattern to item z NBT zawierającym:
        - in: lista input
        - out: lista output
        - crafting: bool
        
        W 1.18.2 podobnie, ale może mieć dodatkowe pola.
        """
        item_id = pattern_nbt.get('id', '')
        tag = pattern_nbt.get('tag', {})
        
        result = {
            'id': 'ae2:crafting_pattern',  # lub processing_pattern
            'Count': pattern_nbt.get('Count', 1)
        }
        
        if tag:
            # Konwertuj NBT patternu
            new_tag = self._convert_pattern_nbt(tag)
            if new_tag:
                result['tag'] = new_tag
        
        return result
    
    def _convert_pattern_nbt(self, pattern_tag: Dict[str, Any]) -> Dict[str, Any]:
        """Konwertuje NBT encoded pattern"""
        # Sprawdź czy to crafting czy processing
        is_crafting = pattern_tag.get('crafting', True)
        
        result = {
            'crafting': is_crafting
        }
        
        # Konwertuj inputs
        inputs = pattern_tag.get('in', [])
        if inputs:
            result['input'] = [
                self._convert_item_stack_for_pattern(inp)
                for inp in inputs
            ]
        
        # Konwertuj outputs
        outputs = pattern_tag.get('out', [])
        if outputs:
            result['output'] = [
                self._convert_item_stack_for_pattern(out)
                for out in outputs
            ]
        
        return result
    
    def _convert_item_stack_for_pattern(self, item_nbt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje ItemStack dla patternu.
        
        W 1.18.2 patterny używają nieco innego formatu.
        """
        result = {
            '#c': self._convert_item_id(item_nbt.get('id', '')),
        }
        
        # Dodaj count jeśli > 1
        count = item_nbt.get('Count', 1)
        if count > 1:
            result['count'] = count
        
        return result
    
    def _convert_fuzzy_mode(self, fuzzy_mode: int) -> str:
        """Konwertuje fuzzy mode"""
        modes = {
            0: "IGNORE_ALL",
            1: "PERCENT_25",
            2: "PERCENT_50",
            3: "PERCENT_75",
            4: "PERCENT_99"
        }
        return modes.get(fuzzy_mode, "IGNORE_ALL")
