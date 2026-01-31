#!/usr/bin/env python3
"""
Testy automatyczne dla RedstoneValidator
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from debug_redstone import RedstoneValidator, Position


VGRID_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'schematics', 'voxel_grid.json'
)


class TestBuildability(unittest.TestCase):
    """Testy budowalnosci."""
    
    def setUp(self):
        self.validator = RedstoneValidator(VGRID_PATH)
        self.validator.load_from_voxel_grid(VGRID_PATH)
    
    def test_01_no_duplicate_coordinates(self):
        """Test: Brak duplikatow (x,y,z)."""
        positions = list(self.validator.blocks.keys())
        unique_positions = set(positions)
        self.assertEqual(len(positions), len(unique_positions), 
                        f"Znaleziono duplikaty: {len(positions) - len(unique_positions)}")
    
    def test_02_redstone_requires_support(self):
        """Test: Redstone ma podparcie."""
        self.validator.validate_construction()
        support_errors = [e for e in self.validator.errors if 'SUPPORT:' in e]
        self.assertEqual(len(support_errors), 0, 
                        f"Redstone bez podparcia: {support_errors}")
    
    def test_03_torch_attachment_is_solid(self):
        """Test: Torch przyczepiony do solidnego bloku."""
        self.validator.validate_construction()
        attach_errors = [e for e in self.validator.errors if 'ATTACH:' in e]
        self.assertEqual(len(attach_errors), 0,
                        f"Torch bez attachment: {attach_errors}")


class TestClockConnection(unittest.TestCase):
    """Testy polaczenia zegara."""
    
    def setUp(self):
        self.validator = RedstoneValidator(VGRID_PATH)
        self.validator.load_from_voxel_grid(VGRID_PATH)
    
    def test_04_clock_connects_to_bus(self):
        """Test: Clock polaczony z bus (BFS)."""
        connected = self.validator.validate_clock_to_bus_connection()
        self.assertTrue(connected, "Clock nie jest polaczony z bus")


class TestRingCounter(unittest.TestCase):
    """Testy ring countera."""
    
    def setUp(self):
        self.validator = RedstoneValidator(VGRID_PATH)
        self.validator.load_from_voxel_grid(VGRID_PATH)
        self.validator.validate_construction()
        self.validator.validate_clock_to_bus_connection()
    
    def test_05_ring_counter_advances_one_step_per_pulse(self):
        """Test: Ring counter przesuwa o 1 na impuls."""
        # Symuluj 3 impulsy
        digits_seen = []
        for _ in range(3 * 20):  # 3 okresy zegara
            state = self.validator.tick()
            if state['triggered']:
                digits_seen.append(state['digit'])
        
        # Sprawdz czy kazdy krok to +1
        for i in range(1, len(digits_seen)):
            expected = (digits_seen[i-1] + 1) % 10
            self.assertEqual(digits_seen[i], expected,
                           f"Nieprawidlowy krok: {digits_seen[i-1]} -> {digits_seen[i]}")
    
    def test_06_command_blocks_fire_on_edges_only(self):
        """Test: Command blocki odpalaja tylko na edge."""
        fired_counts = {i: 0 for i in range(10)}
        prev_triggered = set()
        
        for tick in range(100):
            state = self.validator.tick()
            current = set(state['triggered'])
            new_fired = current - prev_triggered
            for d in new_fired:
                fired_counts[d] += 1
            prev_triggered = current
        
        # Max 3 odpalenia na cyfre w 100 tickach (5 cykli)
        for digit, count in fired_counts.items():
            self.assertLessEqual(count, 5,
                               f"Cyfra {digit} odpalila sie {count} razy")
    
    def test_07_sequence_0_to_9_repeats(self):
        """Test: Sekwencja 0-9 powtarza sie."""
        all_digits = set()
        for _ in range(220):  # 11 sekund
            state = self.validator.tick()
            all_digits.add(state['digit'])
        
        self.assertEqual(all_digits, set(range(10)),
                        f"Brakujace cyfry: {set(range(10)) - all_digits}")


class TestTiming(unittest.TestCase):
    """Testy timing-u."""
    
    def test_08_clock_period_is_20_ticks(self):
        """Test: Okres zegara to 20 tickow."""
        validator = RedstoneValidator(VGRID_PATH)
        self.assertEqual(validator.CLOCK_PERIOD, 20)
    
    def test_09_clock_pulse_is_4_ticks(self):
        """Test: Impuls zegara to 4 ticki."""
        validator = RedstoneValidator(VGRID_PATH)
        self.assertEqual(validator.CLOCK_PULSE, 4)


def run_tests():
    """Uruchamia wszystkie testy."""
    print("\n" + "=" * 70)
    print("   REDSTONE VALIDATOR - AUTOMATED TESTS")
    print("=" * 70 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestBuildability))
    suite.addTests(loader.loadTestsFromTestCase(TestClockConnection))
    suite.addTests(loader.loadTestsFromTestCase(TestRingCounter))
    suite.addTests(loader.loadTestsFromTestCase(TestTiming))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
