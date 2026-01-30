# run.py
import argparse
from core import open_world, pick_dim
from ae2_handlers import (
    scan_cells_in_chunk, place_cell,
    scan_fluix_cables_in_chunk, place_fluix_cable
)
from dump_te import dump_tile_entities_json, dump_tile_entities_json_many

def parse_chunk(arg):
    """cx,cz -> (cx, cz)"""
    try:
        cx, cz = map(int, arg.split(","))
        return (cx, cz)
    except Exception:
        raise ValueError("Nieprawidłowy format --chunk/--dump-chunk. Użyj np. -5,-5")

def parse_range(arg):
    """x1,z1:x2,z2 -> lista (cx,cz) włącznie"""
    try:
        a, b = arg.split(":")
        x1, z1 = map(int, a.split(","))
        x2, z2 = map(int, b.split(","))
        lx, gx = sorted((x1, x2))
        lz, gz = sorted((z1, z2))
        return [(cx, cz) for cx in range(lx, gx + 1) for cz in range(lz, gz + 1)]
    except Exception:
        raise ValueError("Nieprawidłowy format --range. Użyj np. 0,0:5,5")

def main():
    ap = argparse.ArgumentParser("mini AE2 converter: cell + fluix cable + TE dump")
    ap.add_argument("--old", required=True, help="Świat 1.7.10 (przed DFU)")
    ap.add_argument("--new", required=True, help="Świat 1.18 (po DFU)")
    ap.add_argument("--dim", default="minecraft:overworld")

    # KONWERSJA (albo cały świat, albo jeden chunk)
    ap.add_argument("--chunk", help="KONWERSJA: pojedynczy chunk cx,cz (np. -5,-5). Brak = cały świat.")
    ap.add_argument("--dry-run", action="store_true", help="KONWERSJA: bez zapisu")

    # DUMP TE → JSON (działa niezależnie od konwersji i kończy program)
    ap.add_argument("--dump-te-json", help="ŚCIEŻKA do pliku JSON z dumpem TE (uruchamia tylko dump, bez konwersji)")
    ap.add_argument("--dump-save", choices=["old", "new"], default="old",
                    help="Z którego save robić dump (domyślnie: old)")
    ap.add_argument("--dump-chunk", help="DUMP: pojedynczy chunk cx,cz (np. -5,-5)")
    ap.add_argument("--range", help="DUMP: zakres chunków x1,z1:x2,z2 (włącznie). Tylko dla dumpu!")

    args = ap.parse_args()

    # --- ŚCIEŻKA DUMP (niezależna od konwersji) ---
    if args.dump_te_json:
        # wybór świata do dumpu
        dump_world_path = args.old if args.dump_save == "old" else args.new
        world = open_world(dump_world_path)
        try:
            dim_key = pick_dim(world.level_wrapper, args.dim)

            if args.range:
                chunks = parse_range(args.range)
                total = dump_tile_entities_json_many(world, dim_key, chunks, args.dump_te_json)
                print(f"[DUMP] zapisano łącznie {total} TE do {args.dump_te_json} (chunki={len(chunks)}, save={args.dump_save})")
                return
            else:
                # pojedynczy chunk do dumpu: --dump-chunk lub fallback pierwszy istniejący
                if args.dump_chunk:
                    cx, cz = parse_chunk(args.dump_chunk)
                else:
                    # pierwszy chunk z save (na wszelki wypadek)
                    coords = list(world.all_chunk_coords(dim_key))
                    if not coords:
                        print("[DUMP] brak chunków w wybranym save.")
                        return
                    cx, cz = coords[0]
                count = dump_tile_entities_json(world, dim_key, (cx, cz), args.dump_te_json)
                print(f"[DUMP] zapisano {count} TE do {args.dump_te_json} (chunk=({cx},{cz}), save={args.dump_save})")
                return
        finally:
            try: world.close()
            except: pass

    # --- ŚCIEŻKA KONWERSJI (bez range!) ---
    if args.range:
        raise SystemExit("BŁĄD: --range jest dozwolone tylko dla dumpu, nie dla konwersji.")

    old = open_world(args.old)
    new = open_world(args.new)
    try:
        dim_old = pick_dim(old.level_wrapper, args.dim)
        dim_new = pick_dim(new.level_wrapper, args.dim)

        # konwersja: jeden chunk albo cały świat
        if args.chunk:
            coord_list = [parse_chunk(args.chunk)]
        else:
            coord_list = list(old.all_chunk_coords(dim_old))

        found_cells = found_cables = placed = 0

        for cx, cz in coord_list:
            cells = scan_cells_in_chunk(old, dim_old, cx, cz)
            cables = scan_fluix_cables_in_chunk(old, dim_old, cx, cz)
            found_cells += len(cells)
            found_cables += len(cables)

            if args.dry_run:
                for t in cells:  print("[DRY] cell  @", t["pos"])
                for t in cables: print("[DRY] cable @", t["pos"])
                continue

            for t in cells:
                place_cell(new, dim_new, t); placed += 1
            for t in cables:
                place_fluix_cable(new, dim_new, t); placed += 1

        if not args.dry_run:
            print("[INFO] save()")
            new.save()

        scope = "chunk" if args.chunk else "whole-world"
        print(f"[SUMMARY] scope={scope}, cells={found_cells}, cables={found_cables}, placed={placed}, dry={args.dry_run}")
    finally:
        try: old.close()
        except: pass
        try: new.close()
        except: pass

if __name__ == "__main__":
    main()
