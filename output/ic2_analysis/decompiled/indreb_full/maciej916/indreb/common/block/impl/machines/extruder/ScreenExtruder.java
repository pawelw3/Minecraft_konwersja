package com.maciej916.indreb.common.block.impl.machines.extruder;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.bar.GuiFluidBarVertical;
import com.maciej916.indreb.common.screen.button.GuiBackwardButton;
import com.maciej916.indreb.common.screen.button.GuiForwardButton;
import com.maciej916.indreb.common.screen.progress.GuiProgressExtracting;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenExtruder extends BetterScreen<ContainerExtruder> {
   public ScreenExtruder(ContainerExtruder container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      BlockEntityExtruder be = (BlockEntityExtruder)this.getBlockEntity();
      this.addRenderableComponent(new GuiForwardButton(this, 99, 61, be.prevRecipe()));
      this.addRenderableComponent(new GuiBackwardButton(this, 65, 61, be.nextRecipe()));
      this.addRenderableOnlyComponent(new GuiProgressExtracting(this, 76, 35, be.progress));
      this.addRenderableOnlyComponent(new GuiFluidBarVertical(this, 44, 18, be.lavaStorage));
      this.addRenderableOnlyComponent(new GuiFluidBarVertical(this, 7, 18, be.waterStorage));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/extruder.png");
   }
}
