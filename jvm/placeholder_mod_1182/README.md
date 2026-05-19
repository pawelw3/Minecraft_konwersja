# Conversion Placeholders

Forge 1.18.2 utility mod for the Minecraft 1.7.10 -> 1.18.2 conversion project.

The mod registers one visible placeholder block and one BlockEntity. Converters can place it when a legacy TileEntity is not converted yet. The BlockEntity stores source metadata and the original NBT so the data remains recoverable from the target world.

Build from repository root with any Gradle 7.4+ wrapper/install:

```powershell
gradle -p jvm\placeholder_mod_1182 build
```

In this workspace the 1.18.2 EnderStorage checkout has a compatible wrapper, so this verified command works:

```powershell
mod_src\118\actual_src\1.18.2\EnderStorage\repo\gradlew.bat -p jvm\placeholder_mod_1182 build --no-daemon --console=plain
```

Do not use `jvm\worker\gradlew.bat` for this project while it points at Gradle 7.1.1; that wrapper does not run reliably under JDK 17. The produced jar is written to `jvm/placeholder_mod_1182/build/libs/`.
