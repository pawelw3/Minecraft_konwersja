# Thermal Dynamics — Pełna lista bloków i Tile Entities

> **Dokumentacja konwersji Thermal Dynamics: 1.7.10 → 1.18.2**  
> **Zadanie 1:** Wypisanie wszystkich bloków i Tile Entities  
> **Data utworzenia:** 2026-05-19  
> **Status:** ✅ Ukończono (krok 1)

---

## Spis treści

1. [Architektura Thermal Dynamics — przegląd](#1-architektura-thermal-dynamics--przegląd)
2. [Bloki i Tile Entities — mapowanie 1.7.10 → 1.18.2](#2-bloki-i-tile-entities--mapowanie-1710--1182)
3. [Szczegółowy opis funkcjonalności](#3-szczegółowy-opis-funkcjonalności)
4. [Struktura NBT — kluczowe różnice](#4-struktura-nbt--kluczowe-różnice)
5. [Itemy / Załączniki (Attachments)](#5-itemy--załączniki-attachments)
6. [Weryfikacja na podstawie kodu źródłowego / dekompilacji](#6-weryfikacja-na-podstawie-kodu-źródłowego--dekompilacji)

---

## 1. Architektura Thermal Dynamics — przegląd

Thermal Dynamics 1.7.10 dostarcza system **ductów** (rur) do transportu:
- **Energii (RF)** — Fluxducts
- **Płynów** — Fluiducts
- **Itemów** — Itemducts
- **Bytów (Entity)** — Transport Ducts (Viaducts)
- **Strukturalne** — Structuralduct / Light Duct

Wszystkie ducty w 1.7.10 dzielą **5 instancji bloku** (`BlockDuct` z różnym `offset`), a konkretny typ jest określany przez **metadata** (0–15 względem offsetu).

### Kluczowe różnice 1.7.10 → 1.18.2

| Aspekt | 1.7.10 | 1.18.2 (v9.2.2) |
|--------|--------|-----------------|
| Rejestracja bloków | 5× `BlockDuct` + metadata | Osobne bloki per typ |
| Tile Entities | Per-typ TE (12 klas) | `EnergyDuctBlockEntity`, `FluidDuctBlockEntity`, `FluidDuctWindowedBlockEntity`, `ItemBufferBlockEntity` |
| Itemducty | Są jako bloki | **BRAK bloku `item_duct`** — w wersji 9.2.2 nie zaimplementowano |
| Transport (Viaduct) | Są jako bloki | **BRAK** — nie zaimplementowano |
| Załączniki | Servo, Filter, Retriever | Servo, Filter, Energy Limiter (jako itemy/załączniki) |

---

## 2. Bloki i Tile Entities — mapowanie 1.7.10 → 1.18.2

### 2.1 Bloki ductów w 1.7.10

W 1.7.10 wszystkie ducty używają wspólnego bloku rejestrowanego jako:
```
ThermalDynamics:thermaldynamics.Duct{offset}
```
gdzie `offset ∈ {0, 16, 32, 48, 64}`.

| Offset | Blok 1.7.10 | Zakres metadata | Zakres ID wewnętrznych |
|--------|-------------|-----------------|------------------------|
| 0 | `ThermalDynamics:thermaldynamics.Duct0` | 0–15 | 0–15 (Energy) |
| 16 | `ThermalDynamics:thermaldynamics.Duct16` | 0–15 | 16–31 (Fluid) |
| 32 | `ThermalDynamics:thermaldynamics.Duct32` | 0–15 | 32–47 (Item) |
| 48 | `ThermalDynamics:thermaldynamics.Duct48` | 0–15 | 48–63 (Structure) |
| 64 | `ThermalDynamics:thermaldynamics.Duct64` | 0–15 | 64–79 (Transport) |

### 2.2 Mapowanie Energy Ducts (offset 0)

| Meta | ID wewn. | Nazwa 1.7.10 | Blok 1.18.2 | Uwagi |
|------|----------|--------------|-------------|-------|
| 0 | 0 | Leadstone Fluxduct | `thermal:energy_duct` | Uproszczony system tierów |
| 1 | 1 | Hardened Fluxduct | `thermal:energy_duct` | |
| 2 | 2 | Redstone Energy Fluxduct | `thermal:energy_duct` | |
| 3 | 3 | Reinforced Fluxduct (empty) | — | Crafting item, nie umieszczany |
| 4 | 4 | Signalum Fluxduct | `thermal:energy_duct` | |
| 5 | 5 | Resonant Fluxduct (empty) | — | Crafting item |
| 6 | 6 | Cryo-Stabilized Fluxduct | `thermal:energy_duct` | |
| 7 | 7 | Cryo-Stabilized (empty) | — | Crafting item |

**Tile Entity 1.7.10:** `thermaldynamics.FluxDuct` (zwykłe), `thermaldynamics.FluxDuctSuperConductor` (Cryo)
**Tile Entity 1.18.2:** `thermal:energy_duct`

### 2.3 Mapowanie Fluid Ducts (offset 16)

| Meta | ID wewn. | Nazwa 1.7.10 | Blok 1.18.2 | Uwagi |
|------|----------|--------------|-------------|-------|
| 0 | 16 | Temperate Fluiduct | `thermal:fluid_duct` | |
| 1 | 17 | Temperate Fluiduct (opaque) | `thermal:fluid_duct` | Opaque = nieprzezroczysty |
| 2 | 18 | Hardened Fluiduct | `thermal:fluid_duct` | |
| 3 | 19 | Hardened Fluiduct (opaque) | `thermal:fluid_duct` | |
| 4 | 20 | Flux-Plated Fluiduct | `thermal:fluid_duct` | Przewodzi RF+fluid |
| 5 | 21 | Flux-Plated Fluiduct (opaque) | `thermal:fluid_duct` | |
| 6 | 22 | Super-Laminar Fluiduct | `thermal:fluid_duct_windowed` | |
| 7 | 23 | Super-Laminar Fluiduct (opaque) | `thermal:fluid_duct_windowed` | |

**Tile Entity 1.7.10:** `thermaldynamics.FluidDuct`, `thermaldynamics.FluidDuctFragile`, `thermaldynamics.FluidDuctFlux`, `thermaldynamics.FluidDuctSuper`
**Tile Entity 1.18.2:** `thermal:fluid_duct`, `thermal:fluid_duct_windowed`

### 2.4 Mapowanie Item Ducts (offset 32) — 🔴 PROBLEM

| Meta | ID wewn. | Nazwa 1.7.10 | Blok 1.18.2 | Uwagi |
|------|----------|--------------|-------------|-------|
| 0 | 32 | Itemduct | **BRAK** | 🔴 Nie ma `item_duct` w TD 9.2.2 |
| 1 | 33 | Itemduct (opaque) | **BRAK** | 🔴 |
| 2 | 34 | Impulse Itemduct | **BRAK** | 🔴 |
| 3 | 35 | Impulse Itemduct (opaque) | **BRAK** | 🔴 |
| 4 | 36 | Ender Itemduct | **BRAK** | 🔴 |
| 5 | 37 | Ender Itemduct (opaque) | **BRAK** | 🔴 |
| 6 | 38 | Flux-Plated Itemduct | **BRAK** | 🔴 |
| 7 | 39 | Flux-Plated Itemduct (opaque) | **BRAK** | 🔴 |

**Tile Entity 1.7.10:** `thermaldynamics.ItemDuct`, `thermaldynamics.ItemDuctEnder`, `thermaldynamics.ItemDuctFlux`

> **Krytyczne odkrycie:** W analizowanej wersji Thermal Dynamics 1.18.2 (9.2.2.19) **nie istnieje blok `item_duct`**. Jest tylko `item_buffer` (blok bufora itemów). Oznacza to, że Itemducty z 1.7.10 wymagają:
> - konwersji na inny mod (np. Pipez, Mekanism Logistical Transporter), lub
> - zamiany na placeholdery + ręcznej rekonstrukcji.

### 2.5 Mapowanie Structural Ducts (offset 48)

| Meta | ID wewn. | Nazwa 1.7.10 | Blok 1.18.2 | Uwagi |
|------|----------|--------------|-------------|-------|
| 0 | 48 | Structuralduct | **BRAK** | 🔴 Nie ma odpowiednika w TD 9.2.2 |
| 1 | 49 | Glowstone Illuminator | **BRAK** | 🔴 |

**Tile Entity 1.7.10:** `thermaldynamics.StructuralDuct`

### 2.6 Mapowanie Transport Ducts (offset 64) — 🔴 PROBLEM

| Meta | ID wewn. | Nazwa 1.7.10 | Blok 1.18.2 | Uwagi |
|------|----------|--------------|-------------|-------|
| 0 | 64 | Viaduct | **BRAK** | 🔴 Nie zaimplementowano |
| 1 | 65 | Long-Range Viaduct | **BRAK** | 🔴 |
| 2 | 66 | Accelerated Viaduct | **BRAK** | 🔴 |
| 3 | 67 | Viaduct (crafting) | **BRAK** | 🔴 |

**Tile Entity 1.7.10:** `thermaldynamics.TransportDuct`, `thermaldynamics.TransportDuctLongRange`, `thermaldynamics.TransportDuctCrossover`

---

## 3. Szczegółowy opis funkcjonalności

### 3.1 Energy Ducts (Fluxducts)

**1.7.10:**
- System tierów: Leadstone → Hardened → Redstone Energy → Signalum → Resonant → Cryo-Stabilized
- Cryo-Stabilized przewodzi **nieograniczoną** ilość RF
- Wszystkie używają `TileEnergyDuct` lub `TileEnergyDuctSuper`
- NBT: przechowuje informacje o sieci (grid), połączeniach, załącznikach

**1.18.2:**
- Jeden blok `thermal:energy_duct` — system tierów został uproszczony / przeniesiony na załączniki
- `EnergyDuctBlockEntity` obsługuje sieć energii (Forge Energy / FE)

**Konwersja:** Bezpośrednia zamiana bloku → `thermal:energy_duct`. Dane o sieci nie są przenośne (zostaną odtworzone przez nowy grid system).

### 3.2 Fluid Ducts (Fluiducts)

**1.7.10:**
- Temperate (miedź) — podstawowe, kruche przy ekstremalnych temperaturach
- Hardened (invar) — odporne na gorące/chłodne płyny
- Flux-Plated — przewodzi jednocześnie fluid i RF
- Super-Laminar — bardzo wysoka przepustowość

**1.18.2:**
- `thermal:fluid_duct` — podstawowe/hardened/flux
- `thermal:fluid_duct_windowed` — wersja z okienkiem (wizualnie przezroczysta)

**Konwersja:** Mapowanie typu na odpowiedni blok. Załączniki (servo/fluid servo) wymagają osobnej konwersji.

### 3.3 Item Ducts (Itemducts) — 🔴 KRYTYCZNE

**1.7.10:**
- Itemduct — podstawowy transport itemów
- Impulse Itemduct — przyspieszony transport
- Ender Itemduct — teleportacja między odległymi punktami
- Flux-Plated Itemduct — transport itemów + RF
- System routingu: najkrótsza ścieżka, round-robin, losowo, itp.
- Załączniki: Servo (ekstrakcja), Filter, Retriever

**1.18.2:**
- **Brak bloku item duct** w wersji 9.2.2
- Jest `item_buffer` — bufor/item manifold, nie rura transportowa

**Konwersja:** Wymaga decyzji architektonicznej — prawdopodobnie remap na `pipez:item_pipe` lub `mekanism:logistical_transporter`, albo placeholder.

### 3.4 Structural / Light Ducts

**1.7.10:**
- Structuralduct — dekoracyjny/blokujący, można nakładać cover'y
- Glowstone Illuminator — świecący duct

**1.18.2:**
- Brak odpowiednika.

**Konwersja:** Placeholder dekoracyjny lub usunięcie.

### 3.5 Transport Ducts (Viaducts)

**1.7.10:**
- Przenoszenie graczy i mobów przez rury
- Viaduct, Long-Range, Crossover (przyspieszenie)

**1.18.2:**
- Brak odpowiednika.

**Konwersja:** Placeholder lub usunięcie.

---

## 4. Struktura NBT — kluczowe różnice

### 4.1 Ogólna struktura Tile Entity 1.7.10

```nbt
{
  "id": "thermaldynamics.FluxDuct",
  "x": int, "y": int, "z": int,
  "Connections": [byte, byte, byte, byte, byte, byte],  // typy połączeń per strona
  "Attachment": [compound, compound, compound, compound, compound, compound],  // załączniki per strona
  "Grid": long  // identyfikator sieci
}
```

### 4.2 Struktura załącznika (Servo/Filter) 1.7.10

```nbt
{
  "id": byte,           // typ załącznika (1=Servo, 2=Filter, 3=Retriever, ...)
  "side": byte,         // strona
  "threshold": int,
  "filter": {
    "items": [...],     // filtr itemów
    "flags": int        // flagi filtru (whitelist/blacklist, NBT, meta, oreDict)
  },
  "speed": byte,
  "rsMode": byte        // tryb redstone
}
```

### 4.3 Struktura Tile Entity 1.18.2

```nbt
{
  "id": "thermal:energy_duct",
  "x": int, "y": int, "z": int,
  // Dane gridu są przechowywane w osobnym systemie (nie w NBT bloku)
  // Załączniki są osobnymi BlockEntity lub danymi w NBT
}
```

> **Uwaga:** W 1.18.2 Thermal Dynamics używa osobnego systemu gridów (nie przechowywanych w NBT poszczególnych bloków). Grid jest odtwarzany dynamicznie na podstawie połączeń sąsiednich bloków.

---

## 5. Itemy / Załączniki (Attachments)

### 5.1 Załączniki 1.7.10

| Załącznik | Funkcja |
|-----------|---------|
| Servo | Ekstrakcja z inventory do ductu |
| Filter | Filtrowanie przepływu |
| Retriever | "Ciągnięcie" itemów z sieci |
| Relay | Przekazywanie sygnału redstone |

### 5.2 Załączniki 1.18.2 (dostępne w kodzie)

| ID | Nazwa |
|----|-------|
| `thermal:servo_attachment` | Servo |
| `thermal:turbo_servo_attachment` | Turbo Servo |
| `thermal:filter_attachment` | Filter |
| `thermal:energy_limiter_attachment` | Energy Limiter |
| `thermal:fluid_servo_attachment` | Fluid Servo |
| `thermal:fluid_turbo_servo_attachment` | Fluid Turbo Servo |
| `thermal:fluid_filter_attachment` | Fluid Filter |

> **Uwaga:** Załączniki w 1.18.2 są prawdopodobnie implementowane jako dane NBT w bloku ductu lub jako osobne blockstate, a nie jako osobne Tile Entities.

---

## 6. Weryfikacja na podstawie kodu źródłowego / dekompilacji

### 6.1 Źródła

**1.7.10:** Dekompilacja `ThermalDynamics-[1.7.10]1.2.1-172.jar`
- Klasa `cofh.thermaldynamics.duct.TDDucts` — pełna lista 34 ductów z offsetami i metadata
- Klasa `cofh.thermaldynamics.duct.BlockDuct` — rejestracja bloków jako `thermaldynamics.Duct{offset}`
- Klasa `cofh.thermaldynamics.ThermalDynamics` — rejestracja TE:
  - `thermaldynamics.FluxDuct`
  - `thermaldynamics.FluxDuctSuperConductor`
  - `thermaldynamics.FluidDuct`
  - `thermaldynamics.FluidDuctFragile`
  - `thermaldynamics.FluidDuctFlux`
  - `thermaldynamics.FluidDuctSuper`
  - `thermaldynamics.ItemDuct`
  - `thermaldynamics.ItemDuctEnder`
  - `thermaldynamics.ItemDuctFlux`
  - `thermaldynamics.StructuralDuct`
  - `thermaldynamics.TransportDuct`
  - `thermaldynamics.TransportDuctLongRange`
  - `thermaldynamics.TransportDuctCrossover`

**1.18.2:** Analiza źródła `thermal_dynamics-1.18.2-9.2.2.19.jar`
- `TDynBlocks.java` — rejestruje: `energy_duct`, `fluid_duct`, `fluid_duct_windowed`, `item_buffer`
- `TDynBlockEntities.java` — `EnergyDuctBlockEntity`, `FluidDuctBlockEntity`, `FluidDuctWindowedBlockEntity`, `ItemBufferBlockEntity`
- `TDynIDs.java` — brak `ID_ITEM_DUCT`, brak `ID_STRUCTURE_DUCT`, brak `ID_TRANSPORT_DUCT`

### 6.2 Niezgodność z wcześniejszą dokumentacją

Wcześniejsza dokumentacja projektu (`docs/ANALIZA_MODOW_SZCZEGOLOWA.md`) zakładała istnienie:
- `thermal:item_duct`
- `thermal:item_duct_fast`
- `thermal:structure_duct`

**Weryfikacja kodu źródłowego 1.18.2 pokazuje, że te bloki NIE ISTNIEJĄ** w wersji 9.2.2.19.

---

## 7. Podsumowanie konwersji — priorytety

| Priorytet | Element | Strategia |
|-----------|---------|-----------|
| 🟢 NISKI | Energy Ducts | `thermal:energy_duct` (bezpośrednia zamiana) |
| 🟢 NISKI | Fluid Ducts | `thermal:fluid_duct` / `thermal:fluid_duct_windowed` |
| 🔴 KRYTYCZNY | Item Ducts | **Brak odpowiednika** — wymaga decyzji (Pipez? Placeholder?) |
| 🟡 WYSOKI | Załączniki (Servo/Filter) | Konwersja na nowe załączniki 1.18.2 lub zrzut do skrzyń |
| 🟡 WYSOKI | Structural / Light | Placeholder / usunięcie |
| 🔴 KRYTYCZNY | Transport (Viaduct) | **Brak odpowiednika** — usunięcie lub placeholder |

---

*Dokumentacja przygotowana na podstawie:*
- *Dekompilacji JAR ThermalDynamics 1.7.10 (vineflower)*
- *Analizy kodu źródłowego ThermalDynamics 1.18.2 (repo + JAR)*
- *Weryfikacji rejestrów bloków i Tile Entities*

*Plik utworzony przez: Agent AI Konwersji — Zadanie 1 (Thermal Dynamics)*
