package com.maciej916.indreb.common.block.impl.machines.extractor;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.progress.GuiProgressExtracting;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenExtractor extends BetterScreen<ContainerExtractor> {
   public ScreenExtractor(ContainerExtractor container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      this.addRenderableOnlyComponent(new GuiProgressExtracting(this, 71, 35, ((BlockEntityExtractor)this.getBlockEntity()).progress));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/standard_machine.png");
   }
}
