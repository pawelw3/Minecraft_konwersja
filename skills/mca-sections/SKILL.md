---
name: minecraft-anvil-editkit
description: Offline editing and verification of Minecraft 1.7.10 worlds (Anvil .mca) using the project’s Kotlin/Hephaistos tools. Covers legacy Sections (Blocks/Data/AddBlocks), TileEntities, negative coords, and a test-first workflow to avoid corrupted region files and false inspections.
license: MIT
metadata:
  author: project
  version: "1.0"
compatibility: |
  Intended for Minecraft Java 1.7.10 Anvil worlds (.mca). Requires JVM tooling available in the repo (Kotlin worker using Hephaistos). Network access not required. Do not substitute NBT-only libs (e.g., flow-nbt) for region writing.
---

# Minecraft Anvil EditKit (Hephaistos-first)

## Purpose

This skill teaches you how to **safely read and edit Minecraft 1.7.10 Anvil worlds (`region/r.x.z.mca`)** and verify results **headlessly**.  
The core rule: **use the Kotlin tool in this repo that wraps Hephaistos** for all `.mca` I/O. Treat other approaches as debug-only.

## When to use this skill

Use this skill whenever you need to:
- Inspect blocks/TileEntities in specific chunks, including **negative coordinates**.
- Apply offline patches: set blocks, place command blocks, set TE NBT, paste structures.
- Prove correctness with repeatable tests (read/write round-trip, boot server log probes).

## Non-goals

- Re-implementing a region writer (`.mca` headers, sectors, compression) from scratch.
- Switching to **NBT-only** libraries as the main backend (e.g., `flow-nbt`) when the task is “edit `.mca` safely”.
- Relying on a player joining the server to validate outcomes.

---

# Core concepts you must get right

## 1) Anvil file layout

- Worlds store chunks inside **region files**: `region/r.<rx>.<rz>.mca`
- Each region file contains a 32×32 grid of chunks.
- Chunk coordinates exist in two coordinate spaces:
  - **Global chunk coords**: `(cx, cz)` in world space
  - **Local chunk coords**: `(lcx, lcz)` in range 0..31 within a region file

### Golden rule (Hephaistos API)
When using the repo’s Hephaistos wrapper:
- **Always call RegionFile getChunk/getChunkData with GLOBAL chunk coords** `(cx, cz)`.
- Compute local coords only for indexing or debug prints.

## 2) Negative coordinate math (must be floor-based)

For any conversions with negatives:
- Use `floorDiv` / `floorMod` equivalents.
- In this repo, use the shared Kotlin helpers (e.g. `Coords.kt`) rather than rewriting formulas.

Required helpers pattern (example):
- `regionCoordFromChunk(c) = floorDiv(c, 32)`
- `localChunkFromChunk(c) = floorMod(c, 32)`
- `chunkCoordFromBlock(b) = floorDiv(b, 16)`
- `localBlockFromWorld(b) = floorMod(b, 16)`

If you see `int(x/16)` or “clever” `shr` + `-1` tricks duplicated across files, refactor to one shared util.

## 3) 1.7.10 legacy chunk storage: Sections

Minecraft 1.7.10 stores blocks in `Level/Sections` (a list of section compounds).  
Each section covers Y from `Y*16` to `Y*16+15` and uses fixed-size arrays:

- `Blocks`: ByteArray(4096)  -> low 8 bits of block ID
- `Data`: ByteArray(2048)    -> metadata nibble (0..15)
- `AddBlocks`: ByteArray(2048) optional -> high 4 bits of block ID if ID > 255

### Indexing inside a section
For local block coords `(lx, ly, lz)` each 0..15:
- `idx = (ly * 16 + lz) * 16 + lx`  (store and use consistently)
- Nibble arrays (`Data`, `AddBlocks`) store 2 values per byte.

### “Sections” pitfalls checklist
- ✅ Create missing section compounds when writing.
- ✅ Ensure array sizes exactly match 4096/2048.
- ✅ Only create `AddBlocks` if needed (blockId > 255), but handle the case where it already exists.
- ❌ Do not invent 1.13+ palette/block_states structures for 1.7.10 chunks.

## 4) TileEntities (TE) in 1.7.10

Chunk TEs live in: `Level/TileEntities` (list of compounds).  
Each TE must have:
- `id` (string)
- `x`, `y`, `z` (ints)

