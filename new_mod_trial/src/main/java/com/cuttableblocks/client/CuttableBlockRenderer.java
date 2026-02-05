package com.cuttableblocks.client;

import com.cuttableblocks.client.render.RenderHelper;
import com.cuttableblocks.tileentities.TileEntityCuttable;
import cpw.mods.fml.client.registry.ISimpleBlockRenderingHandler;
import net.minecraft.block.Block;
import net.minecraft.client.renderer.RenderBlocks;
import net.minecraft.client.renderer.Tessellator;
import net.minecraft.util.IIcon;
import net.minecraft.world.IBlockAccess;
import org.lwjgl.opengl.GL11;

public class CuttableBlockRenderer implements ISimpleBlockRenderingHandler {
    
    @Override
    public void renderInventoryBlock(Block block, int metadata, int modelId, RenderBlocks renderer) {
        // Render a simple cube for inventory
        Tessellator tessellator = Tessellator.instance;
        
        GL11.glTranslatef(-0.5F, -0.5F, -0.5F);
        
        IIcon icon = block.getIcon(0, metadata);
        
        // Render all 6 faces
        renderer.renderFaceYNeg(block, 0.0D, 0.0D, 0.0D, icon);
        renderer.renderFaceYPos(block, 0.0D, 0.0D, 0.0D, icon);
        renderer.renderFaceZNeg(block, 0.0D, 0.0D, 0.0D, icon);
        renderer.renderFaceZPos(block, 0.0D, 0.0D, 0.0D, icon);
        renderer.renderFaceXNeg(block, 0.0D, 0.0D, 0.0D, icon);
        renderer.renderFaceXPos(block, 0.0D, 0.0D, 0.0D, icon);
        
        GL11.glTranslatef(0.5F, 0.5F, 0.5F);
    }
    
    @Override
    public boolean renderWorldBlock(IBlockAccess world, int x, int y, int z, 
                                    Block block, int modelId, RenderBlocks renderer) {
        
        TileEntityCuttable te = (TileEntityCuttable) world.getTileEntity(x, y, z);
        if (te == null) {
            return false;
        }
        
        Block originalBlock = te.getOriginalBlock();
        if (originalBlock == null) {
            // Fallback: render as standard block
            return renderer.renderStandardBlock(block, x, y, z);
        }
        
        // Use RenderHelper to render the cut block
        return RenderHelper.renderCutBlock(renderer, block, x, y, z, te);
    }
    
    @Override
    public boolean shouldRender3DInInventory(int modelId) {
        return true;
    }
    
    @Override
    public int getRenderId() {
        return ClientProxy.cuttableRenderId;
    }
}
