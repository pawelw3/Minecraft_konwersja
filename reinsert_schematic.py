import sys
sys.path.insert(0, 'src')
from schematic_to_world import insert_schematic_into_world
from pathlib import Path

# Wstaw schematic do świata
schematic_path = Path('output/digital_counter_v2.schematic')
world_path = Path('headless_server/1.7.10/world')

insert_schematic_into_world(
    schematic_path,
    world_path,
    target_x=0,
    target_y=60,
    target_z=0
)

print("Schematic wstawiony ponownie!")
