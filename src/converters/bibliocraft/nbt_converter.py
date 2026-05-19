"""
Konwerter NBT BiblioCraft 1.7.10 -> 1.18.2

Ten moduł zawiera właściwą implementację konwersji NBT między wersjami:
- Odczyt NBT z formatu BC 1.7.10
- Konwersja do formatu 1.18.2 (Supplementaries, FramedBlocks, ImmersivePaintings)
- Zapis w formacie NBT 1.18.2
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import json


@dataclass
class ConvertedBlock:
    """Reprezentuje przekonwertowany blok z metadanymi"""
    x: int
    y: int
    z: int
    block_id: str  # Nowe ID w 1.18.2
    block_state: Dict[str, Any] = field(default_factory=dict)
    tile_entity: Optional[Dict] = None
    conversion_notes: List[str] = field(default_factory=list)
    
    def add_note(self, note: str):
        """Dodaje notatkę o konwersji"""
        self.conversion_notes.append(note)


class BC1170NBTReader:
    """
    Czytnik NBT z formatu BiblioCraft 1.7.10
    
    Format NBT w 1.7.10:
    - ID bloków: String (nie numeryczne dla modów)
    - Metadata: int (0-15)
    - TileEntity: CompoundTag z danymi
    """
    
    # Mapowanie ID bloków BC 1.7.10 na ID 1.18.2
    BLOCK_ID_MAP = {
        # Bloki podstawowe
        "BiblioCraft:Bookcase": "supplementaries:book_pile",
        "BiblioCraft:ArmorStand": "minecraft:air",  # Encja w 1.18.2 — blok usuwany, dane do spawnu encji w tile_entity
        "BiblioCraft:WeaponCase": "supplementaries:pedestal",
        "BiblioCraft:PotionShelf": "supplementaries:item_shelf",
        "BiblioCraft:WeaponRack": "supplementaries:item_shelf",
        "BiblioCraft:GenericShelf": "supplementaries:item_shelf",
        "BiblioCraft:Label": "supplementaries:sign_post",  # Alternatywa
        "BiblioCraft:WritingDesk": "minecraft:oak_planks",  # Brak odpowiednika
        "BiblioCraft:TypeMachine": "minecraft:oak_planks",      # Brak funkcji (alias historyczny)
        "BiblioCraft:Typewriter": "minecraft:oak_planks",       # Poprawna nazwa bloku w BC source
        "BiblioCraft:TypesettingTable": "minecraft:oak_planks", # Osobny blok BC (stół składu)
        "BiblioCraft:PrintPress": "minecraft:oak_planks",   # Brak funkcji
        "BiblioCraft:Table": "supplementaries:pedestal",
        "BiblioCraft:Seat": "minecraft:oak_stairs",  # Alternatywa
        "BiblioCraft:Lantern": "supplementaries:wall_lantern",
        "BiblioCraft:Lamp": "supplementaries:end_stone_lamp",
        "BiblioCraft:CookieJar": "supplementaries:jar",
        "BiblioCraft:DinnerPlate": "supplementaries:pedestal",
        "BiblioCraft:DiscRack": "minecraft:jukebox",
        "BiblioCraft:MapFrame": "supplementaries:timber_frame",  # Brak odpowiednika funkcjonalnego; dane mapy utracone
        "BiblioCraft:FancySign": "supplementaries:hanging_sign_oak",
        "BiblioCraft:FancyWorkbench": "minecraft:crafting_table",
        "BiblioCraft:SwordPedestal": "supplementaries:pedestal",
        "BiblioCraft:FramedChest": "framedblocks:framed_chest",
        "BiblioCraft:FurniturePaneler": "minecraft:oak_planks",  # Brak funkcji
        "BiblioCraft:Clock": "supplementaries:clock_block",
        "BiblioCraft:Painting": "immersive_paintings:painting",
        "BiblioCraft:PaintPress": "minecraft:oak_planks",  # Brak funkcji
        "BiblioCraft:Bell": "minecraft:bell",
        "BiblioCraft:Clipboard": "supplementaries:notice_board",
        # Framed variants (meble z teksturami)
        "BiblioCraft:FramedBookcase": "framedblocks:framed_block",
        "BiblioCraft:FramedShelf": "framedblocks:framed_slab",
        "BiblioCraft:FramedLabel": "framedblocks:framed_panel",
        "BiblioCraft:FramedTable": "framedblocks:framed_block",
        "BiblioCraft:FramedDesk": "framedblocks:framed_block",
        "BiblioCraft:FramedSeat": "framedblocks:framed_slab",
        "BiblioCraft:FramedSign": "framedblocks:framed_sign",
        "BiblioCraft:FramedDoor": "framedblocks:framed_door",
        "BiblioCraft:FramedTrapDoor": "framedblocks:framed_trapdoor",
        "BiblioCraft:FramedFence": "framedblocks:framed_fence",
        "BiblioCraft:FramedGate": "framedblocks:framed_gate",
        # Mapowania po rzeczywistym ID TileEntity z plików MCA 1.7.10
        "BookcaseTile": "supplementaries:book_pile",
        "GenericShelfTile": "supplementaries:item_shelf",
        "PotionShelfTile": "supplementaries:item_shelf",
        "ToolRackTile": "supplementaries:item_shelf",
        "WeaponCaseTile": "supplementaries:pedestal",
        "SwordPedestalTile": "supplementaries:pedestal",
        "TableTile": "supplementaries:pedestal",
        "seatTile": "minecraft:oak_stairs",
        "CookieJarTile": "supplementaries:jar",
        "dinnerPlateTile": "supplementaries:pedestal",
        "DiscRackTile": "minecraft:jukebox",
        "MapFrameTile": "supplementaries:timber_frame",
        "fancySignTile": "supplementaries:hanging_sign_oak",
        "WritingDeskTile": "minecraft:oak_planks",
        "biblioBellTile": "minecraft:bell",
        "biblioClipboardTile": "supplementaries:notice_board",
        "biblioTypewriterTile": "minecraft:oak_planks",
        "PrintPressTile": "minecraft:oak_planks",
        "biblioPaintingTile": "immersive_paintings:painting",
        "biblioPaintPressTile": "minecraft:oak_planks",
        "ArmorStandTile": "minecraft:air",
        "biblioClockTile": "supplementaries:clock_block",
        "LanternTile": "supplementaries:wall_lantern",
        "LampTile": "supplementaries:end_stone_lamp",
        "WoodLabelTile": "supplementaries:sign_post",
        "FramedChestTile": "framedblocks:framed_chest",
    }
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def read_tile_entity(self, nbt_data: Dict) -> Dict:
        """
        Odczytuje TileEntity z NBT BC 1.7.10
        
        Args:
            nbt_data: Słownik z danymi NBT
            
        Returns:
            Słownik z przetworzonymi danymi TE
        """
        result = {
            "id": nbt_data.get("id", ""),
            "x": nbt_data.get("x", 0),
            "y": nbt_data.get("y", 0),
            "z": nbt_data.get("z", 0),
            "raw": nbt_data
        }
        
        # Odczytaj specyficzne pola w zależności od typu
        te_id = result["id"]
        
        if "Bookcase" in te_id:
            result["items"] = self._read_items(nbt_data.get("Items", []))
            result["book_count"] = nbt_data.get("bookCount", 0)
            
        elif "ArmorStand" in te_id:
            result["armor_items"] = self._read_items(nbt_data.get("armorItems", []))
            
        elif "Shelf" in te_id or "WeaponRack" in te_id or "ToolRack" in te_id:
            result["items"] = self._read_items(nbt_data.get("Items", nbt_data.get("shelfItems", [])))
            
        elif "FancySign" in te_id or "fancySign" in te_id:
            result["sign_text"] = nbt_data.get("signText", "")
            result["text_scale"] = nbt_data.get("textScale", 1.0)
            
        elif "Clock" in te_id:
            result["hour"] = nbt_data.get("hour", 0)
            result["minute"] = nbt_data.get("minute", 0)
            
        elif "FramedChest" in te_id:
            result["frame_texture"] = nbt_data.get("frameTexture", "")
            result["items"] = self._read_items(nbt_data.get("Items", []))
            
        elif "Label" in te_id:
            result["items"] = self._read_items(nbt_data.get("Items", []))
            result["text"] = nbt_data.get("text", "")

        elif "Clipboard" in te_id:
            result["text"] = nbt_data.get("text", "")
            result["title"] = nbt_data.get("title", "")

        elif "DiscRack" in te_id:
            result["items"] = self._read_items(nbt_data.get("Items", []))

        elif "Painting" in te_id:
            result["resource_location"] = nbt_data.get("resourceLocation", "")
            result["painting_type"] = nbt_data.get("paintingType", "custom")
            
        return result
    
    def _read_items(self, items_list: List[Dict]) -> List[Dict]:
        """Odczytuje listę itemów z NBT"""
        return [self._read_item(item) for item in items_list if item]
    
    def _read_item(self, item_data: Dict) -> Dict:
        """Odczytuje pojedynczy item z NBT"""
        if not item_data:
            return {"id": "", "Count": 0}
        return {
            "id": item_data.get("id", ""),
            "Count": item_data.get("Count", 1),
            "Damage": item_data.get("Damage", 0),
            "tag": item_data.get("tag", {})
        }
    
    def get_target_block_id(self, bc_block_id: str) -> str:
        """Zwraca docelowe ID bloku dla BC"""
        return self.BLOCK_ID_MAP.get(bc_block_id, "minecraft:stone")


class BC1182NBTWriter:
    """
    Zapisuje NBT w formacie 1.18.2
    
    Format 1.18.2:
    - BlockState z Properties
    - TileEntity zgodne z nowymi modami
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def write_supplementaries_book_pile(self, bc_data: Dict, pos: Tuple[int, int, int]) -> Dict:
        """
        Zapisuje Book Pile z Supplementaries
        
        BC Bookcase (16 slotów) -> Supplementaries Book Pile (4 sloty)
        """
        items = bc_data.get("items", [])[:4]  # Tylko 4 pierwsze książki
        
        nbt = {
            "id": "supplementaries:book_pile",
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "horizontal": False,
            "Items": self._write_items_with_slots(items[:4])
        }
        
        return nbt
    
    def write_supplementaries_item_shelf(self, bc_data: Dict, pos: Tuple[int, int, int]) -> Dict:
        """
        Zapisuje Item Shelf z Supplementaries
        
        BC Shelf/WeaponRack (4 sloty) -> Item Shelf (4 sloty)
        """
        items = bc_data.get("items", [])
        
        nbt = {
            "id": "supplementaries:item_shelf",
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "Items": self._write_items_with_slots(items[:4])
        }
        
        return nbt
    
    def write_supplementaries_jar(self, bc_data: Dict, pos: Tuple[int, int, int]) -> Dict:
        """
        Zapisuje Jar z Supplementaries
        
        BC Cookie Jar -> Jar
        """
        items = bc_data.get("items", [])
        
        nbt = {
            "id": "supplementaries:jar",
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "Items": self._write_items_with_slots(items[:4])
        }
        
        return nbt
    
    def write_supplementaries_pedestal(self, bc_data: Dict, pos: Tuple[int, int, int]) -> Dict:
        """
        Zapisuje Pedestal z Supplementaries
        
        BC WeaponCase/SwordPedestal/Table -> Pedestal
        """
        items = bc_data.get("items", [])
        
        nbt = {
            "id": "supplementaries:pedestal",
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "Items": self._write_items_with_slots(items[:1])  # Pedestal ma 1 slot
        }
        
        return nbt
    
    def write_framed_block(self, bc_data: Dict, pos: Tuple[int, int, int], 
                          shape: str, bc_texture: str = "") -> Dict:
        """
        Zapisuje FramedBlock z FramedBlocks
        
        BC Framed* -> FramedBlocks
        """
        # Konwertuj teksturę BC na camo_state
        camo_state = self._convert_bc_texture_to_camo_state(bc_texture)
        camo_stack = self._create_camo_stack(bc_texture)
        
        nbt = {
            "id": "framedblocks:framed_block",
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "shape": shape,
            "camo_state": camo_state,
            "camo_stack": camo_stack,
            "glowing": False,
            "intangible": False,
            "reinforced": False
        }
        
        # Dodaj inventory dla skrzyń
        if "chest" in shape.lower():
            items = bc_data.get("items", [])
            nbt["Items"] = self._write_items_with_slots(items[:27])  # Skrzynia 3x9
        
        return nbt
    
    def write_immersive_painting(self, bc_data: Dict, pos: Tuple[int, int, int]) -> Dict:
        """
        Zapisuje Painting z Immersive Paintings
        
        BC Painting -> Immersive Painting
        """
        resource_loc = bc_data.get("resource_location", "")
        
        # Wydobyć nazwę z resourceLocation
        image_name = resource_loc.split("/")[-1].replace(".png", "") if resource_loc else "unknown"
        ip_motive = f"immersive_paintings:bc_{image_name}"
        
        nbt = {
            "id": "immersive_paintings:painting",
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "Motive": ip_motive,
            "Frame": "immersive_paintings:classic",
            "Material": "immersive_paintings:wood",
            "Facing": "north",  # Domyślnie, do odczytania z block state
            "Rotation": 0
        }
        
        return nbt
    
    def write_vanilla_armor_stand(self, bc_data: Dict, pos: Tuple[int, int, int]) -> Dict:
        """
        Zapisuje Armor Stand z vanilla
        
        BC Armor Stand -> Vanilla Armor Stand (encja, nie blok!)
        To wymaga specjalnej obsługi - armor stand to encja w 1.18.2
        """
        armor_items = bc_data.get("armor_items", [])
        
        nbt = {
            "id": "minecraft:armor_stand",
            "Pos": [pos[0] + 0.5, pos[1], pos[2] + 0.5],
            "ArmorItems": self._write_items_for_entity(armor_items),
            "ShowArms": True,
            "NoBasePlate": False
        }
        
        return nbt
    
    def write_sign_post_label(self, bc_data: Dict, pos: Tuple[int, int, int]) -> Dict:
        """
        Zapisuje Label z BC jako SignPost z Supplementaries.

        BC Label (3 display items + text) -> supplementaries:sign_post (tekst).
        Przedmioty są tracone — sign_post nie przechowuje itemów w NBT.
        """
        text = bc_data.get("text", "")
        return {
            "id": "supplementaries:sign_post",
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "Text": f'{{"text":"{text}"}}',
        }

    def write_notice_board(self, bc_data: Dict, pos: Tuple[int, int, int]) -> Dict:
        """
        Zapisuje Clipboard z BC jako NoticeBoard z Supplementaries.

        BC Clipboard (tekst notatki) -> supplementaries:notice_board.
        """
        text = bc_data.get("text", "")
        title = bc_data.get("title", "")
        return {
            "id": "supplementaries:notice_board",
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "Text": text,
            "Title": title,
        }

    def write_jukebox_disc(self, bc_data: Dict, pos: Tuple[int, int, int]) -> Dict:
        """
        Zapisuje DiscRack z BC jako Jukebox vanilla.

        BC DiscRack (9 dysków) -> minecraft:jukebox (1 slot).
        Tylko pierwsza płyta jest zachowana; pozostałe są tracone.
        """
        items = bc_data.get("items", [])
        nbt = {
            "id": "minecraft:jukebox",
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "IsPlaying": False,
        }
        first = next((i for i in items if i and i.get("id")), None)
        if first:
            nbt["RecordItem"] = {
                "id": self._convert_item_id(first["id"]),
                "Count": 1,
            }
        return nbt

    def _write_items_with_slots(self, items: List[Dict]) -> List[Dict]:
        """Zapisuje itemy z polami Slot dla BlockEntity"""
        result = []
        for slot, item in enumerate(items):
            if item and item.get("id"):
                item_nbt = {
                    "id": self._convert_item_id(item.get("id", "")),
                    "Count": item.get("Count", 1),
                    "Slot": slot
                }
                # Dodaj tag jeśli istnieje
                tag = item.get("tag", {})
                if tag:
                    item_nbt["tag"] = tag
                result.append(item_nbt)
        return result
    
    def _write_items_for_entity(self, items: List[Dict]) -> List[Dict]:
        """Zapisuje itemy dla encji (armor stand)"""
        # ArmorItems: [feet, legs, chest, head]
        result = [{}, {}, {}, {}]
        for i, item in enumerate(items):
            if i < 4 and item and item.get("id"):
                result[i] = {
                    "id": self._convert_item_id(item.get("id", "")),
                    "Count": item.get("Count", 1)
                }
        return result
    
    def _convert_item_id(self, item_id_1710: str) -> str:
        """Konwertuje ID itemu z 1.7.10 na 1.18.2"""
        # Mapowanie podstawowe
        item_map = {
            # Dodaj mapowania itemów jeśli potrzebne
        }
        
        # Usuń prefiks minecraft: jeśli już jest
        if ":" not in item_id_1710 and item_id_1710:
            return f"minecraft:{item_id_1710.lower()}"
        return item_id_1710
    
    def write_simple_block(self, bc_data: Dict, pos: Tuple[int, int, int], target_id: str) -> Dict:
        """
        Zapisuje blok bez złożonych danych NBT — tylko pozycja i ID.
        Używane dla bloków, których stan nie wymaga migracji danych (Clock, Lantern, itp.)
        """
        return {
            "id": target_id,
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
        }

    def _convert_bc_texture_to_camo_state(self, bc_texture: str) -> Dict:
        """Konwertuje teksturę BC na camo_state FramedBlocks"""
        if not bc_texture:
            return {"Name": "minecraft:oak_planks", "Properties": {}}
        
        # Mapowanie tekstur
        texture_map = {
            "minecraft:planks:0": "minecraft:oak_planks",
            "minecraft:planks:1": "minecraft:spruce_planks",
            "minecraft:planks:2": "minecraft:birch_planks",
            "minecraft:planks:3": "minecraft:jungle_planks",
            "minecraft:planks:4": "minecraft:acacia_planks",
            "minecraft:planks:5": "minecraft:dark_oak_planks",
            "minecraft:log": "minecraft:oak_log",
            "minecraft:log:0": "minecraft:oak_log",
            "minecraft:log:1": "minecraft:spruce_log",
            "minecraft:log:2": "minecraft:birch_log",
            "minecraft:log:3": "minecraft:jungle_log",
            "minecraft:log2": "minecraft:acacia_log",
            "minecraft:log2:0": "minecraft:acacia_log",
            "minecraft:log2:1": "minecraft:dark_oak_log",
        }
        
        block_id = texture_map.get(bc_texture, bc_texture)
        
        # Upewnij się że ID jest w formacie minecraft:xxx
        if ":" not in block_id:
            block_id = f"minecraft:{block_id}"
        
        return {"Name": block_id, "Properties": {}}
    
    def _create_camo_stack(self, bc_texture: str) -> Dict:
        """Tworzy camo_stack dla FramedBlocks"""
        if not bc_texture:
            return {}
        
        block_id = self._convert_bc_texture_to_camo_state(bc_texture)["Name"]
        
        return {
            "id": block_id,
            "Count": 1
        }


