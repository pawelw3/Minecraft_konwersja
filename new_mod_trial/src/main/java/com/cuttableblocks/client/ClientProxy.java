package com.cuttableblocks.client;

import com.cuttableblocks.CreativeTabCuttableBlocks;
import com.cuttableblocks.blocks.ModBlocks;
import com.cuttableblocks.common.CommonProxy;
import cpw.mods.fml.client.registry.RenderingRegistry;

public class ClientProxy extends CommonProxy {

    public static int cuttableRenderId;
    public static int collapsibleRenderId;

    @Override
    public void preInit() {
        super.preInit();

        CreativeTabCuttableBlocks.tabCuttableBlocks.setBackgroundImageName("item_search.png");

        // IDs must be allocated before blocks are registered (they reference them)
        cuttableRenderId   = RenderingRegistry.getNextAvailableRenderId();
        collapsibleRenderId = RenderingRegistry.getNextAvailableRenderId();
    }

    @Override
    public void init() {
        super.init();

        RenderingRegistry.registerBlockHandler(new CuttableBlockRenderer());
        RenderingRegistry.registerBlockHandler(new CollapsibleBlockRenderer());
    }
    
    @Override
    public void postInit() {
        super.postInit();
    }
}
