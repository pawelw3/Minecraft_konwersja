"""
Skrypt konwersji testowej mapy ForgeMultipart (Zadanie 5A).

Odczytuje testową mapę 1.7.10, znajduje TileEntity savedMultipart,
wywołuje ForgeMultipartConverter i zapisuje eventy konwersji.
"""
import copy
import json
import sys
from pathlib import Path

# Dodaj src/ do path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from minecraft_map_parser.anvil_parser import AnvilParser
from minecraft_map_parser.nbt_parser import NBTTag

from converters.forge_multipart.forge_multipart_converter import ForgeMultipartConverter


def nbt_to_python(obj):
    """Rekurencyjnie konwertuje NBT na zwykłe typy Pythona."""
    if isinstance(obj, NBTTag):
        return nbt_to_python(obj.value)
    if isinstance(obj, list):
        return [nbt_to_python(x) for x in obj]
    if isinstance(obj, dict):
        return {k: nbt_to_python(v) for k, v in obj.items()}
    return obj


def get_block_id_from_chunk(chunk_data, x, y, z):
    """Odczytuje block ID z chunka na podstawie globalnych współrzędnych."""
    level = chunk_data.nbt.get('Level', {})
    if isinstance(level, NBTTag):
        level = level.value
    sections = level.get('Sections', [])
    if isinstance(sections, NBTTag):
        sections = sections.value

    lx = x & 15
    ly = y & 15
    lz = z & 15
    sec_y = y // 16

    for sec in sections:
        if isinstance(sec, NBTTag):
            sec = sec.value
        if sec.get('Y') == sec_y:
            blocks = sec.get('Blocks', [])
            if isinstance(blocks, NBTTag):
                blocks = blocks.value
            idx = (ly * 16 + lz) * 16 + lx
            bid = blocks[idx]
            if isinstance(bid, NBTTag):
                bid = bid.value
            bid = bid & 0xFF

            add = sec.get('AddBlocks') or sec.get('Add')
            if add:
                if isinstance(add, NBTTag):
                    add = add.value
                add_idx = idx // 2
                add_byte = add[add_idx]
                if isinstance(add_byte, NBTTag):
                    add_byte = add_byte.value
                if idx % 2 == 0:
                    bid += (add_byte & 0x0F) << 8
                else:
                    bid += ((add_byte >> 4) & 0x0F) << 8
            return bid
    return None


def convert_test_world(world_path: str, output_path: str):
    """Konwertuje testową mapę ForgeMultipart."""
    converter = ForgeMultipartConverter()
    events = []
    stats = {"processed": 0, "converted": 0, "failed": 0}

    region_dir = Path(world_path) / "region"
    if not region_dir.exists():
        print(f"Brak katalogu region: {region_dir}")
        return

    for region_file in sorted(region_dir.glob("*.mca")):
        try:
            rf = AnvilParser(str(region_file))
            chunks = rf.get_all_chunks()
            for cd in chunks:
                level = cd.nbt.get('Level', {})
                if isinstance(level, NBTTag):
                    level = level.value
                te_list = level.get('TileEntities', [])
                if isinstance(te_list, NBTTag):
                    te_list = te_list.value

                for te in te_list:
                    if isinstance(te, NBTTag):
                        te = te.value
                    te_id = te.get('id')
                    if isinstance(te_id, NBTTag):
                        te_id = te_id.value
                    if te_id != 'savedMultipart':
                        continue

                    x, y, z = te['x'], te['y'], te['z']
                    if isinstance(x, NBTTag):
                        x, y, z = x.value, y.value, z.value

                    # Odczytaj block ID
                    block_id = get_block_id_from_chunk(cd, x, y, z)

                    # Normalizuj NBT do dict
                    te_dict = nbt_to_python(te)

                    # Użyjemy stringowego block_id dla konwertera
                    # W testowej mapie block ID 256 to ForgeMultipart:block
                    block_id_str = "ForgeMultipart:block"

                    result = converter.convert_block(
                        block_id_1710=block_id_str,
                        metadata=0,
                        nbt_1710=te_dict,
                        position=(x, y, z),
                    )

                    stats["processed"] += 1
                    if result.converted.success:
                        stats["converted"] += 1
                    else:
                        stats["failed"] += 1

                    # Zbuduj event
                    event = {
                        "pos": [x, y, z],
                        "block_id_1710": block_id_str,
                        "block_numeric_id_1710": block_id,
                        "te_id": te_id,
                        "converted": result.converted.success,
                        "block_id_1182": result.converted.block_id_1182,
                        "errors": result.converted.errors,
                        "warnings": result.converted.warnings,
                        "nbt_1182": result.converted.nbt_1182,
                        "parts_original": [p.get("id") for p in te_dict.get("parts", [])],
                        "parts_converted": [p.get("id") for p in (result.converted.nbt_1182 or {}).get("parts", [])] if result.converted.nbt_1182 else [],
                    }
                    events.append(event)
        except Exception as e:
            print(f"Błąd przetwarzania {region_file.name}: {e}")

    # Zapisz wyniki
    output = {
        "stats": stats,
        "converter_stats": converter.stats,
        "events": events,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Konwersja zakończona.")
    print(f"  Przetworzono: {stats['processed']}")
    print(f"  Skonwertowano: {stats['converted']}")
    print(f"  Błędy: {stats['failed']}")
    print(f"  Wynik zapisano: {output_path}")

    return output


if __name__ == "__main__":
    world_path = "test_scenarios/forge_multipart_task5a/1710_test_world"
    output_path = "output/forge_multipart/task5a_conversion_result.json"
    convert_test_world(world_path, output_path)
