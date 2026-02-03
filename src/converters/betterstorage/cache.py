"""
Cache i optymalizacje dla konwertera Better Storage.

Zapewnia:
- Cache'owanie danych Crate Pile
- Cache'owanie wyników konwersji
- Batch processing z minimalnym I/O
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from functools import wraps
import time


@dataclass
class CacheEntry:
    """Pojedynczy wpis w cache"""
    key: str
    value: Any
    timestamp: float
    hits: int = 0


class SimpleCache:
    """Prosty cache w pamięci z limitem czasu życia"""
    
    def __init__(self, max_size: int = 1000, ttl: float = 3600):
        """
        Args:
            max_size: Maksymalna liczba wpisów
            ttl: Czas życia wpisu w sekundach (Time To Live)
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, CacheEntry] = {}
    
    def _make_key(self, *args, **kwargs) -> str:
        """Tworzy klucz cache z argumentów"""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Pobiera wartość z cache"""
        entry = self._cache.get(key)
        if entry is None:
            return None
        
        # Sprawdzamy czy nie wygasło
        if time.time() - entry.timestamp > self.ttl:
            del self._cache[key]
            return None
        
        entry.hits += 1
        return entry.value
    
    def set(self, key: str, value: Any):
        """Ustawia wartość w cache"""
        # Sprzątamy jeśli pełne
        if len(self._cache) >= self.max_size:
            self._cleanup()
        
        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            timestamp=time.time()
        )
    
    def _cleanup(self):
        """Usuwa najstarsze/najrzadziej używane wpisy"""
        # Usuwamy wygasłe
        now = time.time()
        expired = [
            k for k, v in self._cache.items() 
            if now - v.timestamp > self.ttl
        ]
        for k in expired:
            del self._cache[k]
        
        # Jeśli nadal pełne, usuwamy połowę najrzadziej używanych
        if len(self._cache) >= self.max_size:
            sorted_items = sorted(
                self._cache.items(), 
                key=lambda x: x[1].hits
            )
            to_remove = len(sorted_items) // 2
            for k, _ in sorted_items[:to_remove]:
                del self._cache[k]
    
    def clear(self):
        """Czyści cały cache"""
        self._cache.clear()
    
    def stats(self) -> Dict[str, int]:
        """Zwraca statystyki cache"""
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'total_hits': sum(e.hits for e in self._cache.values()),
        }


class CratePileCache:
    """
    Wyspecjalizowany cache dla danych Crate Pile.
    
    Cache'uje dane z plików data/crates/<id>.dat aby uniknąć
    wielokrotnego odczytu tych samych plików.
    """
    
    def __init__(self, crate_pile_loader, max_size: int = 100):
        self.loader = crate_pile_loader
        self.cache = SimpleCache(max_size=max_size, ttl=7200)  # 2h TTL
        self._loaded_piles: set = set()
    
    def get_pile(self, pile_id: int):
        """Pobiera dane pile (z cache lub z dysku)"""
        cache_key = f"pile_{pile_id}"
        
        # Sprawdzamy cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Ładujemy z dysku
        pile_data = self.loader.get_pile(pile_id)
        
        if pile_data:
            self.cache.set(cache_key, pile_data)
            self._loaded_piles.add(pile_id)
        
        return pile_data
    
    def preload_all_piles(self):
        """Preloaduje wszystkie pliki crate pile do cache"""
        piles = self.loader.load_all_piles()
        for pile_id, pile_data in piles.items():
            self.cache.set(f"pile_{pile_id}", pile_data)
            self._loaded_piles.add(pile_id)
        return len(piles)
    
    def get_loaded_count(self) -> int:
        """Zwraca liczbę załadowanych pile"""
        return len(self._loaded_piles)


class ConversionCache:
    """
    Cache dla wyników konwersji.
    
    Przydatny gdy te same bloki mogą być konwertowane wielokrotnie
    (np. podczas iteracyjnej konwersji chunków).
    """
    
    def __init__(self, max_size: int = 10000):
        self.cache = SimpleCache(max_size=max_size, ttl=1800)  # 30min TTL
    
    def _make_block_key(
        self, 
        block_id: str, 
        nbt_data: Dict[str, Any],
        x: int, 
        y: int, 
        z: int
    ) -> str:
        """Tworzy unikalny klucz dla bloku"""
        # Używamy hash NBT + współrzędnych
        nbt_hash = hashlib.md5(
            json.dumps(nbt_data, sort_keys=True).encode()
        ).hexdigest()[:16]
        return f"{block_id}:{x}:{y}:{z}:{nbt_hash}"
    
    def get_cached_result(
        self,
        block_id: str,
        nbt_data: Dict[str, Any],
        x: int,
        y: int,
        z: int
    ) -> Optional[Dict[str, Any]]:
        """Pobiera wynik konwersji z cache"""
        key = self._make_block_key(block_id, nbt_data, x, y, z)
        return self.cache.get(key)
    
    def cache_result(
        self,
        block_id: str,
        nbt_data: Dict[str, Any],
        x: int,
        y: int,
        z: int,
        result: Dict[str, Any]
    ):
        """Zapisuje wynik konwersji w cache"""
        key = self._make_block_key(block_id, nbt_data, x, y, z)
        self.cache.set(key, result)


def cached_conversion(cache_attr: str = '_conversion_cache'):
    """
    Dekorator do cache'owania wyników konwersji.
    
    Usage:
        class MyConverter:
            def __init__(self):
                self._conversion_cache = ConversionCache()
            
            @cached_conversion()
            def convert_block(self, block_id, nbt, x, y, z):
                ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cache = getattr(self, cache_attr, None)
            if cache is None:
                return func(self, *args, **kwargs)
            
            # Ekstrahujemy argumenty
            if len(args) >= 5:
                block_id, nbt, x, y, z = args[0], args[1], args[2], args[3], args[4]
            else:
                return func(self, *args, **kwargs)
            
            # Sprawdzamy cache
            cached = cache.get_cached_result(block_id, nbt, x, y, z)
            if cached is not None:
                return cached
            
            # Wykonujemy konwersję
            result = func(self, *args, **kwargs)
            
            # Zapisujemy w cache
            cache.cache_result(block_id, nbt, x, y, z, result)
            
            return result
        return wrapper
    return decorator


class OptimizedCratePileLoader:
    """
    Zoptymalizowany loader Crate Pile z prefetchingiem.
    
    Ładuje dane crate pile z wyprzedzeniem aby zminimalizować I/O.
    """
    
    def __init__(self, crate_pile_loader, prefetch: bool = True):
        self.loader = crate_pile_loader
        self.cache = CratePileCache(crate_pile_loader)
        
        if prefetch:
            self._prefetch()
    
    def _prefetch(self):
        """Preloaduje wszystkie pliki crate pile"""
        count = self.cache.preload_all_piles()
        print(f"Preloaded {count} crate piles into cache")
    
    def get_pile(self, pile_id: int):
        """Pobiera dane pile (z cache)"""
        return self.cache.get_pile(pile_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki"""
        return {
            'cached_piles': self.cache.get_loaded_count(),
            'cache_stats': self.cache.cache.stats(),
        }


# Cache globalny dla całego procesu konwersji
_global_cache: Optional[SimpleCache] = None


def get_global_cache() -> SimpleCache:
    """Zwraca globalny cache (tworzy jeśli potrzeba)"""
    global _global_cache
    if _global_cache is None:
        _global_cache = SimpleCache(max_size=5000, ttl=3600)
    return _global_cache


def clear_global_cache():
    """Czyści globalny cache"""
    global _global_cache
    if _global_cache:
        _global_cache.clear()
