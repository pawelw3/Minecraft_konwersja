"""
Test spirali R=1 (mikro) na czystym świecie 1.7.10
"""
import sys
sys.path.insert(0, '.')
import shutil
import subprocess
import time
import re
import os

from mc_editkit.world.editor import WorldEditor
from mc_editkit.world.types import Pos

CLEAN_WORLD = r'..\headless_server\tests\headless_server\1.7.10_clean'
TEST_WORLD = r'C:\Users\pawel\AppData\Local\Temp\mc_spiral_r1_test'

def build_spiral_r1():
    """Buduje spiralę R=1 (3x3 chunks)"""
    # Skopiuj świat
    if os.path.exists(TEST_WORLD):
        shutil.rmtree(TEST_WORLD)
    shutil.copytree(CLEAN_WORLD, TEST_WORLD)
    
    world_path = os.path.join(TEST_WORLD, 'world')
    editor = WorldEditor(world_path, backup=False)
    
    # Spiralna ścieżka R=1 (chunks: (0,0), (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1))
    # To 9 chunków, uproszczona spirala
    spiral = [
        (0, 0), (1, 0), (1, 1), (0, 1), (-1, 1),
        (-1, 0), (-1, -1), (0, -1), (1, -1)
    ]
    
    y = 64  # Wysokość na superflat
    
    for step, (cx, cz) in enumerate(spiral):
        # Stone platform 3x3 w środku chunka
        base_x = cx * 16 + 8
        base_z = cz * 16 + 8
        
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                editor.set_block(Pos(base_x + dx, y, base_z + dz), 1, 0)  # stone
        
        # Command block z probe
        editor.set_command_block(
            Pos(base_x, y + 1, base_z),
            f'/say [PROBE] R1 cx={cx} cz={cz} step={step}'
        )
        
        # Repeater do następnego (jeśli nie ostatni)
        if step < len(spiral) - 1:
            next_cx, next_cz = spiral[step + 1]
            # Uproszczony repeater - redstone block
            mid_x = (base_x + next_cx * 16 + 8) // 2
            mid_z = (base_z + next_cz * 16 + 8) // 2
            editor.set_block(Pos(mid_x, y + 1, mid_z), 152, 0)  # redstone block
    
    # Start signal na początku
    start_x, start_z = spiral[0][0] * 16 + 8, spiral[0][1] * 16 + 8
    editor.set_block(Pos(start_x, y + 2, start_z), 152, 0)  # redstone block nad pierwszym
    
    editor.commit()
    editor.close()
    
    print(f'Zbudowano spiralę R=1 w: {world_path}')
    return world_path

def run_server_test():
    """Uruchamia serwer i sprawdza logi"""
    # Przygotuj serwer
    server_dir = TEST_WORLD
    
    # Zmień port
    props_path = os.path.join(server_dir, 'server.properties')
    with open(props_path, 'r') as f:
        props = f.read()
    props = props.replace('server-port=25567', 'server-port=25568')
    with open(props_path, 'w') as f:
        f.write(props)
    
    print(f'Uruchamiam serwer w: {server_dir}')
    
    proc = subprocess.Popen(
        ['java', '-Xmx1G', '-cp', 'minecraft_server.1.7.10.jar;libraries/*',
         'net.minecraft.server.MinecraftServer', 'nogui'],
        cwd=server_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    probes = []
    start_time = time.time()
    max_wait = 60
    
    try:
        for line in proc.stdout:
            line = line.rstrip()
            print(line)
            
            # Szukaj [PROBE]
            m = re.search(r'\[PROBE\] R1 cx=(\-?\d+) cz=(\-?\d+) step=(\d+)', line)
            if m:
                cx, cz, step = int(m.group(1)), int(m.group(2)), int(m.group(3))
                probes.append(step)
                print(f'>>> PROBE: step={step} @ ({cx},{cz})')
            
            if 'Done (' in line:
                print('>>> Serwer GOTOWY!')
            
            if time.time() - start_time > max_wait:
                print('>>> Timeout')
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
    
    probes = sorted(set(probes))
    print(f'\nZnalezione steps: {probes}')
    
    if 0 in probes:
        print('SPIRALA R=1: PASS (znaleziono step=0)')
        return True
    else:
        print('SPIRALA R=1: FAIL (brak step=0)')
        return False

if __name__ == '__main__':
    build_spiral_r1()
    success = run_server_test()
    sys.exit(0 if success else 1)
