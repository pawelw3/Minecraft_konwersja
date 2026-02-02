"""
Edge Cases Handler dla BiblioCraft - obsługa nietypowych sytuacji

Ten moduł obsługuje:
1. Brakujące tekstury (fallback do znanych)
2. Uszkodzone dane NBT (naprawa lub pominięcie)
3. Nieznane typy bloków (detekcja i logowanie)
4. Konflikty ID (rozwiązywanie)
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
import logging
import traceback


@dataclass
class EdgeCase:
    """Reprezentacja edge case"""
    case_type: str
    description: str
    position: Optional[Tuple[int, int, int]] = None
    original_data: Any = None
    resolution: str = "unresolved"
    fallback_applied: bool = False


class EdgeCaseLogger:
    """Logger dla edge cases"""
    
    def __init__(self):
        self.cases: List[EdgeCase] = []
        self.handlers: Dict[str, Callable] = {}
        
        # Rejestracja domyślnych handlerów
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Rejestruje domyślne handlery"""
        self.handlers["missing_texture"] = self._handle_missing_texture
        self.handlers["corrupted_nbt"] = self._handle_corrupted_nbt
        self.handlers["unknown_block"] = self._handle_unknown_block
        self.handlers["missing_te_data"] = self._handle_missing_te_data
        self.handlers["invalid_inventory"] = self._handle_invalid_inventory
        self.handlers["unknown_mod_texture"] = self._handle_unknown_mod_texture
    
    def log_case(self, case: EdgeCase) -> EdgeCase:
        """Loguje edge case i próbuje go rozwiązać"""
        self.cases.append(case)
        
        # Spróbuj znaleźć handler
        handler = self.handlers.get(case.case_type)
        if handler:
            try:
                resolved_case = handler(case)
                return resolved_case
            except Exception as e:
                case.resolution = f"handler_error: {str(e)}"
        
        return case
    
    def _handle_missing_texture(self, case: EdgeCase) -> EdgeCase:
        """Handler dla brakującej tekstury"""
        # Domyślnie użyj oak_planks
        case.resolution = "fallback_to_oak_planks"
        case.fallback_applied = True
        return case
    
    def _handle_corrupted_nbt(self, case: EdgeCase) -> EdgeCase:
        """Handler dla uszkodzonego NBT"""
        # Sprawdź czy możemy naprawić
        if case.original_data:
            # Próba naprawy - wyciągnij co się da
            case.resolution = "partial_recovery"
        else:
            case.resolution = "skip_block"
        return case
    
    def _handle_unknown_block(self, case: EdgeCase) -> EdgeCase:
        """Handler dla nieznanego bloku"""
        case.resolution = "log_and_skip"
        return case
    
    def _handle_missing_te_data(self, case: EdgeCase) -> EdgeCase:
        """Handler dla brakujących danych TileEntity"""
        case.resolution = "convert_as_decorative"
        case.fallback_applied = True
        return case
    
    def _handle_invalid_inventory(self, case: EdgeCase) -> EdgeCase:
        """Handler dla nieprawidłowego inventory"""
        case.resolution = "clear_inventory"
        case.fallback_applied = True
        return case
    
    def _handle_unknown_mod_texture(self, case: EdgeCase) -> EdgeCase:
        """Handler dla tekstury z nieznanego modu"""
        # Spróbuj znaleźć podobną teksturę
        case.resolution = "fallback_to_vanilla_oak"
        case.fallback_applied = True
        return case
    
    def get_cases_by_type(self, case_type: str) -> List[EdgeCase]:
        """Zwraca wszystkie przypadki danego typu"""
        return [c for c in self.cases if c.case_type == case_type]
    
    def get_statistics(self) -> Dict[str, int]:
        """Zwraca statystyki edge cases"""
        stats = {}
        for case in self.cases:
            stats[case.case_type] = stats.get(case.case_type, 0) + 1
        return stats


