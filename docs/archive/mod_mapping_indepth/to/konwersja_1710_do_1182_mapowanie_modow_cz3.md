# Konwersja świata 1.7.10 → 1.18.2 — mapowanie modów (część 3 / cz3)

> Zakres: tylko mody z listy **cz3** (Flan’s Mod, Forestry, ForgeEssentials, ForgeMultipart/Relocation, Growthcraft, IC2(+NuclearControl), Jammy Furniture, LiteLoader/litemody, LogisticsPipes, Mekanism, MobiusCore).  
> Cel: dobrać **mody 1.18.2 (Forge)** tak, aby dało się zbudować mapowanie bloków/block-entities i zachować *sens/treść* świata (budowle, maszyny, magazyny, farmy), nawet jeśli w części przypadków **nie da się zachować identycznego NBT** bez własnych skryptów konwersji.

## TL;DR — tabela „stary mod → nowy mod(y)”

| 1.7.10 mod | Rola/funkcjonalność | 1.18.2 (Forge) — docelowy mod/moduły | Ocena „bezstratności” bloków/BE |
|---|---|---|---|
| Flan’s Mod | bronie, pojazdy, content-packi | **Immersive Vehicles** (pojazdy + dekoracje) + **[TaCZ] Timeless and Classics Zero / Guns** (broń) + opcj. **Immersive Aircraft** (samoloty) | ❌ (w praktyce remap na inne bloki/encje) |
| Forestry | pszczoły, apiarystyka, maszyny, uprawy, backpacki, mail | **Productive Bees** (pszczoły) + automatyzacja farm: **Create** / (opc.) **Thermal** / **Industrial Foregoing**; backpacki: **Sophisticated Backpacks**; poczta: **Ender Mail** (jeśli potrzebne) | ⚠️ (częściowo) |
| ForgeEssentials | serwer: permisje, warpy, /home, kit, administracja | **ForgeEssentials** (nowsze wydanie, jeśli dostępne) / alternatywnie zestaw modów utility | ✅ (brak bloków) |
| ForgeMultipart | microbloki / wiele elementów w 1 bloku | **CB Multipart** | ⚠️ (zależy od modów używających multipartów) |
| ForgeRelocation (+FMP addon) | przenoszenie bloków z TE/BE | Brak 1:1; zwykle **Create** (contraptions) + rozwiązania przenośne w docelowych modach | ❌ |
| Growthcraft (complete) | jedzenie, alkohole, fermentacja, kuchnia | **Farmer’s Delight** + **Brewin’ and Chewin’**; opcj. szeroka lista jedzenia: **Croptopia** | ⚠️ |
| IC2 (IndustrialCraft 2) | EU, kable/trafo, maszyny, rudy, reaktory | **FTB Industrial Contraptions (Forge)** jako „IC2-like” + (uzupełnienia) **Mekanism** / **Create** / **Thermal** | ⚠️ (semantycznie tak, 1:1 nie) |
| IC2 Nuclear Control | monitoring reaktorów/energetyki | **CC: Tweaked** (+ integracje) albo monitory/IO w modach energetycznych | ⚠️ / ✅ |
| iChunUtil / MobiusCore | biblioteki zależności | tylko jeśli masz iChun/Mobius-mody na 1.18.2; inaczej pomijasz | ✅ (brak bloków) |
| Jammy Furniture Reborn | meble/dekoracje | **Macaw’s Furniture**, **Handcrafted**, **Supplementaries** | ⚠️ |
| LiteLoader + litemody (Omniscience) | klient: QOL/overlay | 1.18.2: odpowiedniki jako mody Forge (nie wpływa na mapę) | ✅ (brak bloków) |
| LogisticsPipes | rury+logistyka, request, crafting w sieci | **Pipez** (transport) + **Refined Storage**/**AE2** (sieć, autocrafting) + **XNet** (routing/IO) + opcj. **Integrated Dynamics** (logika) | ⚠️ |
| Mekanism (+Generators/Tools) | tech/machines/processing | **Mekanism** (ta sama rodzina) | ⚠️ (NBТ inne, ale mapowanie naturalne) |

---

## 1) Flan’s Mod (1.7.10) → 1.18.2

### Co było na mapie (typowo)
- Garaże ze spawnerami pojazdów (entity), skrzynie/ammo, stoły warsztatowe Flana, dekoracje z content-packów.

### Proponowane zamienniki 1.18.2
- **Immersive Vehicles** — pojazdy + dekoracje/elementy transportu; ma wsparcie dla 1.18.2 (Forge).
- **[TaCZ] Timeless and Classics Zero / Guns** — broń palna + amunicja; ma wydania dla 1.18.2.
- Opcjonalnie: **Immersive Aircraft** — dodatkowe „rustic” samoloty.

### Jak mapować bloki/BE
- Flan workbenches/gun box/vehicle box → stacje craftingu w TaCZ i „workbench/parts” w Immersive Vehicles.
- Pojazdy (entity) → w 1.18.2 to inny format encji; realnie:
  - zachowujesz konstrukcję budynków,
  - a pojazdy/uzbrojenie odtwarzasz (ręcznie lub skryptem).

---

## 2) Forestry → 1.18.2  - UWAGA - konwersja nie wymagana - ignoruj

### Funkcjonalności (1.7.10)
- Pszczoły (apiary/alveary), produkty (combs, honey), maszyny (centrifuge, squeezer, fermenter, carpenter), farmy (multifarm), backpacki, czasem mail.

### Proponowane zamienniki 1.18.2 (modułowo)
**Pszczoły:**
- **Productive Bees** — system uli/pszczoły/produkty.

**Przetwórstwo i farmy:**
- **Create** — processing i automatyzacja (świetny „zamiennik fabryk”).
- (Opcjonalnie) **Thermal** / **Industrial Foregoing** — gdy chcesz GUI-maszyny „1 blok = 1 funkcja”.

**Backpacki:**
- **Sophisticated Backpacks**.

**Mail:**
- **Ender Mail** (tylko jeśli realnie potrzebujesz funkcji poczty).

### Mapowanie bloków/BE
- Apiary/Alveary → hives z Productive Bees + bloki przetwórcze (odpowiedniki centrifuge/squeezer).
- Forestry machines → Create processing (press/mixer/etc.) lub Thermal/IF.
- Multifarm → automatyczne farmy Create lub maszyny IF.

---

## 3) ForgeEssentials → 1.18.2   - UWAGA - konwersja nie wymagana - ignoruj

To mod serwerowy (komendy, permisje, warpy).  
**Nie mapuje się na bloki**, więc nie wpływa na konwersję chunków.

---

## 4) ForgeMultipart / ForgeRelocation → 1.18.2

### ForgeMultipart
- Zamiennik: **CB Multipart** (biblioteka multipartów na 1.18.2) - konieczne perfekcyjne przekonwertowanie mikrobloków

### ForgeRelocation (+FMP)
- Brak prostego 1:1 w 1.18.2.
- Najbliżej funkcjonalnie: **Create** (contraptions), ale to inna mechanika i nie przeniesie każdej BE jak „relocation”.

---

## 5) Growthcraft (complete) → 1.18.2

### Zamiennik 1.18.2
- **Farmer’s Delight** — system gotowania i jedzenia.
- **Brewin’ and Chewin’** — fermentacja/napoje (keg), sery, itd.
- Opcjonalnie: **Croptopia** — dużo upraw i jedzenia.

### Mapowanie
- Growthcraft fermenters/presses → Brewin’ and Chewin’ (keg) + Create processing.
- Cropy/food → Croptopia + Farmer’s Delight.

---

## 6) IC2 + IC2 Nuclear Control → 1.18.2

### IC2 (1.7.10) — kluczowe klasy funkcji
- EU + kable/trafo + magazyny energii.
- Maszyny do obróbki rud i produkcji.
- Reaktor nuklearny + komponenty.
- Narzędzia/pancerze elektryczne, automatyzacja.

### Proponowany „rdzeń IC2-like” w 1.18.2
- **FTB Industrial Contraptions (Forge)** — najbliższy klimatowo/narzędziowo do IC2 w 1.18.2.
- Uzupełnienie: **Mekanism** (processing/transport/energia) i/lub **Create**.

### Nuclear Control (monitoring)
- **CC: Tweaked** (komputery) + integracje (np. peripheral addony) do monitoringu.
- Alternatywnie: monitoring przez redstone/IO/porty w samych modach energetycznych.

### Mapowanie bloków/BE
- IC2 EU-kable → zdecyduj, czy zostajesz w „IC2-like” (FTBIC), czy przechodzisz w FE-ekosystem (Mekanism/Thermal/Create).  
- IC2 maszyny → analogiczne klasy maszyn w FTBIC/Mekanism (semantycznie), ale NBT będzie inne.
- IC2 reaktor → brak 1:1; zachowujesz budynek/układ, a „serce” reaktora odtwarzasz w docelowym systemie (np. Mekanism fission lub osobny mod reaktorowy).

---

## 7) LogisticsPipes → 1.18.2

### Zamienniki 1.18.2
- **Pipez** — transport item/fluid/energy (najprostszy zamiennik „rur”).
- **AE2** lub **Refined Storage** — request/crafting/sieci magazynowe.
- **XNet** — elastyczny routing/IO.
- Opcjonalnie: **Integrated Dynamics** — logika warunkowa i „programowalne” zachowanie sieci.

### Mapowanie
- LP pipes+modules → Pipez (transport) + XNet/ID (routing/warunki), albo pełne przejście na sieć AE2/RS (logistyka „wirtualna”).
- LP request/crafting → autocrafting w AE2/RS.

---

## 8) Mekanism (+Generators/Tools) → 1.18.2

To najłatwiejszy przypadek „stary → nowy”:
- **Mekanism** ma wersje na 1.18.2 (Forge), więc mapowanie jest naturalne (ta sama rodzina bloków).

Uwaga: dla „bezstratnej” migracji maszyn nadal potrzebujesz remappera NBT, ale semantycznie jest to najlepsza możliwa para.

---

## 9) Jammy Furniture Reborn → 1.18.2

### Zamienniki
- **Macaw’s Furniture**, **Handcrafted**, **Supplementaries** (dobór pod styl mapy).

### Mapowanie
- Meble są dekoracyjne → mapuj kategoriami (krzesło/stół/szafka/itp.) na odpowiedniki w wybranym modzie.

---

## 10) LiteLoader / Omniscience / MobiusCore / iChunUtil → 1.18.2 - UWAGA - konwersja nie wymagana - ignoruj

To narzędzia klientowe/biblioteczne — **nie zostawiają bloków w chunkach**.  
Dla konwersji mapy: możesz je pominąć i dobrać QOL osobno.

---

## Minimalny „rdzeń” 1.18.2 dla cz3 (propozycja)

Jeśli chcesz maksymalnie pokryć funkcje cz3 i mieć bazę pod mapowanie:

- Automatyzacja/processing: **Create**
- Transport i routing: **Pipez** + **XNet**
- Magazyn + crafting: **AE2** *lub* **Refined Storage**
- Tech: **FTB Industrial Contraptions** + **Mekanism**
- Rolnictwo/food: **Farmer’s Delight** + **Brewin’ and Chewin’** (+ opcj. **Croptopia**)
- Pszczoły: **Productive Bees**
- Multipart: **CB Multipart** (jeśli potrzebne)
- Flan replacement: **Immersive Vehicles** + **TaCZ** (+ opcj. Immersive Aircraft)
- Dekoracje: **Macaw’s Furniture** / **Handcrafted** / **Supplementaries**

---

## Notatka o „bezstratnej” migracji block entities

Nawet gdy istnieje „ten sam mod” (np. Mekanism), różnica między 1.7.10 (legacy ID/metadata + TileEntity NBT) a 1.18.2 (blockstates + registry + DataFixers) oznacza, że:

- **mapowanie semantyczne** (ten dokument) to dopiero baza,
- a **realna bezstratna migracja BE** wymaga narzędzia, które:
  1) odczyta stare chunki (blok+meta+NBT),
  2) przepisze na nowe blockstates + nowe NBT (dla docelowych modów),
  3) zapisze świat w formacie zjadliwym dla 1.18.2.

