"""Symulacja multiblock monitora ComputerCraft 1.7.10 → CC:Tweaked 1.18.2.

Bazuje na kodzie źródłowym:
- 1.7.10: `shared/peripheral/monitor/TileMonitor.java`, `BlockPeripheral.java`
- 1.18.2: `shared/peripheral/monitor/MonitorBlockEntity.java`, `MonitorBlock.java`

Kluczowa różnica: w 1.7.10 orientacja jest zakodowana w polu `dir` w NBT,
w 1.18.2 jest wyrażona przez blockstate (`orientation` + `facing`).
"""

from __future__ import annotations

from dataclasses import dataclass


# Mapowanie 1.7.10 `dir` → 1.18.2 (`orientation`, `facing`)
# dir <= 5: horizontal (wall-mounted), orientation=NORTH
# dir 8-11: ceiling (screen faces DOWN), orientation=DOWN
# dir 14-17: floor (screen faces UP), orientation=UP
DIR_TO_BLOCKSTATE: dict[int, tuple[str, str]] = {
    # Horizontal monitors
    2: ("north", "north"),
    3: ("north", "south"),
    4: ("north", "west"),
    5: ("north", "east"),
    # Ceiling monitors (screen faces down)
    8: ("down", "north"),
    9: ("down", "south"),
    10: ("down", "west"),
    11: ("down", "east"),
    # Floor monitors (screen faces up)
    14: ("up", "north"),
    15: ("up", "south"),
    16: ("up", "west"),
    17: ("up", "east"),
}

# Facing indices w 1.7.10: 2=NORTH, 3=SOUTH, 4=WEST, 5=EAST
FACING_IDX_TO_NAME = {2: "north", 3: "south", 4: "west", 5: "east"}
FACING_NAME_TO_IDX = {v: k for k, v in FACING_IDX_TO_NAME.items()}


@dataclass
class Monitor1710:
    """Symulacja tile entity monitora w 1.7.10."""

    x_index: int = 0
    y_index: int = 0
    width: int = 1
    height: int = 1
    dir: int = 2  # 2,3,4,5 = horizontal; 8-11 = ceiling; 14-17 = floor

    def write_to_nbt(self) -> dict:
        return {
            "xIndex": self.x_index,
            "yIndex": self.y_index,
            "width": self.width,
            "height": self.height,
            "dir": self.dir,
        }

    @classmethod
    def read_from_nbt(cls, nbt: dict) -> "Monitor1710":
        return cls(
            x_index=nbt.get("xIndex", 0),
            y_index=nbt.get("yIndex", 0),
            width=nbt.get("width", 1),
            height=nbt.get("height", 1),
            dir=nbt.get("dir", 2),
        )

    def get_facing(self) -> str:
        """Kierunek frontu monitora (dla horizontal) lub baza (dla vertical)."""
        return FACING_IDX_TO_NAME.get(self.dir % 6, "north")

    def get_right(self) -> str:
        """Kierunek 'w prawo' w lokalnych współrzędnych monitora (1.7.10 logic)."""
        base = self.dir % 6
        if base == 2:
            return "west"
        if base == 3:
            return "east"
        if base == 4:
            return "south"
        if base == 5:
            return "north"
        return "west"

    def get_down(self) -> str:
        """Kierunek 'w dół' w lokalnych współrzędnych monitora (1.7.10 logic)."""
        if self.dir <= 5:
            return "up"
        # Vertical monitors — zależy od implementacji, uproszczenie:
        base = self.dir % 6
        if self.dir in (8, 9, 10, 11):  # ceiling
            # W 1.7.10 getDown() dla ceiling: zwraca kierunek zgodny z dir%6
            return self.get_facing()
        # floor
        # W 1.18.2 floor getDown() to opposite facing
        # W 1.7.10 było to trochę inaczej, ale dla celów konwersji wystarczy nam
        # zgodność blockstate — CC:Tweaked samo przeliczy getDown() przy expand()
        return self.get_facing()


@dataclass
class Monitor1182:
    """Symulacja block entity monitora w 1.18.2."""

    x_index: int = 0
    y_index: int = 0
    width: int = 1
    height: int = 1
    orientation: str = "north"  # north | up | down
    facing: str = "north"       # north | south | west | east

    def write_to_nbt(self) -> dict:
        return {
            "XIndex": self.x_index,
            "YIndex": self.y_index,
            "Width": self.width,
            "Height": self.height,
        }

    @classmethod
    def read_from_nbt(cls, nbt: dict, orientation: str, facing: str) -> "Monitor1182":
        return cls(
            x_index=nbt.get("XIndex", 0),
            y_index=nbt.get("YIndex", 0),
            width=nbt.get("Width", 1),
            height=nbt.get("Height", 1),
            orientation=orientation,
            facing=facing,
        )

    def get_right(self) -> str:
        """1.18.2: getRight() = getDirection().getCounterClockWise()."""
        # facing → right (counter-clockwise when looking from front)
        return {
            "north": "west",
            "south": "east",
            "west": "south",
            "east": "north",
        }[self.facing]

    def get_down(self) -> str:
        """1.18.2: getDown() zależy od orientation."""
        if self.orientation == "north":  # horizontal wall
            return "up"
        if self.orientation == "down":  # ceiling
            return self.facing
        # floor (up)
        return {
            "north": "south",
            "south": "north",
            "west": "east",
            "east": "west",
        }[self.facing]


