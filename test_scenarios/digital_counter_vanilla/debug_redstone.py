#!/usr/bin/env python3
"""
Redstone Circuit Partial Validator - Weryfikuje topologię i symuluje ring counter

OPIS:
Ten program to PARTIAL VALIDATOR (nie pełny symulator redstone).
Weryfikuje budowalność układu i symuluje zachowanie dla tej konkretnej topologii.

ZAKRES WALIDACJI:
- Budowalność: podparcia, attach, brak kolizji
- Spójność: clock_out połączony z bus (BFS)
- Symulacja: injected clock, dropper rising edge, comparator container read

ZGODNOŚĆ:
- Minecraft Java 1.7.10
- Game tick = 0.05s (20 TPS)
- Clock: 20 game ticks period, 4 game ticks pulse (injected)
"""

import json
import os
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set
from collections import deque
import argparse


GAME_TICKS_PER_SECOND = 20


@dataclass
class Position:
    x: int
    y: int
    z: int
    
    def __hash__(self):
        return hash((self.x, self.y, self.z))
    
    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)
    
    def __lt__(self, other):
        return (self.x, self.y, self.z) < (other.x, other.y, other.z)
    
    def offset(self, dx=0, dy=0, dz=0) -> 'Position':
        return Position(self.x + dx, self.y + dy, self.z + dz)


@dataclass 
class Block:
    pos: Position
    block_type: str
    properties: Dict
    purpose: str = ""
    nbt: Dict = field(default_factory=dict)
    
    # Stan symulacji
    power_level: int = 0
    was_powered: bool = False  # Do edge detection
    
    def __hash__(self):
        return hash(self.pos)


@dataclass
class ScheduledTick:
    tick: int
    pos: Position
    action: str


