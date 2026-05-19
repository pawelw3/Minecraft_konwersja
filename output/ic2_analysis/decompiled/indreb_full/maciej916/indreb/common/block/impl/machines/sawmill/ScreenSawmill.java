package com.maciej916.indreb.common.block.impl.machines.sawmill;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.progress.GuiProgressSawing;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenSawmill extends BetterScreen<ContainerSawmill> {
   public ScreenSawmill(ContainerSawmill container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      this.addRenderableOnlyComponent(new GuiProgressSawing(this, 71, 35, ((BlockEntitySawmill)this.getBlockEntity()).progress));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/standard_machine.png");
   }
}
