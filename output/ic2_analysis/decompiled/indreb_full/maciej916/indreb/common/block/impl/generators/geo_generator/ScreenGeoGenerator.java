package com.maciej916.indreb.common.block.impl.generators.geo_generator;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.bar.GuiFluidBarVerticalLarge;
import com.maciej916.indreb.common.screen.progress.GuiProgressFill;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenGeoGenerator extends BetterScreen<ContainerGeoGenerator> {
   public ScreenGeoGenerator(ContainerGeoGenerator container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      BlockEntityGeoGenerator be = (BlockEntityGeoGenerator)this.getBlockEntity();
      this.addRenderableOnlyComponent(new GuiProgressFill(this, 62, 40, be.progressFill));
      this.addRenderableOnlyComponent(new GuiFluidBarVerticalLarge(this, 80, 19, be.fluidStorage));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/geo_generator.png");
   }
}
