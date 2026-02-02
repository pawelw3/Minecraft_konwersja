"""
System konwersji obrazów BiblioCraft -> Immersive Paintings

Ten moduł odpowiada za:
1. Odnajdywanie obrazów BC w folderze mapy
2. Konwersję formatu i rozmiarów
3. Rejestrację obrazów w systemie Immersive Paintings
4. Generowanie mapowania NBT dla obrazów
"""

import os
import re
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class BCImageInfo:
    """Informacje o obrazie z BiblioCraft"""
    original_path: str  # Pełna ścieżka do pliku
    relative_path: str  # Ścieżka względem folderu bibliocraft
    filename: str       # Nazwa pliku
    width_px: int       # Szerokość w pikselach
    height_px: int      # Wysokość w pikselach
    width_blocks: int   # Szerokość w blokach (px / 16)
    height_blocks: int  # Wysokość w blokach
    
    @property
    def size_category(self) -> str:
        """Zwraca kategorię rozmiaru obrazu"""
        total_blocks = self.width_blocks * self.height_blocks
        if total_blocks <= 1:
            return "small"
        elif total_blocks <= 4:
            return "medium"
        elif total_blocks <= 12:
            return "large"
        else:
            return "extra_large"


@dataclass
class IPImageRegistration:
    """Rejestracja obrazu w Immersive Paintings"""
    original_bc_path: str
    ip_name: str                    # Nazwa w IP (bc_<nazwa_pliku>)
    ip_identifier: str              # Pełny ID (immersive_paintings:bc_xxx)
    width_blocks: int
    height_blocks: int
    image_hash: str
    frame_style: str = "classic"
    material: str = "wood"
    
    def to_nbt_data(self) -> Dict:
        """Generuje dane NBT dla obrazu"""
        return {
            "Motive": self.ip_identifier,
            "Frame": f"immersive_paintings:{self.frame_style}",
            "Material": f"immersive_paintings:{self.material}",
            "width": self.width_blocks,
            "height": self.height_blocks,
            "original_bc": self.original_bc_path
        }