class BiblioCraftNBTConverter:
    """
    Główny konwerter NBT BiblioCraft 1.7.10 -> 1.18.2
    
    Koordynuje proces konwersji między readerem a writerem.
    """
    
    # Mapowanie rzeczywistych TE IDs z MCA 1.7.10 na metody writer
    CONVERSION_MAP = {
        "BookcaseTile":        ("supplementaries",      "write_supplementaries_book_pile"),
        "GenericShelfTile":    ("supplementaries",      "write_supplementaries_item_shelf"),
        "PotionShelfTile":     ("supplementaries",      "write_supplementaries_item_shelf"),
        "ToolRackTile":        ("supplementaries",      "write_supplementaries_item_shelf"),
        "WeaponCaseTile":      ("supplementaries",      "write_supplementaries_pedestal"),
        "SwordPedestalTile":   ("supplementaries",      "write_supplementaries_pedestal"),
        "TableTile":           ("supplementaries",      "write_supplementaries_pedestal"),
        "CookieJarTile":       ("supplementaries",      "write_supplementaries_jar"),
        "dinnerPlateTile":     ("supplementaries",      "write_supplementaries_pedestal"),
        "FramedChestTile":     ("framedblocks",         "write_framed_block", "framed_chest"),
        "ArmorStandTile":      ("vanilla_entity",       "write_vanilla_armor_stand"),
        "biblioPaintingTile":  ("immersive_paintings",  "write_immersive_painting"),
        "WoodLabelTile":       ("supplementaries",      "write_sign_post_label"),
        "biblioClipboardTile": ("supplementaries",      "write_notice_board"),
        "DiscRackTile":        ("supplementaries",      "write_jukebox_disc"),
        "biblioClockTile":     ("supplementaries",      "write_simple_block", "supplementaries:clock_block"),
        "fancySignTile":       ("supplementaries",      "write_simple_block", "supplementaries:hanging_sign_oak"),
        "MapFrameTile":        ("supplementaries",      "write_simple_block", "supplementaries:timber_frame"),
        "LanternTile":         ("supplementaries",      "write_simple_block", "supplementaries:wall_lantern"),
        "LampTile":            ("supplementaries",      "write_simple_block", "supplementaries:end_stone_lamp"),
    }
    
    def __init__(self):
        self.reader = BC1170NBTReader()
        self.writer = BC1182NBTWriter()
        self.stats = {
            "converted": 0,
            "skipped": 0,
            "errors": 0
        }
    
    def convert_tile_entity(self, nbt_1710: Dict, block_id: str, 
                           pos: Tuple[int, int, int]) -> Optional[ConvertedBlock]:
        """
        Konwertuje TileEntity z BC 1.7.10 na 1.18.2
        
        Args:
            nbt_1710: Dane NBT z BC 1.7.10
            block_id: ID bloku BC
            pos: Pozycja (x, y, z)
            
        Returns:
            ConvertedBlock lub None jeśli konwersja niemożliwa
        """
        # Odczytaj dane BC
        bc_data = self.reader.read_tile_entity(nbt_1710)
        te_id = bc_data.get("id", "")
        
        # Znajdź metodę konwersji
        conversion_info = self.CONVERSION_MAP.get(te_id)
        
        if not conversion_info:
            self.stats["skipped"] += 1
            return None
        
        try:
            # Wykonaj konwersję
            result = self._execute_conversion(conversion_info, bc_data, pos, block_id)
            self.stats["converted"] += 1
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            return ConvertedBlock(
                x=pos[0], y=pos[1], z=pos[2],
                block_id="minecraft:stone",
                conversion_notes=[f"Błąd konwersji: {str(e)}"]
            )
    
    def _execute_conversion(self, conversion_info: tuple, bc_data: Dict, 
                           pos: Tuple[int, int, int], block_id: str) -> ConvertedBlock:
        """Wykonuje konkretną konwersję"""
        mod_type = conversion_info[0]
        method_name = conversion_info[1]
        extra_args = conversion_info[2:] if len(conversion_info) > 2 else ()
        
        # Pobierz metodę
        method = getattr(self.writer, method_name)
        
        # Przygotuj argumenty
        args = [bc_data, pos]
        if extra_args:
            args.extend(extra_args)
        
        # Wywołaj metodę
        new_nbt = method(*args)
        
        # Utwórz ConvertedBlock
        target_block_id = self.reader.get_target_block_id(block_id)
        
        notes = []
        te_id = bc_data.get("id", "")
        if "Bookcase" in te_id:
            book_count = bc_data.get("book_count", 0)
            if book_count > 4:
                notes.append(f"UWAGA: Tylko 4 z {book_count} książek zmieściły się")
        elif "MapFrame" in te_id:
            notes.append("STRATA DANYCH: Dane mapy utracone — brak odpowiednika funkcjonalnego w 1.18.2. Zamieniono na supplementaries:timber_frame")
        elif "Label" in te_id:
            item_count = len(bc_data.get("items", []))
            if item_count:
                notes.append(f"STRATA DANYCH: {item_count} przedmiot(ów) z Label utracono — supplementaries:sign_post nie przechowuje itemów")
        elif "DiscRack" in te_id:
            disc_count = len([i for i in bc_data.get("items", []) if i and i.get("id")])
            if disc_count > 1:
                notes.append(f"STRATA DANYCH: Tylko 1 z {disc_count} płyt zmieściła się w jukebox")
        elif "ArmorStand" in te_id:
            notes.append("ENCJA: Armor Stand to encja w 1.18.2 — blok usunięty (minecraft:air), dane zbroi w tile_entity do spawnu encji osobnym narzędziem")
        
        return ConvertedBlock(
            x=pos[0],
            y=pos[1],
            z=pos[2],
            block_id=target_block_id,
            tile_entity=new_nbt,
            conversion_notes=notes
        )
    
    def get_stats(self) -> Dict:
        """Zwraca statystyki konwersji"""
        return self.stats.copy()


