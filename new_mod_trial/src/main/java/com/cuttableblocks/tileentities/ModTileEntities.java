package com.cuttableblocks.tileentities;

import cpw.mods.fml.common.registry.GameRegistry;

public class ModTileEntities {
    
    public static void registerTileEntities() {
        GameRegistry.registerTileEntity(TileEntityCuttable.class, "cuttableblocks:cuttable_te");
    }
}