class BCImageScanner:
    """
    Skanuje folder mapy w poszukiwaniu obrazów BiblioCraft
    
    BC przechowywał obrazy w:
    - world/bibliocraft/paintings/
    - world/bibliocraft/paintings/custom/
    """
    
    DEFAULT_PAINTING_PATHS = [
        "bibliocraft/paintings",
        "bibliocraft/paintings/custom",
        "bibliocraft/custompaintings",
    ]
    
    SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg"]
    
    def __init__(self, world_path: str):
        self.world_path = Path(world_path)
        self.images: List[BCImageInfo] = []
        self.errors: List[str] = []
    
    def scan_for_images(self) -> List[BCImageInfo]:
        """
        Skanuje folder mapy w poszukiwaniu obrazów
        
        Returns:
            Lista znalezionych obrazów
        """
        self.images = []
        
        for relative_path in self.DEFAULT_PAINTING_PATHS:
            full_path = self.world_path / relative_path
            if full_path.exists():
                self._scan_directory(full_path, relative_path)
        
        return self.images
    
    def _scan_directory(self, directory: Path, relative_base: str):
        """Rekursywnie skanuje katalog"""
        try:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                        self._process_image_file(file_path, relative_base)
                elif file_path.is_dir():
                    # Rekursywnie skanuj podkatalogi
                    sub_relative = f"{relative_base}/{file_path.name}"
                    self._scan_directory(file_path, sub_relative)
        except Exception as e:
            self.errors.append(f"Błąd skanowania {directory}: {e}")
    
    def _process_image_file(self, file_path: Path, relative_base: str):
        """Przetwarza pojedynczy plik obrazu"""
        try:
            # Wyciągnij rozmiar z nazwy pliku lub użyj domyślnego
            width_px, height_px = self._extract_size_from_filename(file_path.name)
            
            # Oblicz rozmiar w blokach
            width_blocks = max(1, width_px // 16)
            height_blocks = max(1, height_px // 16)
            
            info = BCImageInfo(
                original_path=str(file_path),
                relative_path=f"{relative_base}/{file_path.name}",
                filename=file_path.name,
                width_px=width_px,
                height_px=height_px,
                width_blocks=width_blocks,
                height_blocks=height_blocks
            )
            
            self.images.append(info)
            
        except Exception as e:
            self.errors.append(f"Błąd przetwarzania {file_path}: {e}")
    
    def _extract_size_from_filename(self, filename: str) -> Tuple[int, int]:
        """
        Ekstrahuje rozmiar z nazwy pliku
        
        Formaty:
        - painting_16x16.png -> 16x16
        - sunset_32x64.png -> 32x64
        - bez rozmiaru -> 16x16 (domyślnie)
        """
        # Szukaj patternu <liczba>x<liczba> w nazwie
        match = re.search(r'(\d+)x(\d+)', filename)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        # Domyślnie 16x16 (1 blok)
        return 16, 16
    
    def get_images_by_size(self, min_blocks: int = 0, max_blocks: int = 100) -> List[BCImageInfo]:
        """Zwraca obrazy w zakresie rozmiarów"""
        return [
            img for img in self.images
            if min_blocks <= img.width_blocks * img.height_blocks <= max_blocks
        ]
    
    def get_statistics(self) -> Dict:
        """Zwraca statystyki znalezionych obrazów"""
        if not self.images:
            return {"total": 0}
        
        categories = {"small": 0, "medium": 0, "large": 0, "extra_large": 0}
        for img in self.images:
            categories[img.size_category] += 1
        
        return {
            "total": len(self.images),
            "by_category": categories,
            "errors": len(self.errors)
        }


class IPImageRegistry:
    """
    Rejestr obrazów dla Immersive Paintings
    
    Zarządza mapowaniem obrazów BC na identyfikatory IP.
    """
    
    # Dostępne rozmiary w Immersive Paintings
    VALID_SIZES = [
        (1, 1), (1, 2), (2, 1), (2, 2),
        (4, 2), (4, 3), (4, 4),
        (8, 4), (8, 6), (8, 8)
    ]
    
    def __init__(self):
        self.registrations: Dict[str, IPImageRegistration] = {}
        self.name_counter: Dict[str, int] = {}
    
    def register_image(self, bc_image: BCImageInfo, 
                      frame_style: str = "classic",
                      material: str = "wood") -> IPImageRegistration:
        """
        Rejestruje obraz BC w systemie IP
        
        Args:
            bc_image: Informacje o obrazie BC
            frame_style: Styl ramki (classic, simple, none)
            material: Materiał ramki (wood, iron, gold)
            
        Returns:
            Rejestracja obrazu
        """
        # Wygeneruj nazwę dla IP
        base_name = self._sanitize_filename(bc_image.filename)
        ip_name = self._generate_unique_name(base_name)
        
        # Dostosuj rozmiar do dozwolonych
        adjusted_width, adjusted_height = self._adjust_size(
            bc_image.width_blocks, 
            bc_image.height_blocks
        )
        
        # Oblicz hash (w prawdziwej implementacji - z pliku)
        image_hash = self._calculate_hash(bc_image.original_path)
        
        registration = IPImageRegistration(
            original_bc_path=bc_image.relative_path,
            ip_name=ip_name,
            ip_identifier=f"immersive_paintings:{ip_name}",
            width_blocks=adjusted_width,
            height_blocks=adjusted_height,
            image_hash=image_hash,
            frame_style=frame_style,
            material=material
        )
        
        self.registrations[bc_image.relative_path] = registration
        return registration
    
    def _sanitize_filename(self, filename: str) -> str:
        """Czyści nazwę pliku do użycia jako ID"""
        # Usuń rozszerzenie
        name = os.path.splitext(filename)[0]
        # Zamień niedozwolone znaki
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Usuń wielokrotne podkreślenia
        name = re.sub(r'_+', '_', name)
        # Usuń podkreślenia na końcach
        name = name.strip('_')
        # Dodaj prefix
        return f"bc_{name.lower()}"
    
    def _generate_unique_name(self, base_name: str) -> str:
        """Generuje unikalną nazwę"""
        if base_name not in self.name_counter:
            self.name_counter[base_name] = 0
            return base_name
        
        self.name_counter[base_name] += 1
        return f"{base_name}_{self.name_counter[base_name]}"
    
    def _adjust_size(self, width: int, height: int) -> Tuple[int, int]:
        """
        Dostosowuje rozmiar do dozwolonych w IP
        
        Znajduje najbliższy dozwolony rozmiar.
        """
        # Najpierw ogranicz do max
        width = min(width, 8)
        height = min(height, 8)
        
        # Znajdź najbliższy dozwolony rozmiar
        if (width, height) in self.VALID_SIZES:
            return width, height
        
        # Sprawdź czy odwrotna orientacja jest dozwolona
        if (height, width) in self.VALID_SIZES:
            return height, width
        
        # Znajdź najbliższy
        best_size = (1, 1)
        min_diff = float('inf')
        
        for valid_w, valid_h in self.VALID_SIZES:
            diff = abs(valid_w - width) + abs(valid_h - height)
            if diff < min_diff:
                min_diff = diff
                best_size = (valid_w, valid_h)
        
        return best_size
    
    def _calculate_hash(self, file_path: str) -> str:
        """Oblicza hash pliku obrazu"""
        try:
            # W prawdziwej implementacji - czytaj plik i licz hash
            # Na razie - hash z nazwy pliku + timestamp
            content = file_path.encode('utf-8')
            return hashlib.md5(content).hexdigest()[:8]
        except:
            return "unknown"
    
    def get_registration(self, bc_path: str) -> Optional[IPImageRegistration]:
        """Pobiera rejestrację dla obrazu BC"""
        return self.registrations.get(bc_path)
    
    def generate_nbt_for_painting(self, bc_resource_path: str, 
                                   pos: Tuple[int, int, int],
                                   facing: str = "north") -> Optional[Dict]:
        """
        Generuje NBT dla obrazu na podstawie ścieżki BC
        
        Args:
            bc_resource_path: Ścieżka w formacie BC (np. "bibliocraft:paintings/custom/sunset.png")
            pos: Pozycja (x, y, z)
            facing: Kierunek (north, south, east, west)
            
        Returns:
            Dane NBT lub None
        """
        # Wyciągnij nazwę pliku z resource path
        filename = bc_resource_path.split("/")[-1]
        
        # Znajdź rejestrację
        for reg_path, registration in self.registrations.items():
            if filename in reg_path or reg_path in bc_resource_path:
                nbt = registration.to_nbt_data()
                nbt.update({
                    "id": "immersive_paintings:painting",
                    "x": pos[0],
                    "y": pos[1],
                    "z": pos[2],
                    "Facing": facing
                })
                return nbt
        
        return None
    
    def export_registry(self, output_path: str):
        """Eksportuje rejestr do pliku JSON"""
        data = {
            bc_path: {
                "ip_name": reg.ip_name,
                "ip_identifier": reg.ip_identifier,
                "width_blocks": reg.width_blocks,
                "height_blocks": reg.height_blocks,
                "hash": reg.image_hash
            }
            for bc_path, reg in self.registrations.items()
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


class BCtoIPImageConverter:
    """
    Główny konwerter obrazów BC -> IP
    
    Koordynuje proces skanowania, rejestracji i konwersji.
    """
    
    def __init__(self, world_path: str):
        self.scanner = BCImageScanner(world_path)
        self.registry = IPImageRegistry()
        self.stats = {
            "found": 0,
            "registered": 0,
            "errors": 0
        }
    
    def run_conversion(self) -> Dict:
        """
        Uruchamia pełny proces konwersji obrazów
        
        Returns:
            Statystyki konwersji
        """
        # 1. Skanuj obrazy
        images = self.scanner.scan_for_images()
        self.stats["found"] = len(images)
        
        # 2. Zarejestruj każdy obraz
        for image in images:
            try:
                self.registry.register_image(image)
                self.stats["registered"] += 1
            except Exception as e:
                self.stats["errors"] += 1
                print(f"Błąd rejestracji {image.filename}: {e}")
        
        return self.get_statistics()
    
    def get_statistics(self) -> Dict:
        """Zwraca statystyki konwersji"""
        scan_stats = self.scanner.get_statistics()
        return {
            **self.stats,
            **scan_stats,
            "registry_size": len(self.registry.registrations)
        }
    
    def convert_painting_nbt(self, bc_nbt: Dict, pos: Tuple[int, int, int]) -> Optional[Dict]:
        """
        Konwertuje NBT obrazu BC na IP
        
        Args:
            bc_nbt: Dane NBT z BC
            pos: Pozycja
            
        Returns:
            NBT dla IP lub None
        """
        resource_path = bc_nbt.get("resourceLocation", "")
        facing = bc_nbt.get("facing", "north")
        
        return self.registry.generate_nbt_for_painting(resource_path, pos, facing)


# ============================================================================
# FUNKCJE POMOCNICZE
# ============================================================================

def convert_painting_bc_to_ip(bc_resource_path: str, 
                               pos: Tuple[int, int, int],
                               world_path: Optional[str] = None) -> Dict:
    """
    Funkcja pomocnicza do konwersji pojedynczego obrazu
    
    Args:
        bc_resource_path: Ścieżka do obrazu w formacie BC
        pos: Pozycja (x, y, z)
        world_path: Opcjonalna ścieżka do folderu mapy
        
    Returns:
        Dane NBT dla IP
    """
    # Wyciągnij nazwę pliku
    filename = bc_resource_path.split("/")[-1].replace(".png", "").replace(".jpg", "")
    
    # Wyciągnij rozmiar z nazwy
    match = re.search(r'(\d+)x(\d+)', filename)
    if match:
        width_px, height_px = int(match.group(1)), int(match.group(2))
    else:
        width_px, height_px = 16, 16
    
    width_blocks = max(1, width_px // 16)
    height_blocks = max(1, height_px // 16)
    
    # Sanitize nazwy
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', filename).lower()
    
    return {
        "id": "immersive_paintings:painting",
        "x": pos[0],
        "y": pos[1],
        "z": pos[2],
        "Motive": f"immersive_paintings:bc_{safe_name}",
        "Frame": "immersive_paintings:classic",
        "Material": "immersive_paintings:wood",
        "width": width_blocks,
        "height": height_blocks,
        "original_bc": bc_resource_path
    }


# ============================================================================
# TESTOWANIE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Image Converter (BC -> Immersive Paintings)")
    print("=" * 60)
    
    # Test 1: Ekstrakcja rozmiaru z nazwy
    print("\n--- Test 1: Ekstrakcja rozmiaru ---")
    test_names = [
        "sunset_16x16.png",
        "landscape_32x64.png",
        "portrait_16x32.jpg",
        "custom_painting.png",
    ]
    
    scanner = BCImageScanner("/fake/path")
    for name in test_names:
        width, height = scanner._extract_size_from_filename(name)
        print(f"  {name} -> {width}x{height}px ({width//16}x{height//16} bloków)")
    
    # Test 2: Rejestracja obrazu
    print("\n--- Test 2: Rejestracja obrazu ---")
    registry = IPImageRegistry()
    
    test_image = BCImageInfo(
        original_path="/world/bibliocraft/paintings/sunset_32x32.png",
        relative_path="bibliocraft/paintings/sunset_32x32.png",
        filename="sunset_32x32.png",
        width_px=32,
        height_px=32,
        width_blocks=2,
        height_blocks=2
    )
    
    reg = registry.register_image(test_image)
    print(f"  Rejestracja: {reg.original_bc_path}")
    print(f"  IP ID: {reg.ip_identifier}")
    print(f"  Rozmiar: {reg.width_blocks}x{reg.height_blocks} bloków")
    print(f"  Hash: {reg.image_hash}")
    
    # Test 3: Generowanie NBT
    print("\n--- Test 3: Generowanie NBT ---")
    nbt = registry.generate_nbt_for_painting(
        "bibliocraft:paintings/sunset_32x32.png",
        (100, 65, 200),
        "north"
    )
    if nbt:
        print(f"  NBT: {json.dumps(nbt, indent=2)}")
    
    # Test 4: Dostosowanie rozmiaru
    print("\n--- Test 4: Dostosowanie rozmiaru ---")
    test_sizes = [
        (1, 1), (2, 2), (3, 3), (5, 5), (10, 10)
    ]
    for w, h in test_sizes:
        adjusted = registry._adjust_size(w, h)
        print(f"  {w}x{h} -> {adjusted[0]}x{adjusted[1]}")
    
    print("\n" + "=" * 60)
    print("Test zakończony!")
    print("=" * 60)
