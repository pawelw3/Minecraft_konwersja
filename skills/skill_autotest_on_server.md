# SKILL: Automated Testing on Headless Minecraft Server

This skill documents the workflow for creating, deploying, and verifying automated tests on a headless Minecraft server using RCON remote control and log analysis.

## Overview

This workflow enables testing of in-game mechanics (redstone circuits, command blocks, mod behaviors) without requiring manual player interaction. Tests are activated via RCON commands and results are verified through server logs.

## Target Environment

| Parameter | Value | Notes |
|-----------|-------|-------|
| Minecraft Version | 1.7.10 | Can be adapted for other versions |
| Server Type | Forge Headless | Vanilla also supported |
| Communication | RCON (Remote Console) | Enables command injection |
| Map Editing | Kotlin/Hephaistos | For placing test structures |
| Verification | Log parsing | grep/select-string for patterns |

## Architecture

```
Test Definition (JSON Patch)
       ↓
Map Editor (Kotlin Worker)
       ↓
World Files (MCA format)
       ↓
Headless Server + RCON
       ↓
Command Injection (/setblock)
       ↓
In-Game Mechanism Activation
       ↓
Log Output Verification
```

## Step-by-Step Workflow

### Step 1: Design Test Circuit

**Principles:**
- Test must be **initially disabled** (no active power source at placement)
- Power source should be placeable via `/setblock` command
- Output must be observable in logs (command blocks with `/say`)
- Use distinct markers in output (e.g., `[TEST1]`, `[TEST2]`)

**Example Circuit Structure:**
```
[POWER_SOURCE_SLOT] → [REDSTONE_DUST:0] → [REPEATER] → ... → [COMMAND_BLOCK]
```

**Key Design Decisions:**
- First redstone dust has meta=0 (unpowered) - gets activated when power source is placed
- No levers/buttons - everything triggered via RCON `/setblock`
- Command blocks use `/say [TEST_ID] message` for log visibility

### Step 2: Generate Patch

Use the Python generator to create a test patch:

```python
from generate_patch import generate_redstone_test_patch

patch = generate_redstone_test_patch(
    offset_x=600,           # Position (avoid spawn chunks if possible)
    offset_y=70,
    offset_z=-100,
    wire_length=3,          # Redstone segments between repeaters
    repeater_count=2,       # Number of repeaters (delay)
    power_source='redstone_torch',  # What will be placed via RCON
    command_msg='/say [TEST1] Test message',
    name='Test 1'
)
```

**Important:** The generator creates:
- Empty slot for power source (stone base only)
- Unpowered redstone at position +1
- Powered redstone (meta=15) for rest of circuit
- Command block with Tile Entity at the end

### Step 3: Deploy to World

```bash
cd jvm/worker
java -jar mc-editkit-worker.jar \
    --world ../../map_read_write_tests/kimi1 \
    --patch ../../test_scenarios/test1_rcon.json
```

**Verify placement:**
```bash
java -jar mc-editkit-worker.jar \
    --world ../../map_read_write_tests/kimi1 \
    --verify-block 600 70 -100 1 0  # Should be stone (empty slot)
```

### Step 4: Configure Server

**server.properties:**
```properties
enable-command-block=true
enable-rcon=true
rcon.password=your_secure_password
rcon.port=25579
server-port=25569
online-mode=false
level-name=world
```

**Copy world:**
```bash
xcopy /E /I map_read_write_tests/kimi1 headless_server/1.7.10/world
```

### Step 5: Start Server

```bash
cd headless_server/1.7.10
java -Xms1G -Xmx2G -jar minecraft_server.1.7.10.jar nogui
```

**Wait for:** `[RCON Listener #1/INFO]: RCON running on 0.0.0.0:25579`

### Step 6: Activate Tests via RCON

