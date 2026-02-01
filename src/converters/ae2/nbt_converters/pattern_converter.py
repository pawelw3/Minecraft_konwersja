"""
Pattern Converter for AE2

Konwertuje encoded patterns z 1.7.10 do 1.18.2.

UWAGA KLUCZOWA: W 1.18.2 AE2 uzywa Data Components (nie bezposredniego NBT)
i wymaga ID receptury dla crafting patterns, ktorej nie ma w 1.7.10!

Źródło 1.7.10:
    - Item: ItemEncodedPattern (appliedenergistics2:item.ItemEncodedPattern)
    - Klasa: appeng.items.misc.ItemEncodedPattern
    - Helper: appeng.helpers.PatternHelper
    - NBT:
        - "in": NBTTagList (9 slotow input)
        - "out": NBTTagList (output dla processing)
        - "crafting": boolean (true=crafting, false=processing)
        - "substitute": boolean

Źródło 1.18.2:
    - Crafting Item: ae2:crafting_pattern
    - Processing Item: ae2:processing_pattern
    - Klasa: appeng.crafting.pattern.EncodedPatternItem
    - Data Component: "encoded_crafting_pattern" / "encoded_processing_pattern"
    - EncodedCraftingPattern record:
        - inputs: List<ItemStack> (9 slotow)
        - result: ItemStack
        - recipeId: ResourceLocation (WYMAGANE!)
        - canSubstitute: boolean
        - canSubstituteFluids: boolean
    - EncodedProcessingPattern record:
        - inputs: List<GenericStack>
        - outputs: List<GenericStack>

KLUCZOWY PROBLEM:
    W 1.18.2 crafting pattern wymaga recipeId (ID receptury), ktorego nie ma w 1.7.10.
    W 1.7.10 pattern przechowuje tylko wynik (output), nie ID receptury.
    Oznacza to, ze konwersja crafting patterns wymaga dostepu do RecipeManager
    ze swiata docelowego, aby znalezc pasujaca recepture.

Rozwiazanie:
    - Processing patterns: konwertowane bezposrednio (input/output)
    - Crafting patterns: 
        a) Tryb "best-effort": szukamy receptury po wyniku (moze byc wiele!)
        b) Tryb "strict": blad jesli nie mozna jednoznacznie znalezc receptury
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from .base_converter import BaseNBTConverter, NBTConversionResult


@dataclass
class PatternData:
    """Reprezentacja danych patternu niezalezna od wersji"""
    pattern_type: str  # 'crafting' lub 'processing'
    inputs: List[Dict[str, Any]]  # Lista ItemStack
    outputs: List[Dict[str, Any]]  # Lista ItemStack
    can_substitute: bool = False
    can_substitute_fluids: bool = False
    # Tylko dla crafting:
    recipe_id: Optional[str] = None  # np. "minecraft:crafting_table"


class PatternConverter(BaseNBTConverter):
    """
    Konwerter dla encoded patterns.
    
    UWAGA: Konwersja crafting patterns jest problematyczna ze wzgledu na recipeId.
    """
    
    @property
    def converter_name(self) -> str:
        return "pattern"
    
    def convert_pattern(self, pattern_nbt: Dict[str, Any], 
                        item_id: str = None) -> Optional[PatternData]:
        """
        Parsuje NBT patternu 1.7.10 do formatu wewnetrznego.
        
        Args:
            pattern_nbt: NBT zawarte w tag patternu
            item_id: ID itemu (dla weryfikacji)
            
        Returns:
            PatternData lub None jesli blad
        """
        if not pattern_nbt:
            return None
        
        # Rozpoznaj typ patternu
        is_crafting = pattern_nbt.get('crafting', True)
        pattern_type = 'crafting' if is_crafting else 'processing'
        
        # Parsuj inputy (9 slotow)
        inputs = []
        in_tag = pattern_nbt.get('in', [])
        if isinstance(in_tag, list):
            for i, slot_nbt in enumerate(in_tag):
                if slot_nbt:
                    item = self._convert_item_stack(slot_nbt)
                    if item:
                        inputs.append(item)
        
        # Parsuj outputy
        outputs = []
        if is_crafting:
            # Dla crafting, output jest determinowany przez recepture
            # W 1.7.10 output jest w kondensowanych danych, nie bezposrednio w NBT
            # Ale w "out" tag moze byc dla niektorych wersji
            out_tag = pattern_nbt.get('out', [])
            if isinstance(out_tag, list):
                for slot_nbt in out_tag:
                    if slot_nbt:
                        item = self._convert_item_stack(slot_nbt)
                        if item:
                            outputs.append(item)
        else:
            # Dla processing, output jest bezposrednio w NBT
            out_tag = pattern_nbt.get('out', [])
            if isinstance(out_tag, list):
                for slot_nbt in out_tag:
                    if slot_nbt:
                        item = self._convert_item_stack(slot_nbt)
                        if item:
                            outputs.append(item)
        
        can_substitute = pattern_nbt.get('substitute', False)
        
        return PatternData(
            pattern_type=pattern_type,
            inputs=inputs,
            outputs=outputs,
            can_substitute=can_substitute,
            can_substitute_fluids=False  # W 1.7.10 nie ma tej flagi
        )
    
    def convert_to_1182(self, pattern_data: PatternData,
                       recipe_resolver=None) -> Tuple[str, Dict[str, Any]]:
        """
        Konwertuje PatternData do formatu 1.18.2.
        
        Args:
            pattern_data: Dane patternu
            recipe_resolver: Funkcja do rozwiązywania ID receptury (dla crafting)
            
        Returns:
            Krotka (item_id, component_data)
        """
        if pattern_data.pattern_type == 'processing':
            return self._convert_processing_pattern(pattern_data)
        else:
            return self._convert_crafting_pattern(pattern_data, recipe_resolver)
    
    def _convert_processing_pattern(self, pattern_data: PatternData) -> Tuple[str, Dict[str, Any]]:
        """Konwertuje processing pattern"""
        # W 1.18.2 processing pattern uzywa GenericStack (moze zawierac fluidy!)
        # Struktura: inputs (List<GenericStack>), outputs (List<GenericStack>)
        
        # Konwertuj inputy do formatu GenericStack (uproszczony)
        inputs = []
        for inp in pattern_data.inputs:
            inputs.append(self._to_generic_stack(inp))
        
        # Konwertuj outputy
        outputs = []
        for out in pattern_data.outputs:
            outputs.append(self._to_generic_stack(out))
        
        component_data = {
            'inputs': inputs,
            'outputs': outputs,
            'can_substitute': pattern_data.can_substitute
        }
        
        return 'ae2:processing_pattern', component_data
    
    def _convert_crafting_pattern(self, pattern_data: PatternData,
                                  recipe_resolver=None) -> Tuple[str, Dict[str, Any]]:
        """
        Konwertuje crafting pattern.
        
        UWAGA: Wymaga recipe_resolver do znalezienia ID receptury!
        """
        if recipe_resolver and pattern_data.outputs:
            # Sprobuj znalezc recepture po wyniku
            main_output = pattern_data.outputs[0]
            recipe_id = recipe_resolver(main_output)
        else:
            recipe_id = None
        
        if not recipe_id:
            # Nie udalo sie znalezc receptury
            self._add_warning(
                f"Nie mozna znalezc ID receptury dla crafting pattern. "
                f"Output: {pattern_data.outputs[0] if pattern_data.outputs else 'brak'}. "
                f"Wymagany recipe_resolver ze swiata docelowego."
            )
            # Zwracamy pattern z placeholderem - wymaga recznej naprawy
            recipe_id = "minecraft:unknown"
        
        # Przygotuj inputy (9 slotow, moze zawierac puste)
        inputs = []
        for i in range(9):
            if i < len(pattern_data.inputs):
                inputs.append(pattern_data.inputs[i])
            else:
                inputs.append({})  # Pusty slot
        
        # Glowny wynik
        result = pattern_data.outputs[0] if pattern_data.outputs else {}
        
        component_data = {
            'inputs': inputs,
            'result': result,
            'recipeId': recipe_id,
            'canSubstitute': pattern_data.can_substitute,
            'canSubstituteFluids': pattern_data.can_substitute_fluids
        }
        
        return 'ae2:crafting_pattern', component_data
    
    def _to_generic_stack(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje ItemStack do formatu GenericStack (1.18.2).
        
        GenericStack moze reprezentowac item lub fluid.
        """
        return {
            'item': item_data.get('id'),
            'count': item_data.get('Count', 1),
            'tag': item_data.get('tag')
        }
    
    def convert(self, nbt_1710: Dict[str, Any], block_id: str = None,
                metadata: int = 0) -> NBTConversionResult:
        """
        Konwertuje NBT patternu 1.7.10 do formatu 1.18.2.
        
        To jest metoda z BaseNBTConverter, ale PatternConverter
        dziala inaczej - zwraca dane komponentu, nie NBT BE.
        """
        self.reset()
        
        pattern_data = self.convert_pattern(nbt_1710)
        if not pattern_data:
            self._add_error("Nie mozna sparsowac patternu 1.7.10")
            return self._create_result(None, success=False)
        
        item_id, component_data = self.convert_to_1182(pattern_data)
        
        # Zwracamy dane w formacie zrozumialym dla InterfaceConverter
        result = {
            '__is_pattern': True,
            'item_id': item_id,
            'component_data': component_data,
            'pattern_type': pattern_data.pattern_type
        }
        
        return self._create_result(result)