def convert_bc_nbt_to_1182(nbt_1710: Dict, block_id: str, 
                           pos: Tuple[int, int, int]) -> Optional[ConvertedBlock]:
    """
    Funkcja pomocnicza do konwersji NBT
    
    Args:
        nbt_1710: Dane NBT z BC 1.7.10
        block_id: ID bloku BC (np. "BiblioCraft:Bookcase")
        pos: Pozycja (x, y, z)
        
    Returns:
        ConvertedBlock lub None
    """
    converter = BiblioCraftNBTConverter()
    return converter.convert_tile_entity(nbt_1710, block_id, pos)


# Przykład użycia i testowanie
if __name__ == "__main__":
    print("=" * 60)
    print("TEST: BiblioCraft NBT Converter (1.7.10 -> 1.18.2)")
    print("=" * 60)
    
    converter = BiblioCraftNBTConverter()
    
    # Test 1: Bookcase
    print("\n--- Test 1: Bookcase -> Book Pile ---")
    bookcase_nbt = {
        "id": "TileEntityBookcase",
        "x": 100, "y": 64, "z": 200,
        "Items": [
            {"id": "minecraft:book", "Count": 1},
            {"id": "minecraft:book", "Count": 1},
            {"id": "minecraft:enchanted_book", "Count": 1, "tag": {"StoredEnchantments": [{"id": "mending"}]}},
        ],
        "bookCount": 3
    }
    
    result = converter.convert_tile_entity(
        bookcase_nbt, 
        "BiblioCraft:Bookcase", 
        (100, 64, 200)
    )
    
    if result:
        print(f"  Konwersja: Bookcase -> {result.block_id}")
        print(f"  NBT: {json.dumps(result.tile_entity, indent=2)}")
        if result.conversion_notes:
            print(f"  Uwagi: {result.conversion_notes}")
    
    # Test 2: Framed Chest
    print("\n--- Test 2: FramedChest -> FramedBlocks ---")
    chest_nbt = {
        "id": "TileEntityFramedChest",
        "x": 101, "y": 64, "z": 200,
        "frameTexture": "minecraft:planks:0",
        "Items": [{"id": "minecraft:diamond", "Count": 5}]
    }
    
    result = converter.convert_tile_entity(
        chest_nbt,
        "BiblioCraft:FramedChest",
        (101, 64, 200)
    )
    
    if result:
        print(f"  Konwersja: FramedChest -> {result.block_id}")
        print(f"  NBT: {json.dumps(result.tile_entity, indent=2)}")
    
    # Test 3: Painting
    print("\n--- Test 3: Painting -> ImmersivePaintings ---")
    painting_nbt = {
        "id": "TileEntityPainting",
        "x": 102, "y": 65, "z": 200,
        "resourceLocation": "bibliocraft:paintings/custom/sunset_32x32.png",
        "paintingType": "custom"
    }
    
    result = converter.convert_tile_entity(
        painting_nbt,
        "BiblioCraft:Painting",
        (102, 65, 200)
    )
    
    if result:
        print(f"  Konwersja: Painting -> {result.block_id}")
        print(f"  NBT: {json.dumps(result.tile_entity, indent=2)}")
    
    # Statystyki
    print("\n--- Statystyki ---")
    stats = converter.get_stats()
    print(f"  Przekonwertowano: {stats['converted']}")
    print(f"  Pominięto: {stats['skipped']}")
    print(f"  Błędy: {stats['errors']}")
    
    print("\n" + "=" * 60)
    print("Test zakończony!")
    print("=" * 60)