Python RCON client:
```python
import socket
import struct
import time

def send_rcon(host, port, password, command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect((host, port))
        
        # Authenticate
        auth = struct.pack('<ii', 0, 3) + password.encode() + b'\x00\x00'
        sock.send(struct.pack('<i', len(auth)) + auth)
        sock.recv(1024)  # Auth response
        
        # Send command
        cmd = struct.pack('<ii', 1, 2) + command.encode() + b'\x00\x00'
        sock.send(struct.pack('<i', len(cmd)) + cmd)
        
        # Get response
        data = sock.recv(4)
        resp_len = struct.unpack('<i', data)[0]
        resp = sock.recv(resp_len)
        return resp[8:-2].decode('utf-8', errors='ignore')
    finally:
        sock.close()

# Activate Test 1
result = send_rcon('127.0.0.1', 25579, 'test123', 
                   'setblock 600 70 -100 minecraft:redstone_torch 5')
print(result)  # "Block placed"

# Wait for signal propagation
time.sleep(2)

# Activate Test 2
result = send_rcon('127.0.0.1', 25579, 'test123',
                   'setblock 650 70 -100 minecraft:redstone_torch 5')
```

### Step 7: Verify Results

Check logs for test markers:
```powershell
cd headless_server/1.7.10
Select-String -Path logs/latest.log -Pattern "TEST1|TEST2" | Select-Object -Last 10
```

**Expected output:**
```
[23:32:51] [Server thread/INFO]: [@] [TEST1] Układ testowy #1 RCON - DZIAŁA!
[23:32:54] [Server thread/INFO]: [@] [TEST2] Układ testowy #2 RCON (12 repeaterów) - DZIAŁA!
```

## Test Patterns

### Pattern 1: Simple Signal Test
```
Torch → Redstone → Command Block
```
Purpose: Verify basic redstone propagation

### Pattern 2: Delay Chain Test
```
Torch → Redstone → Repeater × N → Command Block
```
Purpose: Test repeater timing, measure propagation delay

### Pattern 3: Multi-Stage Test
```
Torch → Stage 1 → Detector → Stage 2 → Command Block
```
Purpose: Test complex mechanisms, item transport, etc.

## Best Practices

### Do:
- ✅ Place tests away from spawn (different regions if possible)
- ✅ Use distinct test IDs in command output
- ✅ Include circuit metadata in patch JSON
- ✅ Use appropriate delays between test activations
- ✅ Verify block placement before server start
- ✅ Use meta=0 for initially unpowered redstone

### Don't:
- ❌ Place active power sources (circuits will trigger during chunk load)
- ❌ Use random tick dependent blocks (unpredictable)
- ❌ Overlap test regions (may cause interference)
- ❌ Forget to enable `enable-command-block` in server.properties
- ❌ Use weak power sources for long chains (signal may not reach)

## Troubleshooting

### Issue: No output in logs
**Check:**
1. Is command-block enabled in server.properties?
2. Was the chunk loaded? (May need player nearby or spawn chunks)
3. Is the circuit actually powered? (Verify with `/blockdata`)
4. Check for broken redstone connections

### Issue: RCON connection refused
**Check:**
1. Is server fully started? (Wait for "Done!" message)
2. Is rcon.password set?
3. Is correct port used? (rcon.port vs server-port)
4. Firewall blocking 25579?

### Issue: Signal doesn't propagate
**Check:**
1. Redstone dust on proper support block (stone, not air)
2. Repeater orientation (must face toward command block)
3. Signal strength - max 15 blocks, use repeaters
4. Chunk boundaries - redstone may not update across unloaded chunks

## Code Templates

### Generate Test Patch
See: `test_scenarios/redstone_command_block_test/generate_patch.py`

### RCON Client
See conversation for full implementation using `socket` + `struct`

### Log Monitor
```python
import time

def wait_for_log_marker(log_path, marker, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if marker in content:
                return True
        time.sleep(0.5)
    return False
```

## Integration with CI/CD

This workflow can be automated:

```yaml
# Example CI pipeline
steps:
  1. Build test patches
  2. Deploy to world
  3. Start headless server
  4. Wait for "Done!"
  5. Activate tests via RCON
  6. Parse logs for PASS/FAIL markers
  7. Generate report
  8. Stop server
```

## References

- RCON Protocol: https://wiki.vg/RCON
- Minecraft 1.7.10 Block IDs: https://minecraft.wiki/
- Hephaistos Library: https://github.com/jglrxavpok/Hephaistos

---
*Skill based on practical testing workflow developed for Minecraft map conversion project.*