class RedstoneValidator:
    """Partial validator dla ring counter."""
    
    # Konfiguracja zegara (zgodna z circuit_design.json)
    CLOCK_PERIOD = 20  # game ticks
    CLOCK_PULSE = 4    # game ticks
    
    def __init__(self, voxel_grid_path: str):
        self.blocks: Dict[Position, Block] = {}
        self.game_tick = 0
        self.scheduled_ticks: List[ScheduledTick] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Stan ring counter
        self.dropper_contents: Dict[Position, Optional[str]] = {}
        self.dropper_to_digit: Dict[Position, int] = {}
        self.active_digit = 0
        self.command_fired: Set[int] = set()  # Które cyfry już odpaliły w tym cyklu
        
        # History
        self.history: List[Dict] = []
        
        self.load_from_voxel_grid(voxel_grid_path)
    
    def load_from_voxel_grid(self, path: str) -> bool:
        """Wczytuje świat z voxel_grid.json."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.errors.append(f"Cannot load voxel_grid: {e}")
            return False
        
        for section_name, section in data.get('sections', {}).items():
            for voxel in section.get('voxels', []):
                if not isinstance(voxel, dict):
                    continue
                
                pos = Position(voxel['x'], voxel['y'], voxel['z'])
                block = Block(
                    pos=pos,
                    block_type=voxel.get('block', 'minecraft:stone'),
                    properties=voxel.get('properties', {}),
                    purpose=voxel.get('purpose', ''),
                    nbt=voxel.get('nbt', {})
                )
                
                # Sprawdź duplikat
                if pos in self.blocks:
                    self.errors.append(f"DUPLICATE: {pos} has {self.blocks[pos].block_type} and {block.block_type}")
                    continue
                
                self.blocks[pos] = block
                
                # Inicjalizuj dropper
                if 'dropper' in block.block_type:
                    items = block.nbt.get('Items', [])
                    self.dropper_contents[pos] = items[0].get('id') if items else None
                    
                    purpose = block.purpose
                    if purpose and len(purpose) >= 2 and purpose[0] == 'D' and purpose[1].isdigit():
                        self.dropper_to_digit[pos] = int(purpose[1])
        
        print(f"[LOAD] Wczytano {len(self.blocks)} blokow")
        return True
    
    def validate_construction(self) -> bool:
        """Waliduje budowalność."""
        print("\n[VALIDATE] Sprawdzam budowalnosc...")
        errors_before = len(self.errors)
        
        # 1. Redstone wymaga podparcia
        for pos, block in self.blocks.items():
            if self._needs_support(block.block_type):
                support_pos = pos.offset(dy=-1)
                if support_pos not in self.blocks:
                    self.errors.append(f"SUPPORT: {block.block_type} at {pos} has no support below")
                elif not self._is_solid(self.blocks[support_pos].block_type):
                    self.errors.append(f"SUPPORT: {block.block_type} at {pos} support not solid: {self.blocks[support_pos].block_type}")
        
        # 2. Torch wymaga solid attachment
        for pos, block in self.blocks.items():
            if 'torch' in block.block_type and block.block_type != 'minecraft:redstone_torch':
                # Standing torch - musi stać na czymś
                support_pos = pos.offset(dy=-1)
                if support_pos not in self.blocks:
                    self.errors.append(f"ATTACH: Torch at {pos} has no block below")
        
        # 3. Droppery wskazują na dropper
        droppers = [(p, b) for p, b in self.blocks.items() if 'dropper' in b.block_type]
        for pos, dropper in droppers:
            facing = dropper.properties.get('facing', 'north')
            next_pos = self._get_facing_position(pos, facing)
            if next_pos not in self.blocks:
                self.warnings.append(f"DROP: Dropper at {pos} faces {facing} to empty space")
            elif 'dropper' not in self.blocks[next_pos].block_type:
                self.warnings.append(f"DROP: Dropper at {pos} faces non-dropper")
        
        # 4. Komparatory czytają dropper
        for pos, block in self.blocks.items():
            if 'comparator' in block.block_type:
                facing = block.properties.get('facing', 'north')
                input_pos = self._get_facing_position(pos, self._opposite_facing(facing))
                if input_pos not in self.blocks or 'dropper' not in self.blocks[input_pos].block_type:
                    self.warnings.append(f"COMP: Comparator at {pos} doesn't read dropper")
        
        # 5. Command blocki przy komparatorach
        for pos, block in self.blocks.items():
            if 'command_block' in block.block_type:
                connected = False
                for facing in ['north', 'south', 'east', 'west']:
                    adj = self._get_facing_position(pos, facing)
                    if adj in self.blocks and 'comparator' in self.blocks[adj].block_type:
                        connected = True
                        break
                if not connected:
                    self.warnings.append(f"CMD: Command block at {pos} not connected to comparator")
        
        error_count = len(self.errors) - errors_before
        if error_count == 0:
            print("[VALIDATE] OK - Brak bledow krytycznych")
        else:
            print(f"[VALIDATE] BLEDY ({error_count}):")
            for err in self.errors[-error_count:]:
                print(f"  ! {err}")
        
        if self.warnings:
            print(f"[VALIDATE] Ostrzezenia ({len(self.warnings)}):")
            for warn in self.warnings[:5]:  # Pokaż max 5
                print(f"  ? {warn}")
        
        return error_count == 0
    
    def validate_clock_to_bus_connection(self) -> bool:
        """BFS: czy clock_out jest połączony z bus dropperów."""
        print("\n[VALIDATE] Sprawdzam polaczenie clock -> bus...")
        
        # Znajdź clock_out
        clock_out_pos = None
        for pos, block in self.blocks.items():
            if block.purpose == 'clock_out' and 'redstone_wire' in block.block_type:
                clock_out_pos = pos
                break
        
        if not clock_out_pos:
            self.errors.append("CLOCK: No clock_out found")
            return False
        
        # Znajdź wszystkie pozycje bus
        bus_positions = set()
        for pos, block in self.blocks.items():
            if 'bus' in block.purpose and block.block_type == 'minecraft:redstone_wire':
                bus_positions.add(pos)
        
        if not bus_positions:
            self.errors.append("BUS: No bus positions found")
            return False
        
        # BFS z clock_out
        visited = set()
        queue = deque([clock_out_pos])
        reachable_bus = set()
        
        while queue:
            pos = queue.popleft()
            if pos in visited:
                continue
            visited.add(pos)
            
            if pos in bus_positions:
                reachable_bus.add(pos)
            
            # Sąsiedzi (redstone wire na tym samym y lub sąsiednim)
            for dx, dy, dz in [(1,0,0), (-1,0,0), (0,0,1), (0,0,-1), (0,1,0), (0,-1,0)]:
                neighbor = pos.offset(dx=dx, dy=dy, dz=dz)
                if neighbor in self.blocks and neighbor not in visited:
                    block = self.blocks[neighbor]
                    if 'redstone_wire' in block.block_type or 'repeater' in block.block_type:
                        queue.append(neighbor)
        
        unreachable = bus_positions - reachable_bus
        if unreachable:
            self.warnings.append(f"BUS: {len(unreachable)} bus positions unreachable from clock")
            return False
        
        print(f"[VALIDATE] OK - Clock polaczony z {len(reachable_bus)} bus pozycjami")
        return True
    
    def _needs_support(self, block_type: str) -> bool:
        return any(x in block_type for x in ['redstone_wire', 'repeater', 'comparator'])
    
    def _is_solid(self, block_type: str) -> bool:
        non_solid = ['redstone_wire', 'repeater', 'comparator', 'torch', 'dropper', 'command_block', 'lever']
        return not any(n in block_type for n in non_solid)
    
    def _get_facing_position(self, pos: Position, facing: str) -> Position:
        if facing == 'north': return pos.offset(dz=-1)
        if facing == 'south': return pos.offset(dz=1)
        if facing == 'east': return pos.offset(dx=1)
        if facing == 'west': return pos.offset(dx=-1)
        if facing == 'up': return pos.offset(dy=1)
        if facing == 'down': return pos.offset(dy=-1)
        return pos
    
    def _opposite_facing(self, facing: str) -> str:
        opposites = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east', 'up': 'down', 'down': 'up'}
        return opposites.get(facing, facing)
    
    def schedule_tick(self, pos: Position, delay: int, action: str):
        self.scheduled_ticks.append(ScheduledTick(
            tick=self.game_tick + delay,
            pos=pos,
            action=action
        ))
        self.scheduled_ticks.sort(key=lambda t: t.tick)
    
    def process_scheduled_ticks(self):
        """Przetwarza zaplanowane ticki."""
        to_process = [t for t in self.scheduled_ticks if t.tick <= self.game_tick]
        self.scheduled_ticks = [t for t in self.scheduled_ticks if t.tick > self.game_tick]
        
        # Droppery które miały item na początku ticku
        droppers_with_item = set(pos for pos, item in self.dropper_contents.items() if item is not None)
        
        for tick in to_process:
            if tick.pos not in self.blocks:
                continue
            
            block = self.blocks[tick.pos]
            
            if 'dropper' in block.block_type and tick.action == "eject":
                if tick.pos in droppers_with_item:
                    self._process_dropper_eject(block)
                    droppers_with_item.discard(tick.pos)
            elif 'comparator' in block.block_type and tick.action == "update":
                self._process_comparator_update(block)
    
    def _process_dropper_eject(self, dropper: Block):
        """Przenosi item do następnego droppera."""
        item = self.dropper_contents.get(dropper.pos)
        if not item:
            return
        
        facing = dropper.properties.get('facing', 'north')
        next_pos = self._get_facing_position(dropper.pos, facing)
        
        if next_pos in self.blocks and 'dropper' in self.blocks[next_pos].block_type:
            if self.dropper_contents.get(next_pos) is None:
                self.dropper_contents[dropper.pos] = None
                self.dropper_contents[next_pos] = item
                self._update_active_digit()
    
    def _process_comparator_update(self, comparator: Block):
        """Aktualizuje komparator."""
        facing = comparator.properties.get('facing', 'north')
        input_pos = self._get_facing_position(comparator.pos, self._opposite_facing(facing))
        
        if input_pos in self.blocks and 'dropper' in self.blocks[input_pos].block_type:
            has_item = self.dropper_contents.get(input_pos) is not None
            new_power = 1 if has_item else 0  # Uproszczenie: 1 item = signal 1
            
            old_power = comparator.power_level
            comparator.power_level = new_power
            
            # Edge trigger dla command blocka
            if new_power > 0 and old_power == 0:
                output_pos = self._get_facing_position(comparator.pos, facing)
                if output_pos in self.blocks and 'command_block' in self.blocks[output_pos].block_type:
                    cmd_block = self.blocks[output_pos]
                    cmd = cmd_block.nbt.get('Command', '')
                    digit = cmd.split()[-1] if 'say' in cmd else None
                    if digit and digit.isdigit():
                        self.command_fired.add(int(digit))
    
    def _update_active_digit(self):
        """Aktualizuje aktywną cyfrę."""
        for pos, item in self.dropper_contents.items():
            if item is not None and pos in self.dropper_to_digit:
                self.active_digit = self.dropper_to_digit[pos]
                break
    
    def get_clock_power(self) -> int:
        """Zwraca moc zegara (injected)."""
        in_pulse = (self.game_tick % self.CLOCK_PERIOD) < self.CLOCK_PULSE
        return 15 if in_pulse else 0
    
    def propagate_bus_power(self):
        """Propaguje moc z clock_out do wszystkich reachable dust (BFS)."""
        clock_power = self.get_clock_power()
        
        # Znajdź clock_out
        clock_out_pos = None
        for pos, block in self.blocks.items():
            if block.purpose == 'clock_out' and 'redstone_wire' in block.block_type:
                clock_out_pos = pos
                break
        
        if not clock_out_pos:
            return
        
        # BFS z clock_out
        visited = set()
        queue = deque([clock_out_pos])
        powered_dust = set()
        
        while queue:
            pos = queue.popleft()
            if pos in visited:
                continue
            visited.add(pos)
            
            if pos in self.blocks:
                block = self.blocks[pos]
                if 'redstone_wire' in block.block_type:
                    block.power_level = clock_power
                    block.is_powered = clock_power > 0
                    powered_dust.add(pos)
                    
                    # Sąsiedzi
                    for dx, dy, dz in [(1,0,0), (-1,0,0), (0,0,1), (0,0,-1), (0,1,0), (0,-1,0)]:
                        neighbor = pos.offset(dx=dx, dy=dy, dz=dz)
                        if neighbor in self.blocks and neighbor not in visited:
                            queue.append(neighbor)
        
        # Zasil droppery pod dust (y=3 dust -> y=1 dropper)
        for dust_pos in powered_dust:
            dropper_pos = dust_pos.offset(dy=-2)  # y=3 -> y=1
            if dropper_pos in self.blocks and 'dropper' in self.blocks[dropper_pos].block_type:
                dropper = self.blocks[dropper_pos]
                old_powered = dropper.was_powered
                dropper.power_level = clock_power
                dropper.was_powered = clock_power > 0
                
                # Rising edge - schedule eject
                if not old_powered and clock_power > 0:
                    self.schedule_tick(dropper_pos, 4, "eject")
    
    def tick(self) -> Dict:
        """Wykonuje jeden game tick."""
        # Reset command fired na początku ticku (tylko cyfry odpalone w TYM ticku)
        self.command_fired.clear()
        
        self.propagate_bus_power()
        self.process_scheduled_ticks()
        
        # Aktualizuj komparatory
        for pos, block in self.blocks.items():
            if 'comparator' in block.block_type:
                facing = block.properties.get('facing', 'north')
                input_pos = self._get_facing_position(pos, self._opposite_facing(facing))
                if input_pos in self.blocks and 'dropper' in self.blocks[input_pos].block_type:
                    has_item = self.dropper_contents.get(input_pos) is not None
                    new_power = 1 if has_item else 0
                    if new_power != block.power_level:
                        self.schedule_tick(pos, 2, "update")
        
        state = {
            'tick': self.game_tick,
            'time': self.game_tick / GAME_TICKS_PER_SECOND,
            'clock': self.get_clock_power() > 0,
            'digit': self.active_digit,
            'triggered': sorted(self.command_fired) if self.command_fired else [],
            'dropper_with_item': self._get_dropper_with_item()
        }
        
        self.game_tick += 1
        return state
    
    def _get_dropper_with_item(self) -> Optional[int]:
        for pos, item in self.dropper_contents.items():
            if item is not None and pos in self.dropper_to_digit:
                return self.dropper_to_digit[pos]
        return None
    
    def run_validation(self, duration_seconds: float = 12.0, show_interval: float = 0.5):
        """Główna metoda walidacji i symulacji."""
        print("=" * 70)
        print("   REDSTONE CIRCUIT PARTIAL VALIDATOR")
        print("   Ring Counter Topology | MC 1.7.10 | Injected Clock")
        print("=" * 70)
        print()
        print("   Scope: Buildability check + Topology-based simulation")
        print("   Clock: 20 tick period, 4 tick pulse (injected)")
        print()
        
        # Walidacja
        if not self.validate_construction():
            print("\n[FAIL] Bledy budowalnosci - przerwano")
            return False
        
        if not self.validate_clock_to_bus_connection():
            print("\n[WARNING] Problem z polaczeniem clock-bus")
        
        # Symulacja
        print(f"\n[SIMULATE] Symulacja na {duration_seconds}s...")
        total_ticks = int(duration_seconds * GAME_TICKS_PER_SECOND)
        last_show = -show_interval
        
        for _ in range(total_ticks):
            state = self.tick()
            self.history.append(state)
            
            if state['time'] - last_show >= show_interval:
                self._print_state(state)
                last_show = state['time']
        
        self._print_summary()
        return True
    
    def _print_state(self, state: Dict):
        clock_str = "[PULSE]" if state['clock'] else "[-----]"
        digit = state['digit']
        triggered = state['triggered']
        dropper = state['dropper_with_item']
        
        if triggered:
            output = f"[CHAT] [Server] {triggered[-1]} <<< NOWA CYFRA!"
        else:
            output = "(oczekiwanie...)"
        
        print(f"Tick {state['tick']:4d} | {state['time']:5.2f}s | {clock_str} | D{dropper} | {output}")
    
    def _print_summary(self):
        print("\n" + "=" * 70)
        print("[SUMMARY] Symulacja zakonczona")
        print("=" * 70)
        
        # Zlicz aktywacje
        all_fired = set()
        for state in self.history:
            all_fired.update(state['triggered'])
        
        print(f"\nOdpalone cyfry: {sorted(all_fired)}")
        
        if set(range(10)).issubset(all_fired):
            print("[PASS] Wszystkie cyfry 0-9 pojawily sie")
        else:
            missing = set(range(10)) - all_fired
            print(f"[FAIL] Brakujace cyfry: {missing}")
        
        # Sprawdź sekwencję
        sequence = []
        for state in self.history:
            if state['triggered'] and state['triggered'][-1] != sequence[-1] if sequence else True:
                if state['triggered']:
                    sequence.append(state['triggered'][-1])
        
        print(f"\nSekwencja: {sequence[:20]}...")  # Pokaż pierwsze 20
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Redstone Circuit Partial Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-t', '--time', type=float, default=12.0)
    parser.add_argument('-i', '--interval', type=float, default=0.5)
    
    args = parser.parse_args()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    voxel_path = os.path.join(script_dir, 'schematics', 'voxel_grid.json')
    
    if not os.path.exists(voxel_path):
        print(f"[ERROR] Nie znaleziono: {voxel_path}")
        sys.exit(1)
    
    validator = RedstoneValidator(voxel_path)
    
    try:
        success = validator.run_validation(duration_seconds=args.time, show_interval=args.interval)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[STOP] Przerwano")
        sys.exit(0)


if __name__ == '__main__':
    main()
