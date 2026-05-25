import sys
from pathlib import Path
sys.path.insert(0, 'src')
from minecraft_map_parser.anvil_parser import AnvilParser

files = sorted(Path('mapa_1710/region').glob('*.mca'))
print(f"Total: {len(files)} files")
for i, f in enumerate(files, 1):
    print(f"[{i}/{len(files)}] {f.name} ...", flush=True)
    try:
        parser = AnvilParser(str(f))
        chunks = parser.get_all_chunks()
        rc_count = 0
        for chunk in chunks:
            for te in chunk.get_tile_entities():
                te_id = te.get('id', '')
                if te_id and ('RC' in te_id or 'railcraft' in te_id.lower()):
                    rc_count += 1
        print(f"  -> {len(chunks)} chunks, {rc_count} RC TE", flush=True)
    except Exception as e:
        print(f"  -> ERROR: {e}", flush=True)
print("DONE", flush=True)
