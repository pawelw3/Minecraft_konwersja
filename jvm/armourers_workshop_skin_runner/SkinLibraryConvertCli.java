package moe.plushie.armourers_workshop.tools;

import moe.plushie.armourers_workshop.core.skin.Skin;
import moe.plushie.armourers_workshop.core.skin.serializer.SkinFileOptions;
import moe.plushie.armourers_workshop.core.skin.serializer.SkinSerializer;
import net.minecraft.DetectedVersion;
import net.minecraft.SharedConstants;
import net.minecraft.server.Bootstrap;

import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;

public class SkinLibraryConvertCli {

    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: SkinLibraryConvertCli <source.armour> <target.armour>");
            System.exit(2);
        }

        SharedConstants.setVersion(DetectedVersion.BUILT_IN);
        Bootstrap.bootStrap();

        Path source = Path.of(args[0]);
        Path target = Path.of(args[1]);
        Files.createDirectories(target.getParent());

        Skin skin;
        try (InputStream input = Files.newInputStream(source)) {
            skin = SkinSerializer.readFromStream(null, input);
        }

        SkinFileOptions options = new SkinFileOptions();
        options.setFileVersion(SkinSerializer.Versions.LATEST);
        try (OutputStream output = Files.newOutputStream(target)) {
            SkinSerializer.writeToStream(skin, options, output);
        }
    }
}