class BCNBTFixup:
    """
    Naprawia uszkodzone lub niekompletne dane NBT z BC
    """
    
    # Domyślne wartości dla różnych typów TE
    DEFAULTS = {
        "TileEntityBookcase": {
            "Items": [],
            "bookCount": 0
        },
        "TileEntityGenericShelf": {
            "shelfItems": []
        },
        "TileEntityArmorStand": {
            "armorItems": []
        },
        "TileEntityFramedChest": {
            "Items": [],
            "frameTexture": "minecraft:planks:0"
        },
        "TileEntityClock": {
            "hour": 0,
            "minute": 0
        },
        "TileEntityFancySign": {
            "signText": "",
            "textScale": 1.0
        },
        "TileEntityLabel": {
            "slotItem": {},
            "text": ""
        },
        "TileEntityPainting": {
            "resourceLocation": "",
            "paintingType": "custom"
        }
    }
    
    @classmethod
    def fixup_te_data(cls, te_data: Dict, te_id: str) -> Dict:
        """
        Naprawia dane TileEntity uzupełniając brakujące pola
        
        Args:
            te_data: Oryginalne dane TE
            te_id: ID TileEntity
            
        Returns:
            Naprawione dane
        """
        if not isinstance(te_data, dict):
            te_data = {}
        
        # Upewnij się że mamy ID
        if "id" not in te_data:
            te_data["id"] = te_id
        
        # Upewnij się że mamy pozycję
        for coord in ["x", "y", "z"]:
            if coord not in te_data:
                te_data[coord] = 0
        
        # Dodaj domyślne wartości dla znanego typu
        defaults = cls.DEFAULTS.get(te_id, {})
        for key, value in defaults.items():
            if key not in te_data or te_data[key] is None:
                te_data[key] = value
        
        return te_data
    
    @classmethod
    def sanitize_inventory(cls, items: List) -> List:
        """
        Czyści inventory usuwając nieprawidłowe itemy
        
        Args:
            items: Lista itemów
            
        Returns:
            Oczyśczona lista
        """
        if not isinstance(items, list):
            return []
        
        sanitized = []
        for item in items:
            if not isinstance(item, dict):
                continue
            
            # Sprawdź czy item ma wymagane pola
            if "id" not in item:
                continue
            
            # Upewnij się że Count istnieje
            if "Count" not in item:
                item["Count"] = 1
            
            # Upewnij się że Count jest liczbą
            try:
                item["Count"] = int(item["Count"])
            except (ValueError, TypeError):
                item["Count"] = 1
            
            sanitized.append(item)
        
        return sanitized
    
    @classmethod
    def fix_texture_id(cls, texture_id: str) -> str:
        """
        Naprawia ID tekstury jeśli jest nieprawidłowe
        
        Args:
            texture_id: Oryginalne ID tekstury
            
        Returns:
            Naprawione ID lub domyślne
        """
        if not texture_id or not isinstance(texture_id, str):
            return "minecraft:planks:0"
        
        # Sprawdź czy ID jest w poprawnym formacie
        if ":" not in texture_id:
            # Dodaj domyślny namespace
            return f"minecraft:{texture_id}"
        
        return texture_id


class UnknownBlockHandler:
    """
    Handler dla nieznanych typów bloków BC
    """
    
    # Znane ID BC
    KNOWN_BC_IDS = {
        "TileEntityBookcase",
        "TileEntityArmorStand",
        "TileEntityWeaponCase",
        "TileEntityPotionShelf",
        "TileEntityWeaponRack",
        "TileEntityGenericShelf",
        "TileEntityLabel",
        "TileEntityWritingDesk",
        "TileEntityTypeMachine",
        "TileEntityPrintPress",
        "TileEntityTable",
        "TileEntitySeat",
        "TileEntityLantern",
        "TileEntityLamp",
        "TileEntityCookieJar",
        "TileEntityDinnerPlate",
        "TileEntityDiscRack",
        "TileEntityMapFrame",
        "TileEntityFancySign",
        "TileEntityFancyWorkbench",
        "TileEntitySwordPedestal",
        "TileEntityFramedChest",
        "TileEntityFurniturePaneler",
        "TileEntityClock",
        "TileEntityPainting",
        "TileEntityPaintPress",
        "TileEntityBell",
        "TileEntityClipboard",
        "TileEntityFramedBookcase",
        "TileEntityFramedShelf",
        "TileEntityFramedLabel",
        "TileEntityFramedTable",
        "TileEntityFramedDesk",
        "TileEntityFramedSeat",
        "TileEntityFramedSign",
        "TileEntityFramedDoor",
        "TileEntityFramedTrapDoor",
        "TileEntityFramedFence",
        "TileEntityFramedGate",
    }
    
    @classmethod
    def is_known_block(cls, block_id: str) -> bool:
        """Sprawdza czy blok jest znany"""
        # Sprawdź dokładne dopasowanie
        if block_id in cls.KNOWN_BC_IDS:
            return True
        
        # Sprawdź czy zaczyna się od znanego prefixu
        for known in cls.KNOWN_BC_IDS:
            if block_id.endswith(known) or known in block_id:
                return True
        
        return False
    
    @classmethod
    def classify_unknown_block(cls, block_id: str, te_data: Dict) -> str:
        """
        Klasyfikuje nieznany blok próbując określić jego typ
        
        Returns:
            Sugerowany typ lub "unknown"
        """
        # Sprawdź pola w TE
        if "Items" in te_data and "bookCount" in te_data:
            return "probably_bookcase"
        
        if "shelfItems" in te_data:
            return "probably_shelf"
        
        if "armorItems" in te_data:
            return "probably_armor_stand"
        
        if "frameTexture" in te_data:
            return "probably_framed"
        
        if "resourceLocation" in te_data:
            return "probably_painting"
        
        if "signText" in te_data:
            return "probably_sign"
        
        return "unknown"


