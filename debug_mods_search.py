#!/usr/bin/env python3
"""
Debug script to search for mod strings in region files.
"""

import struct
import zlib
from pathlib import Path

# Strings to search for (case insensitive will be checked both ways)
SEARCH_STRINGS = [
    b"betterstorage",
    b"BetterStorage",
    b"better_storage",
    b"EnchantingPlus",
    b"enchantingplus",
    b"eplus",
    b"EnderStorage",
    b"enderstorage",
    b"ender_storage",
    b"Growthcraft",
    b"growthcraft",
    b"grccellar",
    b"grcmilk",
    b"grcbees",
    b"jammy",
    b"Jammy",
    b"furniture",
    b"cfm:",  # MrCrayfish's Furniture Mod prefix
]


def read_region_chunks(filepath):
    """Read all chunks from a region file."""
    chunks = []
    try:
        with open(filepath, 'rb') as f:
            header = f.read(8192)
            if len(header) < 8192:
                return chunks

            for chunk_x in range(32):
                for chunk_z in range(32):
                    idx = chunk_x + chunk_z * 32
                    offset_data = header[idx*4:(idx+1)*4]
                    offset = ((offset_data[0] << 16) | (offset_data[1] << 8) | offset_data[2]) * 4096

                    if offset == 0:
                        continue

                    f.seek(offset)
                    length_bytes = f.read(4)
                    if len(length_bytes) < 4:
                        continue
                    length = struct.unpack('>I', length_bytes)[0]
                    compression = struct.unpack('B', f.read(1))[0]

                    if length > 0 and length < 2*1024*1024:
                        compressed_data = f.read(length - 1)
                        try:
                            if compression == 2:
                                chunk_data = zlib.decompress(compressed_data)
                                chunks.append(chunk_data)
                            elif compression == 1:
                                import gzip
                                chunk_data = gzip.decompress(compressed_data)
                                chunks.append(chunk_data)
                        except:
                            pass
    except:
        pass
    return chunks


def search_in_region(region_path, search_strings):
    """Search for strings in a region file."""
    found = {}
    chunks = read_region_chunks(region_path)

    all_data = b''.join(chunks)

    for search in search_strings:
        if search.lower() in all_data.lower():
            # Find actual occurrences and context
            pos = 0
            occurrences = []
            lower_data = all_data.lower()
            lower_search = search.lower()
            while True:
                pos = lower_data.find(lower_search, pos)
                if pos == -1:
                    break
                # Get context around the match
                start = max(0, pos - 10)
                end = min(len(all_data), pos + len(search) + 50)
                context = all_data[start:end]
                # Try to extract block ID
                try:
                    context_str = context.decode('ascii', errors='replace')
                    occurrences.append(context_str)
                except:
                    pass
                pos += 1

            if occurrences:
                found[search.decode()] = occurrences[:5]  # First 5 occurrences

    return found


def main():
    region_dir = Path("mapa_1710/region")

    # Check a few sample regions
    sample_regions = [
        "r.0.0.mca",
        "r.0.1.mca",
        "r.1.0.mca",
        "r.-1.-1.mca",
        "r.-5.-3.mca",  # Where Blood Magic was found
    ]

    print("=" * 70)
    print("DEBUG: Searching for mod strings in region files")
    print("=" * 70)

    all_found = {}

    for region_name in sample_regions:
        region_path = region_dir / region_name
        if not region_path.exists():
            print(f"Region {region_name}: not found")
            continue

        print(f"\nScanning {region_name}...")
        found = search_in_region(region_path, SEARCH_STRINGS)

        if found:
            for search_term, contexts in found.items():
                print(f"  Found '{search_term}': {len(contexts)} occurrences")
                for ctx in contexts[:2]:
                    # Clean up the context for display
                    clean_ctx = ''.join(c if c.isprintable() else '.' for c in ctx)
                    print(f"    Context: {clean_ctx[:80]}")
                all_found[search_term] = all_found.get(search_term, 0) + len(contexts)
        else:
            print(f"  No mod strings found")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if all_found:
        for term, count in sorted(all_found.items(), key=lambda x: -x[1]):
            print(f"  {term}: {count} total occurrences")
    else:
        print("  No mod strings found in sampled regions")


if __name__ == "__main__":
    main()
