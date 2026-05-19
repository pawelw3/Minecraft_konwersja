package com.maciej916.indreb.common.block.impl.generators.generator;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.progress.GuiProgressFuel;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenGenerator extends BetterScreen<ContainerGenerator> {
   public ScreenGenerator(ContainerGenerator container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      this.addRenderableOnlyComponent(new GuiProgressFuel(this, 80, 57, ((BlockEntityGenerator)this.getBlockEntity()).progressBurn));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/generator.png");
   }
}
