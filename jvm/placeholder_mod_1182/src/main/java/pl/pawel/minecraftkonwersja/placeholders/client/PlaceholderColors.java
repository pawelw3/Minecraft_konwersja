package pl.pawel.minecraftkonwersja.placeholders.client;

import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.zip.CRC32;

public final class PlaceholderColors {
    private PlaceholderColors() {
    }

    public static int[] colorsFor(String sourceMod, String sourceTeId, String sourceBlockId) {
        int[] modColors = modPalette(sourceMod);
        int beColor = colorFromHash(firstNonEmpty(sourceTeId, sourceBlockId, sourceMod, "unknown_be"), 0.62F, 0.86F);
        return new int[] {modColors[0], modColors[1], modColors[2], beColor};
    }

    private static int[] modPalette(String sourceMod) {
        String key = sourceMod == null ? "" : sourceMod.toLowerCase(Locale.ROOT);
        if (key.contains("ae2") || key.contains("appliedenergistics")) {
            return new int[] {0x4EA0FF, 0x7B5CFF, 0xCFE8FF};
        }
        if (key.contains("mekanism")) {
            return new int[] {0x2EE6D6, 0x7C8D99, 0xD7FBFF};
        }
        if (key.contains("thaum")) {
            return new int[] {0x6F43B5, 0xC99B2E, 0xB88AF0};
        }
        if (key.contains("thermal")) {
            return new int[] {0xE15D2A, 0x3BA7C9, 0xD8D8D8};
        }
        if (key.contains("buildcraft")) {
            return new int[] {0xE2B13C, 0x2B2B2B, 0x5AA1D6};
        }
        return new int[] {
            colorFromHash(sourceMod + ":0", 0.45F, 0.80F),
            colorFromHash(sourceMod + ":1", 0.50F, 0.74F),
            colorFromHash(sourceMod + ":2", 0.58F, 0.88F)
        };
    }

    private static int colorFromHash(String value, float saturation, float brightness) {
        CRC32 crc = new CRC32();
        crc.update(value.getBytes(StandardCharsets.UTF_8));
        float hue = (crc.getValue() % 360L) / 360.0F;
        return java.awt.Color.HSBtoRGB(hue, saturation, brightness) & 0xFFFFFF;
    }

    private static String firstNonEmpty(String... values) {
        for (String value : values) {
            if (value != null && !value.isEmpty()) {
                return value;
            }
        }
        return "";
    }
}
