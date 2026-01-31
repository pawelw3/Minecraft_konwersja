#!/usr/bin/env python3
"""
Test wykonujący setblock na każdym istniejącym chunku mapy.
Dla każdego chunka: pozycja (chunkX*16+5, 40, chunkZ*16+5)
"""

import socket
import struct
import time
import json
from pathlib import Path
from datetime import datetime

def get_existing_chunks(world_path):
    """Znajduje wszystkie istniejące chunki w plikach MCA."""
    region_dir = Path(world_path) / "region"
    chunks = []
    
    for mca_file in sorted(region_dir.glob("r.*.*.mca")):
        # Parse region filename: r.X.Z.mca
        parts = mca_file.stem.split(".")
        region_x, region_z = int(parts[1]), int(parts[2])
        
        # Odczytaj nagłówek regionu
        with open(mca_file, "rb") as f:
            header = f.read(4096)  # Pierwsze 4KB to tablica lokalizacji
            
        # Sprawdź każdy z 1024 możliwych chunków w regionie
        for local_x in range(32):
            for local_z in range(32):
                index = local_x + local_z * 32
                offset = (header[index * 4] << 16) | (header[index * 4 + 1] << 8) | header[index * 4 + 2]
                
                if offset != 0:  # Chunk istnieje
                    chunk_x = region_x * 32 + local_x
                    chunk_z = region_z * 32 + local_z
                    
                    # Oblicz pozycję testową w chunku (x:5, y:40, z:5)
                    test_x = chunk_x * 16 + 5
                    test_y = 40
                    test_z = chunk_z * 16 + 5
                    
                    chunks.append({
                        "region_x": region_x,
                        "region_z": region_z,
                        "local_x": local_x,
                        "local_z": local_z,
                        "chunk_x": chunk_x,
                        "chunk_z": chunk_z,
                        "test_x": test_x,
                        "test_y": test_y,
                        "test_z": test_z,
                        "command": f"/setblock {test_x} {test_y} {test_z} minecraft:redstone_block 0"
                    })
    
    return chunks

