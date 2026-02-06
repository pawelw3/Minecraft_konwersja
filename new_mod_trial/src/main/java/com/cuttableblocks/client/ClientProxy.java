package com.cuttableblocks.client;

import com.cuttableblocks.CreativeTabCuttableBlocks;
import com.cuttableblocks.blocks.ModBlocks;
import com.cuttableblocks.common.CommonProxy;
import cpw.mods.fml.client.registry.RenderingRegistry;

public class ClientProxy extends CommonProxy {
    
    public static int cuttableRenderId;
    
    @Override
    public void preInit() {
        super.preInit();
        
        // Set CreativeTab background image (client-side only)
        CreativeTabCuttableBlocks.tabCuttableBlocks.setBackgroundImageName("item_search.png");
        
        // Register render ID early - needed during block registration
        cuttableRenderId = RenderingRegistry.getNextAvailableRenderId();
    }
    
    @Override
    public void init() {
        super.init();
        
        // Register the actual renderer
        RenderingRegistry.registerBlockHandler(new CuttableBlockRenderer());
    }
    
    @Override
    public void postInit() {
        super.postInit();
    }
}