class TextureFallbackResolver:
    """
    Rozwiązuje problemy z brakującymi teksturami
    """
    
    # Fallback chain dla tekstur
    FALLBACK_CHAIN = {
        # Drewno
        "minecraft:planks:0": "minecraft:oak_planks",
        "minecraft:planks:1": "minecraft:spruce_planks",
        "minecraft:planks:2": "minecraft:birch_planks",
        "minecraft:planks:3": "minecraft:jungle_planks",
        "minecraft:planks:4": "minecraft:acacia_planks",
        "minecraft:planks:5": "minecraft:dark_oak_planks",
        # Logi
        "minecraft:log:0": "minecraft:oak_log",
        "minecraft:log:1": "minecraft:spruce_log",
        "minecraft:log:2": "minecraft:birch_log",
        "minecraft:log:3": "minecraft:jungle_log",
        "minecraft:log2:0": "minecraft:acacia_log",
        "minecraft:log2:1": "minecraft:dark_oak_log",
    }
    
    # Fallback dla modów
    MOD_FALLBACKS = {
        "BiomesOPlenty": "minecraft:oak_planks",
        "Forestry": "minecraft:oak_planks",
        "Natura": "minecraft:oak_planks",
        "CarpentersBlocks": "minecraft:oak_planks",
    }
    
    @classmethod
    def resolve_texture(cls, texture_id: str) -> Tuple[str, bool]:
        """
        Rozwiązuje teksturę znajdując odpowiednik
        
        Returns:
            Tuple (resolved_id, used_fallback)
        """
        # Sprawdź dokładne dopasowanie
        if texture_id in cls.FALLBACK_CHAIN:
            return cls.FALLBACK_CHAIN[texture_id], True
        
        # Sprawdź czy to tekstura z modu
        if ":" in texture_id:
            mod_id = texture_id.split(":")[0]
            if mod_id in cls.MOD_FALLBACKS:
                return cls.MOD_FALLBACKS[mod_id], True
        
        # Jeśli nie znamy, zwróć domyślną
        return "minecraft:oak_planks", True
    
    @classmethod
    def is_vanilla_texture(cls, texture_id: str) -> bool:
        """Sprawdza czy tekstura jest z vanilla Minecraft"""
        return texture_id.startswith("minecraft:")