def send_rcon_command(host, port, password, command, timeout=10):
    """Wysyła komendę RCON i zwraca wynik."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        sock.connect((host, port))
        
        # Autentykacja
        auth_packet = struct.pack('<ii', 0, 3) + password.encode() + b'\x00\x00'
        auth_len = struct.pack('<i', len(auth_packet))
        sock.send(auth_len + auth_packet)
        
        # Odpowiedź auth
        resp_len = struct.unpack('<i', sock.recv(4))[0]
        auth_resp = sock.recv(resp_len)
        auth_id = struct.unpack('<i', auth_resp[:4])[0]
        
        if auth_id == -1:
            return {"success": False, "error": "Auth failed"}
        
        # Wyślij komendę
        cmd_packet = struct.pack('<ii', 1, 2) + command.encode() + b'\x00\x00'
        cmd_len = struct.pack('<i', len(cmd_packet))
        sock.send(cmd_len + cmd_packet)
        
        # Odpowiedź
        resp_len_data = sock.recv(4)
        if len(resp_len_data) < 4:
            return {"success": False, "error": "No response"}
        
        resp_len = struct.unpack('<i', resp_len_data)[0]
        resp = sock.recv(resp_len)
        
        if len(resp) < 8:
            return {"success": False, "error": "Invalid response"}
        
        body = resp[8:-2].decode('utf-8', errors='ignore')
        return {"success": True, "response": body}
        
    except socket.timeout:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        sock.close()

def run_chunk_test(world_path, rcon_host, rcon_port, rcon_password, delay=0.1):
    """Główna funkcja testująca wszystkie chunki."""
    
    print("=" * 70)
    print("CHUNK SETBLOCK TEST - RAPORT")
    print("=" * 70)
    print(f"Czas startu: {datetime.now().isoformat()}")
    print(f"Świat: {world_path}")
    print(f"RCON: {rcon_host}:{rcon_port}")
    print()
    
    # Znajdź wszystkie chunki
    print("Szukanie istniejących chunków...")
    chunks = get_existing_chunks(world_path)
    print(f"Znaleziono {len(chunks)} chunków")
    print()
    
    # Wyniki
    results = {
        "start_time": datetime.now().isoformat(),
        "total_chunks": len(chunks),
        "world_path": str(world_path),
        "rcon_host": rcon_host,
        "rcon_port": rcon_port,
        "chunks": [],
        "summary": {
            "success": 0,
            "failed": 0,
            "block_placed": 0,
            "cannot_place": 0,
            "other": 0
        }
    }
    
    # Testuj każdy chunk
    print("Wykonywanie komend setblock...")
    print("-" * 70)
    
    for i, chunk in enumerate(chunks, 1):
        result = send_rcon_command(rcon_host, rcon_port, rcon_password, chunk["command"])
        
        chunk_result = {
            "chunk_x": chunk["chunk_x"],
            "chunk_z": chunk["chunk_z"],
            "position": f"({chunk['test_x']}, {chunk['test_y']}, {chunk['test_z']})",
            "command": chunk["command"],
            "success": result["success"]
        }
        
        if result["success"]:
            response = result.get("response", "")
            chunk_result["response"] = response
            
            if "Block placed" in response:
                chunk_result["status"] = "BLOCK_PLACED"
                results["summary"]["block_placed"] += 1
            elif "cannot place" in response.lower() or "occupied" in response.lower():
                chunk_result["status"] = "CANNOT_PLACE"
                results["summary"]["cannot_place"] += 1
            else:
                chunk_result["status"] = "OTHER"
                results["summary"]["other"] += 1
            
            results["summary"]["success"] += 1
        else:
            chunk_result["error"] = result.get("error", "Unknown error")
            chunk_result["status"] = "FAILED"
            results["summary"]["failed"] += 1
        
        results["chunks"].append(chunk_result)
        
        # Progress
        if i % 100 == 0 or i == len(chunks):
            print(f"  Progress: {i}/{len(chunks)} ({i*100//len(chunks)}%) - "
                  f"OK:{results['summary']['success']} FAIL:{results['summary']['failed']}")
        
        # Delay to not overwhelm server
        if delay > 0:
            time.sleep(delay)
    
    print("-" * 70)
    print()
    
    # Podsumowanie
    results["end_time"] = datetime.now().isoformat()
    results["duration_seconds"] = (datetime.fromisoformat(results["end_time"]) - 
                                   datetime.fromisoformat(results["start_time"])).total_seconds()
    
    print("PODSUMOWANIE:")
    print(f"  Całkowity czas: {results['duration_seconds']:.2f}s")
    print(f"  Przetworzono chunków: {results['total_chunks']}")
    print(f"  Sukcesów: {results['summary']['success']}")
    print(f"  Niepowodzeń: {results['summary']['failed']}")
    print()
    print("Szczegóły wyników:")
    print(f"  Block placed: {results['summary']['block_placed']}")
    print(f"  Cannot place: {results['summary']['cannot_place']}")
    print(f"  Inne odpowiedzi: {results['summary']['other']}")
    print()
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test setblock na wszystkich chunkach")
    parser.add_argument("--world", default="../../map_read_write_tests/kimi1",
                       help="Ścieżka do świata Minecraft")
    parser.add_argument("--rcon-host", default="127.0.0.1")
    parser.add_argument("--rcon-port", type=int, default=25579)
    parser.add_argument("--rcon-password", default="test123")
    parser.add_argument("--delay", type=float, default=0.05,
                       help="Opóźnienie między komendami (sekundy)")
    parser.add_argument("--output", default="chunk_test_report.json",
                       help="Plik wyjściowy z raportem")
    
    args = parser.parse_args()
    
    results = run_chunk_test(
        args.world,
        args.rcon_host,
        args.rcon_port,
        args.rcon_password,
        args.delay
    )
    
    # Zapisz raport
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Raport zapisano do: {args.output}")
    
    return 0 if results["summary"]["failed"] == 0 else 1

if __name__ == "__main__":
    exit(main())
