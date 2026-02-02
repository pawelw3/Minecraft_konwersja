"""
Symulacja systemu Immersive Paintings (1.18.2) - Konwersja z BiblioCraft (1.7.10)

Ta symulacja pokazuje:
1. Jak Immersive Paintings przechowuje dane obrazów
2. Jak konwertować Custom Paintings z BC
3. System rejestracji i zarządzania obrazami
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import hashlib


class PaintingSize(Enum):
    """Dostępne rozmiary obrazów w Immersive Paintings"""
    SIZE_1x1 = (1, 1)
    SIZE_1x2 = (1, 2)
    SIZE_2x1 = (2, 1)
    SIZE_2x2 = (2, 2)
    SIZE_4x2 = (4, 2)
    SIZE_4x3 = (4, 3)
    SIZE_4x4 = (4, 4)
    SIZE_8x4 = (8, 4)
    SIZE_8x6 = (8, 6)
    SIZE_8x8 = (8, 8)


class PaintingFilter(Enum):
    """Filtry dostępne w Immersive Paintings"""
    NONE = "none"
    SEPIA = "sepia"
    GRAYSCALE = "grayscale"
    NEGATIVE = "negative"
    PIXELATE = "pixelate"


@dataclass
class PaintingData:
    """
    Dane obrazu w systemie Immersive Paintings
    
    Obrazy są przechowywane na serwerze i identyfikowane przez:
    - name: unikalna nazwa (ID)
    - width/height: rozmiar w blokach
    - image_data: dane obrazu (bytes)
    """
    name: str  # ID obrazu (np. "custom_sunset")
    width: int  # szerokość w blokach
    height: int  # wysokość w blokach
    author: str = "unknown"  # autor (gracz)
    filter_type: PaintingFilter = PaintingFilter.NONE
    visibility: str = "public"  # public/private
    image_hash: str = ""  # hash dla weryfikacji
    
    @staticmethod
    def calculate_hash(image_bytes: bytes) -> str:
        """Oblicza hash obrazu"""
        return hashlib.md5(image_bytes).hexdigest()[:8]


@dataclass
class ImmersivePaintingEntity:
    """
    Symulacja ImmersivePaintingEntity z 1.18.2
    
    Kluczowe pola NBT:
    - Motive: Identifier (nazwa obrazu)
    - Frame: Identifier (styl ramki)
    - Material: Identifier (materiał ramki)
    - width/height: rozmiar w blokach (automatycznie z PaintingData)
    """
    pos: Tuple[int, int, int]
    facing: str = "north"  # kierunek (north, south, east, west)
    rotation: int = 0  # obrót (0, 90, 180, 270)
    
    # ID obrazu (odniesienie do PaintingData)
    motive: str = "immersive_paintings:none"
    
    # Styl ramki
    frame: str = "immersive_paintings:classic"
    
    # Materiał ramki
    material: str = "immersive_paintings:wood"
    
    def set_painting(self, painting_name: str, painting_data: PaintingData):
        """Ustawia obraz"""
        self.motive = f"immersive_paintings:{painting_name}"
        print(f"  [ImmersivePainting] Ustawiono obraz: {painting_name}")
        print(f"    Rozmiar: {painting_data.width}x{painting_data.height}")
    
    def to_nbt(self) -> Dict:
        """Serializacja do NBT (1.18.2 format)"""
        return {
            # Podstawowe dane encji
            "Pos": list(self.pos),
            "Facing": self.facing,
            "Rotation": self.rotation,
            
            # Specyficzne dla obrazu
            "Motive": self.motive,
            "Frame": self.frame,
            "Material": self.material
        }
    
    @classmethod
    def from_nbt(cls, nbt: Dict) -> "ImmersivePaintingEntity":
        """Deserializacja z NBT"""
        pos = tuple(nbt.get("Pos", [0, 0, 0]))
        return cls(
            pos=pos,
            facing=nbt.get("Facing", "north"),
            rotation=nbt.get("Rotation", 0),
            motive=nbt.get("Motive", "immersive_paintings:none"),
            frame=nbt.get("Frame", "immersive_paintings:classic"),
            material=nbt.get("Material", "immersive_paintings:wood")
        )
    
    def get_width_pixels(self) -> int:
        """Zwraca szerokość w pikselach (1 blok = 16 pikseli)"""
        return self._get_size_from_motive()[0] * 16
    
    def get_height_pixels(self) -> int:
        """Zwraca wysokość w pikselach"""
        return self._get_size_from_motive()[1] * 16
    
    def _get_size_from_motive(self) -> Tuple[int, int]:
        """Pobiera rozmiar z danych obrazu (w rzeczywistości z PaintingData)"""
        # W symulacji zwracamy przykładowe wartości
        # W rzeczywistości pobierane z ClientPaintingManager/ServerPaintingManager
        if "small" in self.motive:
            return (1, 1)
        elif "medium" in self.motive:
            return (2, 2)
        elif "large" in self.motive:
            return (4, 3)
        return (1, 1)
    
    def __str__(self) -> str:
        return f"ImmersivePaintingEntity(motive={self.motive}, frame={self.frame})"


class PaintingManager:
    """
    Symulacja ServerPaintingManager / ClientPaintingManager
    
    Zarządza obrazami na serwerze - przechowuje dane i obsługuje
    żądania klientów.
    """
    
    def __init__(self):
        # Baza obrazów: name -> PaintingData
        self.paintings: Dict[str, PaintingData] = {}
        # Baza danych obrazów: name -> bytes
        self.image_data: Dict[str, bytes] = {}
    
    def register_painting(self, name: str, width: int, height: int, 
                          image_bytes: bytes, author: str = "unknown") -> PaintingData:
        """Rejestruje nowy obraz w systemie"""
        painting = PaintingData(
            name=name,
            width=width,
            height=height,
            author=author,
            image_hash=PaintingData.calculate_hash(image_bytes)
        )
        self.paintings[name] = painting
        self.image_data[name] = image_bytes
        print(f"  [PaintingManager] Zarejestrowano obraz: {name}")
        print(f"    Rozmiar: {width}x{height}, Hash: {painting.image_hash}")
        return painting
    
    def get_painting(self, name: str) -> Optional[PaintingData]:
        """Pobiera dane obrazu"""
        return self.paintings.get(name)
    
    def get_image_bytes(self, name: str) -> Optional[bytes]:
        """Pobiera dane binarne obrazu"""
        return self.image_data.get(name)


class BiblioCraftPaintingConverter:
    """
    Konwerter obrazów BiblioCraft na Immersive Paintings
    
    BC 1.7.10:
    - Obrazy przechowywane w folderze world/bibliocraft/paintings/
    - Nazwy plików: np. "custom_painting_1.png"
    - NBT: resourceLocation (ścieżka do pliku)
    
    Immersive Paintings 1.18.2:
    - Obazy rejestrowane w systemie modu
    - ID: Identifier (np. "immersive_paintings:sunset")
    - Przesyłane przez sieć do klientów
    """
    
    # Mapowanie rozmiarów obrazów BC na rozmiary Immersive Paintings
    SIZE_MAP = {
        # (width_blocks, height_blocks) -> PaintingSize
        (1, 1): PaintingSize.SIZE_1x1,
        (1, 2): PaintingSize.SIZE_1x2,
        (2, 1): PaintingSize.SIZE_2x1,
        (2, 2): PaintingSize.SIZE_2x2,
        (4, 2): PaintingSize.SIZE_4x2,
        (4, 3): PaintingSize.SIZE_4x3,
        (4, 4): PaintingSize.SIZE_4x4,
    }
    
    def __init__(self, painting_manager: PaintingManager):
        self.painting_manager = painting_manager
    
    def extract_size_from_bc_path(self, resource_path: str) -> Tuple[int, int]:
        """
        Ekstrahuje rozmiar z ścieżki BC
        
        BC używał: "bibliocraft:paintings/custom_16x16.png"
        lub predefiniowanych rozmiarów
        """
        # Domyślnie 1x1
        default_size = (1, 1)
        
        # Szukamy patternu WxH w nazwie pliku
        import re
        match = re.search(r'(\d+)x(\d+)', resource_path)
        if match:
            w, h = int(match.group(1)), int(match.group(2))
            # Konwertuj piksele na bloki (zakładając 16px = 1 blok)
            return (w // 16, h // 16)
        
        return default_size
    
    def convert_bc_painting(self, bc_resource_path: str, image_bytes: bytes,
                           pos: Tuple[int, int, int], facing: str = "north") -> ImmersivePaintingEntity:
        """
        Konwertuje obraz BC na Immersive Painting
        
        Args:
            bc_resource_path: np. "bibliocraft:paintings/custom/sunset.png"
            image_bytes: dane binarne obrazu
            pos: pozycja na ścianie
            facing: kierunek (north, south, east, west)
        """
        print(f"\n[Konwersja BC Painting -> Immersive Paintings]")
        print(f"  BC resource: {bc_resource_path}")
        
        # 1. Wydobyć nazwę obrazu z ścieżki
        image_name = bc_resource_path.split("/")[-1].replace(".png", "")
        # Dodaj prefix aby uniknąć konfliktów
        ip_name = f"bc_converted_{image_name}"
        print(f"  -> IP name: {ip_name}")
        
        # 2. Określić rozmiar
        width, height = self.extract_size_from_bc_path(bc_resource_path)
        print(f"  -> Rozmiar: {width}x{height} bloków")
        
        # 3. Zarejestrować obraz w systemie
        painting_data = self.painting_manager.register_painting(
            name=ip_name,
            width=width,
            height=height,
            image_bytes=image_bytes,
            author="bibliocraft_conversion"
        )
        
        # 4. Utworzyć encję obrazu
        entity = ImmersivePaintingEntity(
            pos=pos,
            facing=facing
        )
        entity.set_painting(ip_name, painting_data)
        
        return entity
    
    def convert_bc_painting_simple(self, bc_resource_path: str,
                                    pos: Tuple[int, int, int]) -> Dict:
        """
        Wersja uproszczona - tylko mapowanie danych NBT
        
        Używane gdy nie mamy dostępu do plików obrazów
        """
        print(f"\n[Konwersja NBT BC -> Immersive Paintings (simple)]")
        print(f"  BC resource: {bc_resource_path}")
        
        # Wydobyć nazwę
        image_name = bc_resource_path.split("/")[-1].replace(".png", "")
        ip_name = f"bc_converted_{image_name}"
        
        # Określić rozmiar
        width, height = self.extract_size_from_bc_path(bc_resource_path)
        
        # Zwrócić mapowanie NBT
        return {
            "bc_resource": bc_resource_path,
            "ip_motive": f"immersive_paintings:{ip_name}",
            "ip_frame": "immersive_paintings:classic",
            "ip_material": "immersive_paintings:wood",
            "width": width,
            "height": height,
            "needs_image_upload": True  # flaga: wymaga uploadu obrazu
        }


def run_simulation():
    """Uruchamia symulację konwersji obrazów"""
    print("=" * 60)
    print("SYMULACJA: BiblioCraft Paintings -> Immersive Paintings (1.18.2)")
    print("=" * 60)
    
    # Inicjalizacja managera obrazów
    painting_manager = PaintingManager()
    converter = BiblioCraftPaintingConverter(painting_manager)
    
    # Scenariusz 1: Konwersja obrazu z BC
    print("\n--- Scenariusz 1: Custom Painting (2x2 bloki) ---")
    bc_path = "bibliocraft:paintings/custom/sunset_32x32.png"
    dummy_image = b"fake_png_data_for_sunset_32x32"  # Symulacja danych obrazu
    
    painting_entity = converter.convert_bc_painting(
        bc_resource_path=bc_path,
        image_bytes=dummy_image,
        pos=(100, 65, 200),
        facing="north"
    )
    print(f"  Wynik: {painting_entity}")
    print(f"  NBT: {json.dumps(painting_entity.to_nbt(), indent=2)}")
    
    # Scenariusz 2: Konwersja dużego obrazu
    print("\n--- Scenariusz 2: Large Painting (4x3 bloki) ---")
    bc_path_large = "bibliocraft:paintings/custom/landscape_64x48.png"
    dummy_image_large = b"fake_png_data_for_landscape"
    
    large_painting = converter.convert_bc_painting(
        bc_resource_path=bc_path_large,
        image_bytes=dummy_image_large,
        pos=(105, 65, 200),
        facing="east"
    )
    print(f"  Wynik: {large_painting}")
    
    # Scenariusz 3: Konwersja bez dostępu do plików (tylko NBT)
    print("\n--- Scenariusz 3: Konwersja NBT bez pliku ---")
    bc_path_simple = "bibliocraft:paintings/custom/portrait_16x32.png"
    
    simple_mapping = converter.convert_bc_painting_simple(
        bc_resource_path=bc_path_simple,
        pos=(110, 65, 200)
    )
    print(f"  Mapowanie: {json.dumps(simple_mapping, indent=2)}")
    
    # Scenariusz 4: Weryfikacja obrazów w managerze
    print("\n--- Scenariusz 4: Lista zarejestrowanych obrazów ---")
    print(f"  Liczba obrazów: {len(painting_manager.paintings)}")
    for name, data in painting_manager.paintings.items():
        print(f"    - {name}: {data.width}x{data.height} (hash: {data.image_hash})")
    
    # Scenariusz 5: Round-trip NBT
    print("\n--- Scenariusz 5: Test round-trip NBT ---")
    nbt_data = painting_entity.to_nbt()
    restored = ImmersivePaintingEntity.from_nbt(nbt_data)
    print(f"  Oryginał: {painting_entity}")
    print(f"  Przywrócony: {restored}")
    print(f"  Zgodność motive: {painting_entity.motive == restored.motive}")
    
    print("\n" + "=" * 60)
    print("Symulacja zakończona pomyślnie!")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation()