### Replacing TE deterministically
When setting a TE at `(x,y,z)`:
- Remove any existing TE with matching coords.
- Insert the new TE.

### Command block TE in 1.7.10
For command blocks in 1.7.10 commonly:
- `id = "Control"`
- `Command = "/say ..."` (string)

---

# The mandated workflow (test-first)

## Step 0 — Always use the repo’s Kotlin Hephaistos tool

- Do **not** implement `.mca` I/O in Python.
- Do **not** replace Hephaistos with NBT-only libs.
- Use the Kotlin worker/inspector already in this project.

If you need new capabilities, extend the Kotlin tool (not a parallel backend).

## Step 1 — “Read/Write unchanged” smoke test (must pass)

Before any edits:
1. Pick an existing region file (e.g., `r.0.0.mca`).
2. Read a known chunk.
3. Write it back **without changes**.
4. Read again and verify it’s readable.

If this fails: stop. Fix I/O before touching Sections/TE.

## Step 2 — Minimal single-block write

Apply one block edit in a known chunk (e.g. stone at (0,64,0)):
- Ensure section exists
- Set `Blocks`/`Data` correctly
- Read-back verifies the exact id/meta

## Step 3 — TE round-trip

Place a command block + TE:
- Block ID 137 at (0,64,1)
- TE with id `"Control"` and a `Command` that produces a log marker

Read-back must confirm TE presence and the `Command` string.

## Step 4 — Headless server probe (no “join and check”)

Boot the server headless and expect a log marker:
- PASS if logs contain e.g. `[ROUNDTRIP] ok`
- FAIL if chunk load errors appear (e.g. “Couldn't load chunk”) or marker is missing

## Step 5 — Scale to multi-chunk / spiral probes

Only after the above pass:
- Generate multi-chunk patches.
- Run a spiral probe test that logs per chunk/step.

---

# How to inspect “what blocks are in this chunk”

Use the Kotlin inspector built on Hephaistos:
- It must read the target chunk (GLOBAL `(cx,cz)`)
- It must decode legacy `Sections` arrays into `(blockId, meta)` values
- It must print:
  - region file path opened
  - global chunk coords requested
  - computed `(regionX, regionZ)` and `(localChunkX, localChunkZ)` for debugging
  - summary of block IDs/metas (unique counts or a bounded sample)
  - list of TileEntities (id + coords)

**Do not** trust a tool that:
- hardcodes region `r.0.0.mca`,
- calls RegionFile getChunk using local (0..31) coords,
- uses non-floor division for negatives.

---

# Hard requirements and “stop conditions”

## Stop conditions (do not continue until fixed)
- You see negative chunks mapping into region 0 (e.g., chunk (-1,0) opening `r.0.0.mca`)
- RegionFile throws “Out of RegionFile” when you used global coords (that indicates your coords are wrong)
- Array sizes are not exact (4096/2048)
- Duplicate `Level` nesting appears in chunk NBT (`Level -> Level -> ...`)
- The server logs chunk load errors after your write

## Required regression tests to keep
- Mapping table for negatives:
  - (0,-1), (-1,0), (-1,-1), (-32,0), (-33,0), (32,0)
- “Read/Write unchanged” on at least one region file
- TE replace test (no duplicates at same x/y/z)

---

# Examples (what “good” looks like)

## Example: inspect chunks around origin (global coords)
- Inspect: (0,0), (0,-1), (-1,0), (-1,-1)
- Expected debug output includes:
  - file opened: `r.0.0`, `r.0.-1`, `r.-1.0`, `r.-1.-1` respectively
  - globals passed to API: `getChunkData(cx,cz)` with the same `(cx,cz)` you requested

## Example: set a block in chunk (-1,-1)
- World coords: x=-1, z=-1  -> global chunk (-1,-1)
- region: (-1,-1), local chunk: (31,31)
- but the **Hephaistos call uses global (-1,-1)**, not (31,31)

---

# Notes for future extensions

If you cannot find authoritative documentation for a modded TE schema:
- Treat TE NBT as opaque; preserve unknown tags.
- Ask the user for small in-game reproductions + screenshots or TE dumps, then implement a minimal safe write path.

If you need to paste large structures:
- Batch edits by region file and chunk to minimize open/close overhead.
- Validate after each region write with read-back.