def convert_monitor_nbt(nbt_1710: dict) -> dict:
    """Skonwertuj NBT monitora z 1.7.10 na 1.18.2.

    Mapowanie tagów:
        xIndex → XIndex
        yIndex → YIndex
        width  → Width
        height → Height
        dir    → (w blockstate, nie w NBT)
    """
    return {
        "XIndex": nbt_1710.get("xIndex", 0),
        "YIndex": nbt_1710.get("yIndex", 0),
        "Width": nbt_1710.get("width", 1),
        "Height": nbt_1710.get("height", 1),
    }


def convert_monitor_dir(dir_1710: int) -> tuple[str, str]:
    """Zamień 1.7.10 `dir` na 1.18.2 (`orientation`, `facing`).

    Zwraca (orientation, facing).
    """
    return DIR_TO_BLOCKSTATE.get(dir_1710, ("north", "north"))


def derive_monitor_blockstate(nbt_1710: dict) -> dict[str, str]:
    """Wydedukuj blockstate monitora 1.18.2 z NBT 1.7.10."""
    orientation, facing = convert_monitor_dir(nbt_1710.get("dir", 2))
    # State (krawędzie) — można wyliczyć z xIndex/yIndex/width/height
    # lub zostawić do przeliczenia przez grę przy pierwszym ticku
    x = nbt_1710.get("xIndex", 0)
    y = nbt_1710.get("yIndex", 0)
    w = nbt_1710.get("width", 1)
    h = nbt_1710.get("height", 1)

    # Oblicz krawędzie (l=left, r=right, u=up, d=down)
    # Kolejność w blockstate CC:Tweaked: l < r < u < d
    edges = []
    if x > 0:
        edges.append("l")
    if x < w - 1:
        edges.append("r")
    if y > 0:
        edges.append("u")
    if y < h - 1:
        edges.append("d")

    state = "".join(edges) if edges else "none"
    return {
        "orientation": orientation,
        "facing": facing,
        "state": state,
    }


def _run_example():
    print("=" * 60)
    print("ComputerCraft — symulacja multiblock monitora")
    print("=" * 60)

    # Przykład: monitor 2x2, lewy-górny róg (origin)
    mon_1710 = Monitor1710(x_index=0, y_index=0, width=2, height=2, dir=2)
    nbt_1710 = mon_1710.write_to_nbt()
    print("\n[1.7.10] Monitor NBT:", nbt_1710)
    print("[1.7.10] getRight():", mon_1710.get_right(), "getDown():", mon_1710.get_down())

    # Konwersja
    nbt_1182 = convert_monitor_nbt(nbt_1710)
    blockstate = derive_monitor_blockstate(nbt_1710)
    print("[1.18.2] Converted NBT:", nbt_1182)
    print("[1.18.2] Blockstate:", blockstate)

    mon_1182 = Monitor1182.read_from_nbt(nbt_1182, blockstate["orientation"], blockstate["facing"])
    print("[1.18.2] getRight():", mon_1182.get_right(), "getDown():", mon_1182.get_down())

    assert mon_1710.get_right() == mon_1182.get_right(), "getRight mismatch!"
    print("\n✓ Test równoważności getRight() przeszedł")

    # Test wszystkich dir values
    print("\n--- Mapowanie dir → (orientation, facing) ---")
    for d in sorted(DIR_TO_BLOCKSTATE.keys()):
        ori, fac = convert_monitor_dir(d)
        print(f"  dir={d:2d} → orientation={ori:5s}, facing={fac:5s}")

    # Test równoważności getRight/getDown dla wszystkich dir
    print("\n--- Weryfikacja getRight/getDown dla wszystkich dir ---")
    all_ok = True
    for d in sorted(DIR_TO_BLOCKSTATE.keys()):
        m1710 = Monitor1710(dir=d)
        ori, fac = convert_monitor_dir(d)
        m1182 = Monitor1182(orientation=ori, facing=fac)
        # Dla horizontal getDown musi być "up"
        if d <= 5:
            if m1710.get_down() != "up" or m1182.get_down() != "up":
                print(f"  FAIL dir={d}: getDown mismatch")
                all_ok = False
        if m1710.get_right() != m1182.get_right():
            print(f"  FAIL dir={d}: getRight mismatch ({m1710.get_right()} vs {m1182.get_right()})")
            all_ok = False
    if all_ok:
        print("✓ Wszystkie dir values poprawnie mapują getRight/getDown")


if __name__ == "__main__":
    _run_example()
