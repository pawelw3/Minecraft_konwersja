# Zadanie 1: Analiza bloków i tile/block entities — ComputerCraft 1.7.10 → CC:Tweaked 1.18.2

## Spis treści
- [1.7.10 — Bloki](#1710--bloki)
- [1.7.10 — Tile Entities](#1710--tile-entities)
- [1.18.2 — Bloki](#1182--bloki)
- [1.18.2 — Block Entities](#1182--block-entities)
- [Porównanie 1.7.10 vs 1.18.2](#porównanie-1710-vs-1182)
- [Tabela podsumowująca registry names](#tabela-podsumowująca-registry-names)

---

## 1.7.10 — Bloki

### `computercraft:computer` (BlockComputer)
- **Typ:** Block
- **Wersja:** 1.7.10
- **Registry names:**
  - Block registry: `"computercraft:computer"`
  - TileEntity registry: `"computercraft : computer"`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `dan200.computercraft.shared.computer.blocks.BlockComputer`
- **Opis działania:** Podstawowy blok komputera. Wariant Normal (meta 0-7) / Advanced (meta 8-15) rozróżniany przez metadata. Meta & 0x7 to kierunek (N/S/W/E, Y wymuszony na NORTH). Advanced computer ma większą rozdzielczość ekranu i więcej kolorów.
- **Dowody z internetu:**
  - Źródło: https://tweaked.cc/peripheral/computer.html — Komputer w CC:Tweaked działa identycznie jak w 1.7.10, uruchamia skrypty Lua (CraftOS).
- **Dowód z kodu (rejestracja):**
  - Plik: `ComputerCraftProxyCommon.java`
  ```java
  ComputerCraft.Blocks.computer = new BlockComputer();
  registry.register( ComputerCraft.Blocks.computer.setRegistryName( new ResourceLocation( ComputerCraft.MOD_ID, "computer" ) ) );
  ```
- **Dowód z kodu (logika):**
  - Plik: `BlockComputer.java`
  ```java
  public int getMetaFromState( IBlockState state )
  {
      int meta = state.getValue( Properties.FACING ).getIndex();
      if( state.getValue( Properties.ADVANCED ) ) meta += 8;
      return meta;
  }
  ```

### `computercraft:peripheral` (BlockPeripheral)
- **Typ:** Block
- **Wersja:** 1.7.10
- **Registry names:**
  - Block registry: `"computercraft:peripheral"`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `dan200.computercraft.shared.peripheral.common.BlockPeripheral`
- **Opis działania:** Wielofunkcyjny blok peryferyjny. Jeden block ID obsługuje wiele urządzeń rozróżnianych przez metadata: Wireless Modem, Disk Drive, Monitor, Printer, Advanced Monitor, Speaker.
- **Dowody z internetu:**
  - Źródło: https://tweaked.cc/peripheral/ — Dokumentacja CC:Tweaked opisuje peryferia jako osobne bloki (w 1.18.2), ale w 1.7.10 były zgrupowane pod jednym ID.
- **Dowód z kodu (rejestracja):**
  - Plik: `ComputerCraftProxyCommon.java`
  ```java
  ComputerCraft.Blocks.peripheral = new BlockPeripheral();
  registry.register( ComputerCraft.Blocks.peripheral.setRegistryName( new ResourceLocation( ComputerCraft.MOD_ID, "peripheral" ) ) );
  ```
- **Dowód z kodu (logika / metadata mapping):**
  - Plik: `BlockPeripheral.java`
  ```java
  if( meta >= 2 && meta <= 5 )      // DiskDrive
  else if( meta <= 9 )              // WirelessModem (0=down, 1=up, 6-9=horizontal)
  else if( meta == 10 )             // Monitor
  else if( meta == 11 )             // Printer
  else if( meta == 12 )             // AdvancedMonitor
  else if (meta == 13)              // Speaker
  ```

### `computercraft:cable` (BlockCable)
- **Typ:** Block
- **Wersja:** 1.7.10
- **Registry names:**
  - Block registry: `"computercraft:cable"`
  - TileEntity registry: `"computercraft : wiredmodem"`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `dan200.computercraft.shared.peripheral.common.BlockCable`
- **Opis działania:** Kabel sieciowy / przewodowy modem. Meta 0-5 = modem bez kabla, 6-11 = modem + kabel, 13 = sam kabel. Umożliwia łączenie peryferii w sieć.
- **Dowody z internetu:**
  - Źródło: https://tweaked.cc/peripheral/modem.html — Wired modem w CC:Tweaked zachowuje tę samą funkcjonalność sieciową.
- **Dowód z kodu (logika):**
  - Plik: `BlockCable.java`
  ```java
  if( meta < 6 ) { cable=false; modem=fromFacing(meta); }
  else if( meta < 12 ) { cable=true; modem=fromFacing(meta-6); }
  else if( meta == 13 ) { cable=true; modem=None; }
  ```

### `computercraft:command_computer` (BlockCommandComputer)
- **Typ:** Block
- **Wersja:** 1.7.10
- **Registry names:**
  - Block registry: `"computercraft:command_computer"`
  - TileEntity registry: `"computercraft : command_computer"`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `dan200.computercraft.shared.computer.blocks.BlockCommandComputer`
- **Opis działania:** Komputer trybu kreatywnego/admina. Może wykonywać komendy serwera (`commands.exec`). Dostępny tylko w trybie creative.
- **Dowody z internetu:**
  - Źródło: https://tweaked.cc/peripheral/command_computer.html — Command computer w CC:Tweaked zachowuje identyczną funkcjonalność.
- **Dowód z kodu (rejestracja):**
  ```java
  ComputerCraft.Blocks.commandComputer = new BlockCommandComputer();
  registry.register( ...setRegistryName( new ResourceLocation( ComputerCraft.MOD_ID, "command_computer" ) ) );
  ```

### `computercraft:advanced_modem` (BlockAdvancedModem)
- **Typ:** Block
- **Wersja:** 1.7.10
- **Registry names:**
  - Block registry: `"computercraft:advanced_modem"`
  - TileEntity registry: `"computercraft : advanced_modem"`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.BlockAdvancedModem`
- **Opis działania:** Ender modem (zaawansowany modem bezprzewodowy). Umożliwia komunikację międzywymiarową i na większe odległości niż zwykły wireless modem.
- **Dowody z internetu:**
  - Źródło: https://tweaked.cc/peripheral/modem.html — Advanced wireless modem w 1.18.2 zastępuje ender modem z 1.7.10.

### `computercraft:turtle` / `turtle_expanded` / `turtle_advanced`
- **Typ:** Block
- **Wersja:** 1.7.10
- **Registry names:**
  - Block registry: `"computercraft:turtle"`, `"computercraft:turtle_expanded"`, `"computercraft:turtle_advanced"`
  - TileEntity registry: `"computercraft : turtle"`, `"computercraft : turtleex"`, `"computercraft : turtleadv"`
  - **Ma prefiks moda:** TAK
- **Klasa Java:** `dan200.computercraft.shared.turtle.blocks.BlockTurtle`
- **Opis działania:** Żółw (mobilny komputer z inventory i slotami na narzędzia). `turtle` = legacy/normal, `turtle_expanded` = normal z rozszerzonym inventory, `turtle_advanced` = advanced. Każdy ma osobny block ID i osobny TE registry string.
- **Dowody z internetu:**
  - Źródło: https://tweaked.cc/peripheral/turtle.html — Turtle w CC:Tweaked zachowuje te same funkcje (move, dig, place, equip).
- **Dowód z kodu (rejestracja):**
  - Plik: `CCTurtleProxyCommon.java`
  ```java
  ComputerCraft.Blocks.turtle = BlockTurtle.createTurtleBlock();
  registry.register( ...setRegistryName( new ResourceLocation( ComputerCraft.MOD_ID, "turtle" ) ) );
  ComputerCraft.Blocks.turtleExpanded = BlockTurtle.createTurtleBlock();
  registry.register( ...setRegistryName( new ResourceLocation( ComputerCraft.MOD_ID, "turtle_expanded" ) ) );
  ComputerCraft.Blocks.turtleAdvanced = BlockTurtle.createTurtleBlock();
  registry.register( ...setRegistryName( new ResourceLocation( ComputerCraft.MOD_ID, "turtle_advanced" ) ) );
  ```

---

## 1.7.10 — Tile Entities

### `computercraft : computer` (TileComputer)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : computer"` (UWAGA: spacja wokół dwukropka!)
- **Klasa Java:** `dan200.computercraft.shared.computer.blocks.TileComputer`
- **Opis działania:** Tile entity komputera (normalnego lub advanced). Przechowuje `computerID`, `label`, stan włączenia (`on`). Dziedziczy z `TileComputerBase` który obsługuje NBT.
- **Dowód z kodu (rejestracja):**
  ```java
  GameRegistry.registerTileEntity( TileComputer.class, ComputerCraft.LOWER_ID + " : " + "computer" );
  ```
- **Dowód z kodu (NBT):**
  - Plik: `TileComputerBase.java`
  ```java
  if( m_computerID >= 0 ) nbttagcompound.setInteger( "computerID", m_computerID );
  if( m_label != null ) nbttagcompound.setString( "label", m_label );
  nbttagcompound.setBoolean( "on", m_on );
  ```

### `computercraft : diskdrive` (TileDiskDrive)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : diskdrive"`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.diskdrive.TileDiskDrive`
- **Opis działania:** Stacja dysków. Przechowuje ItemStack dyskietki w polu `item`. Umożliwia odczyt/zapis plików na dyskietce.
- **Dowód z kodu (NBT):**
  ```java
  if( nbttagcompound.hasKey( "item" ) )
  {
      NBTTagCompound item = nbttagcompound.getCompoundTag( "item" );
      m_diskStack = new ItemStack( item );
  }
  ```

### `computercraft : wirelessmodem` (TileWirelessModem)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : wirelessmodem"`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.TileWirelessModem`
- **Opis działania:** Modem bezprzewodowy. Brak dodatkowego NBT poza dziedziczonym z `TilePeripheralBase` (`dir`, `anim`, `label`).

### `computercraft : monitor` (TileMonitor)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : monitor"`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.monitor.TileMonitor`
- **Opis działania:** Monitor / zaawansowany monitor. Przechowuje indeksy wieloblokowego ekranu (`xIndex`, `yIndex`, `width`, `height`) oraz kierunek (`dir`). Monitory łączą się w większe ekrany.
- **Dowód z kodu (NBT):**
  ```java
  nbttagcompound.setInteger( "xIndex", m_xIndex );
  nbttagcompound.setInteger( "yIndex", m_yIndex );
  nbttagcompound.setInteger( "width", m_width );
  nbttagcompound.setInteger( "height", m_height );
  nbttagcompound.setInteger( "dir", m_dir );
  ```

### `computercraft : ccprinter` (TilePrinter)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : ccprinter"`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.printer.TilePrinter`
- **Opis działania:** Drukarka. Przechowuje inventory (papier, tusz), stan drukowania (`printing`), tytuł strony (`pageTitle`) oraz zawartość strony w terminalu.
- **Dowód z kodu (NBT):**
  ```java
  nbttagcompound.setBoolean( "printing", m_printing );
  nbttagcompound.setString( "pageTitle", m_pageTitle );
  m_page.writeToNBT( nbttagcompound );
  // + Items (inventory)
  ```

### `computercraft : wiredmodem` (TileCable)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : wiredmodem"`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.TileCable`
- **Opis działania:** Przewodowy modem / kabel. Przechowuje `peripheralAccess` (boolean) i `peripheralID` (int). Obsługuje podłączanie peryferii do sieci.
- **Dowód z kodu (NBT):**
  ```java
  m_peripheralAccessAllowed = nbttagcompound.getBoolean( "peripheralAccess" );
  m_attachedPeripheralID = nbttagcompound.getInteger( "peripheralID" );
  ```

### `computercraft : command_computer` (TileCommandComputer)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : command_computer"`
- **Klasa Java:** `dan200.computercraft.shared.computer.blocks.TileCommandComputer`
- **Opis działania:** Tile entity command computera. Nie posiada własnego NBT — dziedziczy całość z `TileComputerBase` (`computerID`, `label`, `on`).

### `computercraft : advanced_modem` (TileAdvancedModem)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : advanced_modem"`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.TileAdvancedModem`
- **Opis działania:** Zaawansowany (ender) modem. Brak własnego NBT — dziedziczy z `TileModemBase` → `TilePeripheralBase`.

### `computercraft : speaker` (TileSpeaker)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : speaker"`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.speaker.TileSpeaker`
- **Opis działania:** Głośnik. Odtwarza dźwięki i muzykę przez API `speaker`. Brak własnego NBT — dziedziczy z `TilePeripheralBase`.

### `computercraft : turtle` (TileTurtle)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : turtle"`
- **Klasa Java:** `dan200.computercraft.shared.turtle.blocks.TileTurtle`
- **Opis działania:** Żółw (legacy/normal). Przechowuje inventory (`Items`), kierunek (`dir`), wybrane slot (`selectedSlot`), poziom paliwa (`fuelLevel`), kolory (`colour`), nakładkę (`overlay_mod`/`overlay_path`), upgrady (`leftUpgrade`, `rightUpgrade`, `leftUpgradeNBT`, `rightUpgradeNBT`).
- **Dowód z kodu (NBT — TurtleBrain):**
  ```java
  nbttagcompound.setInteger( "dir", m_direction.getIndex() );
  nbttagcompound.setInteger( "selectedSlot", m_selectedSlot );
  nbttagcompound.setInteger( "fuelLevel", m_fuelLevel );
  if( leftUpgradeID != null ) nbttagcompound.setString( "leftUpgrade", leftUpgradeID );
  if( rightUpgradeID != null ) nbttagcompound.setString( "rightUpgrade", rightUpgradeID );
  if( m_colourHex != -1 ) nbttagcompound.setInteger( "colour", m_colourHex );
  if( m_overlay != null ) {
      nbttagcompound.setString( "overlay_mod", m_overlay.getResourceDomain() );
      nbttagcompound.setString( "overlay_path", m_overlay.getResourcePath() );
  }
  if( m_upgradeNBTData.containsKey(Left) ) nbttagcompound.setTag( "leftUpgradeNBT", ... );
  if( m_upgradeNBTData.containsKey(Right) ) nbttagcompound.setTag( "rightUpgradeNBT", ... );
  ```

### `computercraft : turtleex` (TileTurtleExpanded)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : turtleex"`
- **Klasa Java:** `dan200.computercraft.shared.turtle.blocks.TileTurtleExpanded`
- **Opis działania:** Żółw normalny z rozszerzonym inventory. Ten sam NBT co TileTurtle.

### `computercraft : turtleadv` (TileTurtleAdvanced)
- **Typ:** TileEntity
- **Wersja:** 1.7.10
- **Registry string:** `"computercraft : turtleadv"`
- **Klasa Java:** `dan200.computercraft.shared.turtle.blocks.TileTurtleAdvanced`
- **Opis działania:** Zaawansowany żółw. Ten sam NBT co TileTurtle, ale wyższy limit paliwa.

---

## 1.18.2 — Bloki

### `computercraft:computer_normal`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:computer_normal`
- **BlockEntity registry:** `computercraft:computer_normal`
- **Klasa Java:** `dan200.computercraft.shared.computer.blocks.ComputerBlock`
- **Opis działania:** Standardowy komputer (kamienny). BlockState: `facing` (N/S/W/E), `state` (off/on/blinking). Używa `ComputerBlockEntity`.

### `computercraft:computer_advanced`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:computer_advanced`
- **BlockEntity registry:** `computercraft:computer_advanced`
- **Klasa Java:** `dan200.computercraft.shared.computer.blocks.ComputerBlock`
- **Opis działania:** Zaawansowany komputer (złoty). Wyższa rozdzielczość ekranu. Używa `ComputerBlockEntity`.

### `computercraft:computer_command`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:computer_command`
- **BlockEntity registry:** `computercraft:computer_command`
- **Klasa Java:** `dan200.computercraft.shared.computer.blocks.CommandComputerBlock`
- **Opis działania:** Command computer (creative). Używa tej samej klasy `ComputerBlockEntity` co zwykłe komputery, ale z `ComputerFamily.COMMAND`.

### `computercraft:turtle_normal`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:turtle_normal`
- **BlockEntity registry:** `computercraft:turtle_normal`
- **Klasa Java:** `dan200.computercraft.shared.turtle.blocks.TurtleBlock`
- **Opis działania:** Standardowy żółw. BlockState: `facing` (HORIZONTAL_FACING). Używa `TurtleBlockEntity`.

### `computercraft:turtle_advanced`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:turtle_advanced`
- **BlockEntity registry:** `computercraft:turtle_advanced`
- **Klasa Java:** `dan200.computercraft.shared.turtle.blocks.TurtleBlock`
- **Opis działania:** Zaawansowany żółw. Wyższy limit paliwa, odporność na wybuchy. Używa `TurtleBlockEntity`.

### `computercraft:speaker`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:speaker`
- **BlockEntity registry:** `computercraft:speaker`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.speaker.SpeakerBlock`
- **Opis działania:** Głośnik. BlockState: `facing`. Odtwarza dźwięki przez API `speaker`.

### `computercraft:disk_drive`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:disk_drive`
- **BlockEntity registry:** `computercraft:disk_drive`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.diskdrive.DiskDriveBlock`
- **Opis działania:** Stacja dysków. BlockState: `facing`, `state` (empty/full/invalid). Używa `DiskDriveBlockEntity`.

### `computercraft:printer`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:printer`
- **BlockEntity registry:** `computercraft:printer`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.printer.PrinterBlock`
- **Opis działania:** Drukarka. BlockState: `facing`, `top`, `bottom`. Używa `PrinterBlockEntity`.

### `computercraft:monitor_normal`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:monitor_normal`
- **BlockEntity registry:** `computercraft:monitor_normal`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.monitor.MonitorBlock`
- **Opis działania:** Standardowy monitor. BlockState: `facing`, `orientation` (up/down/north), `state` (krawędzie). Używa `MonitorBlockEntity`.

### `computercraft:monitor_advanced`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:monitor_advanced`
- **BlockEntity registry:** `computercraft:monitor_advanced`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.monitor.MonitorBlock`
- **Opis działania:** Zaawansowany monitor (więcej kolorów). Używa `MonitorBlockEntity`.

### `computercraft:wireless_modem_normal`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:wireless_modem_normal`
- **BlockEntity registry:** `computercraft:wireless_modem_normal`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.wireless.WirelessModemBlock`
- **Opis działania:** Standardowy modem bezprzewodowy. BlockState: `facing`, `on`. Zasięg 64 bloki. Używa `WirelessModemBlockEntity`.

### `computercraft:wireless_modem_advanced`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:wireless_modem_advanced`
- **BlockEntity registry:** `computercraft:wireless_modem_advanced`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.wireless.WirelessModemBlock`
- **Opis działania:** Zaawansowany modem bezprzewodowy. Zasięg większy, może wysyłać do pocket computers w całym wymiarze. Używa `WirelessModemBlockEntity`.

### `computercraft:wired_modem_full`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:wired_modem_full`
- **BlockEntity registry:** `computercraft:wired_modem_full`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.wired.WiredModemFullBlock`
- **Opis działania:** Samodzielny blok przewodowego modemu (pełny blok, nie kabel). Używa `WiredModemFullBlockEntity`.

### `computercraft:cable`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:cable`
- **BlockEntity registry:** `computercraft:cable`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.wired.CableBlock`
- **Opis działania:** Kabel sieciowy. BlockState: `cable` (boolean), `modem` (variant), `north`/`south`/`east`/`west`/`up`/`down` (połączenia). Może mieć dołączony modem. Używa `CableBlockEntity`.

### `computercraft:lectern`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:lectern`
- **BlockEntity registry:** `computercraft:lectern`
- **Klasa Java:** `dan200.computercraft.shared.lectern.CustomLecternBlock`
- **Opis działania:** Niestandardowa katedra trzymająca pocket computer. Nie istnieje w 1.7.10 — nowy blok w CC:Tweaked.

### `computercraft:redstone_relay`
- **Typ:** Block
- **Wersja:** 1.18.2
- **Registry name:** `computercraft:redstone_relay`
- **BlockEntity registry:** `computercraft:redstone_relay`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.redstone.RedstoneRelayBlock`
- **Opis działania:** Przekaźnik redstone transmitujący sygnały bundlowane przez sieć przewodową. Nie istnieje w 1.7.10.

---

## 1.18.2 — Block Entities

### `computercraft:computer_normal` / `computer_advanced` / `computer_command` (ComputerBlockEntity)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry string:** `computercraft:computer_normal`, `computercraft:computer_advanced`, `computercraft:computer_command`
- **Klasa Java:** `dan200.computercraft.shared.computer.blocks.ComputerBlockEntity`
- **Opis działania:** Bazowa klasa `AbstractComputerBlockEntity` zapisuje: `ComputerId` (int), `Label` (string), `On` (boolean). Wszystkie trzy warianty używają tej samej klasy BE.
- **Dowód z kodu (NBT):**
  ```java
  private static final String NBT_ID = "ComputerId";
  private static final String NBT_LABEL = "Label";
  private static final String NBT_ON = "On";
  
  if (computerID >= 0) nbt.putInt(NBT_ID, computerID);
  if (label != null) nbt.putString(NBT_LABEL, label);
  nbt.putBoolean(NBT_ON, on);
  ```

### `computercraft:turtle_normal` / `turtle_advanced` (TurtleBlockEntity)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry string:** `computercraft:turtle_normal`, `computercraft:turtle_advanced`
- **Klasa Java:** `dan200.computercraft.shared.turtle.blocks.TurtleBlockEntity`
- **Opis działania:** Przechowuje inventory (`Items` przez `ContainerHelper`), stan żółwia z `TurtleBrain`: `RightUpgrade`, `RightUpgradeNbt`, `LeftUpgrade`, `LeftUpgradeNbt`, `Fuel`, `Overlay`, `Slot`, `Owner` (UUID + nazwa), `Colour`.
- **Dowód z kodu (NBT):**
  ```java
  public static final String NBT_RIGHT_UPGRADE = "RightUpgrade";
  public static final String NBT_RIGHT_UPGRADE_DATA = "RightUpgradeNbt";
  public static final String NBT_LEFT_UPGRADE = "LeftUpgrade";
  public static final String NBT_LEFT_UPGRADE_DATA = "LeftUpgradeNbt";
  public static final String NBT_FUEL = "Fuel";
  public static final String NBT_OVERLAY = "Overlay";
  // + Owner compound with UpperId/LowerId/Name
  ```

### `computercraft:monitor_normal` / `monitor_advanced` (MonitorBlockEntity)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry string:** `computercraft:monitor_normal`, `computercraft:monitor_advanced`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.monitor.MonitorBlockEntity`
- **Opis działania:** Przechowuje `XIndex`, `YIndex`, `Width`, `Height` — współrzędne wieloblokowego ekranu.
- **Dowód z kodu (NBT):**
  ```java
  tag.putInt(NBT_X, xIndex);
  tag.putInt(NBT_Y, yIndex);
  tag.putInt(NBT_WIDTH, width);
  tag.putInt(NBT_HEIGHT, height);
  ```

### `computercraft:disk_drive` (DiskDriveBlockEntity)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry string:** `computercraft:disk_drive`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.diskdrive.DiskDriveBlockEntity`
- **Opis działania:** Przechowuje ItemStack dyskietki pod tagiem `Item`.
- **Dowód z kodu (NBT):**
  ```java
  if (!stack.isEmpty()) tag.put(NBT_ITEM, stack.save(new CompoundTag()));
  ```

### `computercraft:cable` (CableBlockEntity)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry string:** `computercraft:cable`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.wired.CableBlockEntity`
- **Opis działania:** Przechowuje `PeripheralId` i `PeripheralType` (z `WiredModemLocalPeripheral`).
- **Dowód z kodu (NBT):**
  ```java
  tag.putInt("PeripheralId", id);
  tag.putString("PeripheralType", type);
  ```

### `computercraft:printer` (PrinterBlockEntity)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry string:** `computercraft:printer`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.printer.PrinterBlockEntity`
- **Opis działania:** Przechowuje `Printing` (boolean), `PageTitle` (string), inventory (`Items`), oraz dane terminala strony.

### `computercraft:speaker` (SpeakerBlockEntity)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry string:** `computercraft:speaker`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.speaker.SpeakerBlockEntity`
- **Opis działania:** Brak stałego NBT — stan głośnika jest czysto runtime'owy.

### `computercraft:wireless_modem_normal` / `wireless_modem_advanced` (WirelessModemBlockEntity)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry string:** `computercraft:wireless_modem_normal`, `computercraft:wireless_modem_advanced`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.wireless.WirelessModemBlockEntity`
- **Opis działania:** Brak stałego NBT — stan (otwarty/zamknięty) w blockstate (`on`).

### `computercraft:wired_modem_full` (WiredModemFullBlockEntity)
- **Typ:** BlockEntity
- **Wersja:** 1.18.2
- **Registry string:** `computercraft:wired_modem_full`
- **Klasa Java:** `dan200.computercraft.shared.peripheral.modem.wired.WiredModemFullBlockEntity`
- **Opis działania:** Samodzielny blok modemu — brak stałego NBT poza ewentualnymi danymi peryferii.

---

## Porównanie 1.7.10 vs 1.18.2

### Wspólne elementy (bezpośrednie mapowanie)

| 1.7.10 | 1.18.2 | Uwagi |
|--------|--------|-------|
| `computercraft:computer` (meta 0-7 normal, 8-15 advanced) | `computercraft:computer_normal`, `computercraft:computer_advanced` | Rozdzielenie na osobne block ID |
| `computercraft:command_computer` | `computercraft:computer_command` | Nazwa zmieniona |
| `computercraft:peripheral` (meta 10 monitor) | `computercraft:monitor_normal` | Osobny block ID |
| `computercraft:peripheral` (meta 12 advanced monitor) | `computercraft:monitor_advanced` | Osobny block ID |
| `computercraft:peripheral` (meta 2-5 disk drive) | `computercraft:disk_drive` | Osobny block ID |
| `computercraft:peripheral` (meta 11 printer) | `computercraft:printer` | Osobny block ID |
| `computercraft:peripheral` (meta 0-1, 6-9 wireless modem) | `computercraft:wireless_modem_normal` | Osobny block ID |
| `computercraft:advanced_modem` | `computercraft:wireless_modem_advanced` | Zmiana nazwy: ender → advanced wireless |
| `computercraft:peripheral` (meta 13 speaker) | `computercraft:speaker` | Osobny block ID |
| `computercraft:cable` (meta 0-5 modem, 6-11 modem+cable, 13 cable) | `computercraft:cable` + `computercraft:wired_modem_full` | Cable zachowuje kabel, wired_modem_full to samodzielny modem |
| `computercraft:turtle` | `computercraft:turtle_normal` | Zmiana nazwy |
| `computercraft:turtle_expanded` | → `computercraft:turtle_normal` | Expanded nie istnieje w 1.18.2; mapujemy na normal |
| `computercraft:turtle_advanced` | `computercraft:turtle_advanced` | Bez zmian |

### Nowe w 1.18.2
- `computercraft:lectern` — katedra na pocket computer
- `computercraft:redstone_relay` — przekaźnik redstone w sieci przewodowej
- Pocket computers (`pocket_computer_normal`, `pocket_computer_advanced`) — istniały w 1.7.10 jako itemy, ale w 1.18.2 mają większą funkcjonalność

### Usunięte po 1.7.10
- `turtle_expanded` — wariant żółwia z rozszerzonym inventory zniknął; wszystkie żółwie normalne mają teraz standardowy rozmiar
- `BlockPeripheral` jako multi-block — rozpadł się na osobne block ID

### Zmiany techniczne
- **Rejestracja:** `GameRegistry.registerTileEntity(...)` → `DeferredRegister` + `RegistryObject<BlockEntityType>`
- **TileEntity → BlockEntity:** zmiana nazewnictwa klas i metod (`writeToNBT` → `saveAdditional`, `readFromNBT` → `load`)
- **NBT komputera:** `computerID` → `ComputerId`, `label` → `Label`, `on` → `On` (camelCase → PascalCase)
- **NBT żółwia:** `fuelLevel` → `Fuel`, `selectedSlot` → `Slot`, `leftUpgrade` → `LeftUpgrade`, `leftUpgradeNBT` → `LeftUpgradeNbt`, `rightUpgrade` → `RightUpgrade`, `rightUpgradeNBT` → `RightUpgradeNbt`
- **NBT monitora:** `xIndex` → `XIndex`, `yIndex` → `YIndex`, `width` → `Width`, `height` → `Height`
- **NBT drukarki:** `pageTitle` → `PageTitle`, `printing` → `Printing`
- **NBT kabla:** `peripheralAccess` → nieużywane w 1.18.2 (zastąpione przez `PeripheralId`/`PeripheralType` w `CableBlockEntity`)
- **Turtle Owner:** w 1.18.2 dodano explicit zapis właściciela (`Owner` compound z UUID)

### Mapowanie NBT (kluczowe dla konwersji)

| 1.7.10 tag | 1.18.2 tag | Element |
|------------|-----------|---------|
| `computerID` | `ComputerId` | Computer/Turtle |
| `label` | `Label` | Computer/Turtle |
| `on` | `On` | Computer/Turtle |
| `dir` | — | Computer/Turtle (teraz w blockstate `facing`) |
| `Items` | `Items` | Turtle/Printer (bez zmian) |
| `fuelLevel` | `Fuel` | Turtle |
| `selectedSlot` | `Slot` | Turtle |
| `leftUpgrade` | `LeftUpgrade` | Turtle |
| `leftUpgradeNBT` | `LeftUpgradeNbt` | Turtle |
| `rightUpgrade` | `RightUpgrade` | Turtle |
| `rightUpgradeNBT` | `RightUpgradeNbt` | Turtle |
| `colour` | `Colour` | Turtle |
| `overlay_mod` + `overlay_path` | `Overlay` (ResourceLocation string) | Turtle |
| `xIndex` | `XIndex` | Monitor |
| `yIndex` | `YIndex` | Monitor |
| `width` | `Width` | Monitor |
| `height` | `Height` | Monitor |
| `dir` | — | Monitor (teraz w blockstate `orientation`/`facing`) |
| `item` | `Item` | Disk Drive |
| `printing` | `Printing` | Printer |
| `pageTitle` | `PageTitle` | Printer |
| `peripheralAccess` | — | Cable (archaiczne) |
| `peripheralID` | `PeripheralId` | Cable |

---

## Tabela podsumowująca registry names

### 1.7.10 Tile Entities

| Element | Klasa Java | Registry String | Ma prefiks? |
|---------|-----------|-----------------|-------------|
| Computer | TileComputer | `"computercraft : computer"` | TAK (z spacją!) |
| Disk Drive | TileDiskDrive | `"computercraft : diskdrive"` | TAK (z spacją!) |
| Wireless Modem | TileWirelessModem | `"computercraft : wirelessmodem"` | TAK (z spacją!) |
| Monitor | TileMonitor | `"computercraft : monitor"` | TAK (z spacją!) |
| Printer | TilePrinter | `"computercraft : ccprinter"` | TAK (z spacją!) |
| Wired Modem / Cable | TileCable | `"computercraft : wiredmodem"` | TAK (z spacją!) |
| Command Computer | TileCommandComputer | `"computercraft : command_computer"` | TAK (z spacją!) |
| Advanced Modem | TileAdvancedModem | `"computercraft : advanced_modem"` | TAK (z spacją!) |
| Speaker | TileSpeaker | `"computercraft : speaker"` | TAK (z spacją!) |
| Turtle | TileTurtle | `"computercraft : turtle"` | TAK (z spacją!) |
| Turtle Expanded | TileTurtleExpanded | `"computercraft : turtleex"` | TAK (z spacją!) |
| Turtle Advanced | TileTurtleAdvanced | `"computercraft : turtleadv"` | TAK (z spacją!) |

> **UWAGA KRYTYCZNA:** Wszystkie registry stringi w 1.7.10 mają **spację** wokół dwukropka (`"computercraft : computer"`), nie `"computercraft:computer"`! Jest to wynik konstrukcji `ComputerCraft.LOWER_ID + " : " + "nazwa"` w kodzie źródłowym.

### 1.18.2 Block Entities

| Element | Klasa Java | Registry String | Ma prefiks? |
|---------|-----------|-----------------|-------------|
| Computer Normal | ComputerBlockEntity | `computercraft:computer_normal` | TAK |
| Computer Advanced | ComputerBlockEntity | `computercraft:computer_advanced` | TAK |
| Command Computer | ComputerBlockEntity | `computercraft:computer_command` | TAK |
| Turtle Normal | TurtleBlockEntity | `computercraft:turtle_normal` | TAK |
| Turtle Advanced | TurtleBlockEntity | `computercraft:turtle_advanced` | TAK |
| Speaker | SpeakerBlockEntity | `computercraft:speaker` | TAK |
| Disk Drive | DiskDriveBlockEntity | `computercraft:disk_drive` | TAK |
| Printer | PrinterBlockEntity | `computercraft:printer` | TAK |
| Monitor Normal | MonitorBlockEntity | `computercraft:monitor_normal` | TAK |
| Monitor Advanced | MonitorBlockEntity | `computercraft:monitor_advanced` | TAK |
| Wireless Modem Normal | WirelessModemBlockEntity | `computercraft:wireless_modem_normal` | TAK |
| Wireless Modem Advanced | WirelessModemBlockEntity | `computercraft:wireless_modem_advanced` | TAK |
| Wired Modem Full | WiredModemFullBlockEntity | `computercraft:wired_modem_full` | TAK |
| Cable | CableBlockEntity | `computercraft:cable` | TAK |
| Lectern | CustomLecternBlockEntity | `computercraft:lectern` | TAK |
| Redstone Relay | RedstoneRelayBlockEntity | `computercraft:redstone_relay` | TAK |

---

## Źródła

- Kod źródłowy ComputerCraft 1.75 (1.7.10): `mod_src/1710/actual_src/1.7.10/ComputerCraft/repo`
- Kod źródłowy CC:Tweaked 1.101.x (1.18.2): `mod_src/118/actual_src/1.18.2/CCTweaked/repo`
- Dokumentacja CC:Tweaked: https://tweaked.cc/