class BCEdgeCaseManager:
    """
    Główny menedżer edge cases dla BiblioCraft
    
    Koordynuje obsługę wszystkich nietypowych sytuacji.
    """
    
    def __init__(self):
        self.logger = EdgeCaseLogger()
        self.fixup = BCNBTFixup()
        self.unknown_handler = UnknownBlockHandler()
        self.texture_resolver = TextureFallbackResolver()
    
    def process_block(self, te_data: Dict, block_id: str, 
                      pos: Tuple[int, int, int]) -> Dict:
        """
        Przetwarza blok obsługując edge cases
        
        Args:
            te_data: Dane TileEntity
            block_id: ID bloku
            pos: Pozycja
            
        Returns:
            Przetworzone dane
        """
        result = {
            "te_data": te_data,
            "block_id": block_id,
            "warnings": [],
            "used_fallbacks": []
        }
        
        # Sprawdź czy blok jest znany
        if not self.unknown_handler.is_known_block(block_id):
            case = EdgeCase(
                case_type="unknown_block",
                description=f"Nieznany typ bloku: {block_id}",
                position=pos,
                original_data=te_data
            )
            resolved = self.logger.log_case(case)
            result["warnings"].append(f"Nieznany blok: {block_id}")
        
        # Napraw NBT jeśli potrzeba
        te_data = self.fixup.fixup_te_data(te_data, block_id)
        
        # Sprawdź teksturę (dla Framed blocks)
        if "Framed" in block_id and "frameTexture" in te_data:
            texture = te_data["frameTexture"]
            resolved_texture, used_fallback = self.texture_resolver.resolve_texture(texture)
            
            if used_fallback:
                case = EdgeCase(
                    case_type="missing_texture",
                    description=f"Nieznana tekstura: {texture}, użyto: {resolved_texture}",
                    position=pos,
                    original_data=texture
                )
                self.logger.log_case(case)
                result["warnings"].append(f"Tekstura {texture} -> {resolved_texture}")
                result["used_fallbacks"].append(("texture", texture, resolved_texture))
            
            te_data["frameTexture"] = resolved_texture
        
        # Napraw inventory
        for inv_key in ["Items", "shelfItems", "armorItems"]:
            if inv_key in te_data:
                original = te_data[inv_key]
                fixed = self.fixup.sanitize_inventory(original)
                if len(fixed) != len(original):
                    case = EdgeCase(
                        case_type="invalid_inventory",
                        description=f"Usunięto nieprawidłowe itemy z {inv_key}",
                        position=pos
                    )
                    self.logger.log_case(case)
                    result["warnings"].append(f"Naprawiono inventory: {inv_key}")
                te_data[inv_key] = fixed
        
        result["te_data"] = te_data
        return result
    
    def get_summary(self) -> Dict:
        """Zwraca podsumowanie edge cases"""
        return {
            "total_cases": len(self.logger.cases),
            "by_type": self.logger.get_statistics(),
            "fallbacks_used": sum(
                1 for c in self.logger.cases if c.fallback_applied
            )
        }


# Testowanie
if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Edge Cases Handler")
    print("=" * 60)
    
    # Test fixup NBT
    print("\n--- Test NBT Fixup ---")
    broken_te = {
        "id": "TileEntityBookcase",
        "x": 100,
        # Brak y, z
        # Brak Items i bookCount
    }
    
    fixed = BCNBTFixup.fixup_te_data(broken_te, "TileEntityBookcase")
    print(f"  Naprawione y: {fixed.get('y', 'BRAK')}")
    print(f"  Naprawione z: {fixed.get('z', 'BRAK')}")
    print(f"  Naprawione Items: {fixed.get('Items', 'BRAK')}")
    print(f"  Naprawione bookCount: {fixed.get('bookCount', 'BRAK')}")
    
    # Test texture resolver
    print("\n--- Test Texture Resolver ---")
    textures = [
        "minecraft:planks:0",
        "BiomesOPlenty:planks:3",
        "UnknownMod:block:5",
    ]
    
    for tex in textures:
        resolved, fallback = TextureFallbackResolver.resolve_texture(tex)
        print(f"  {tex} -> {resolved} (fallback: {fallback})")
    
    # Test edge case manager
    print("\n--- Test Edge Case Manager ---")
    manager = BCEdgeCaseManager()
    
    te_data = {
        "id": "TileEntityFramedChest",
        "x": 100, "y": 64, "z": 200,
        "frameTexture": "UnknownMod:custom_block",
        "Items": [
            {"id": "minecraft:diamond", "Count": 5},
            {"invalid": "item"},  # Nieprawidłowy
        ]
    }
    
    result = manager.process_block(te_data, "TileEntityFramedChest", (100, 64, 200))
    
    print(f"  Ostrzeżenia: {result['warnings']}")
    print(f"  Fallbacks: {result['used_fallbacks']}")
    print(f"  Inventory po naprawie: {len(result['te_data']['Items'])} itemów")
    
    print("\n--- Podsumowanie Edge Cases ---")
    summary = manager.get_summary()
    print(f"  Całkowita liczba: {summary['total_cases']}")
    print(f"  Użyte fallbacki: {summary['fallbacks_used']}")
    
    print("\n" + "=" * 60)
    print("Test zakończony!")
    print("=" * 60)
