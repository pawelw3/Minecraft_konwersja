package com.maciej916.indreb.common.block.impl.machines.fluid_enricher;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.bar.GuiFluidBarVertical;
import com.maciej916.indreb.common.screen.progress.GuiProgressArrow;
import com.maciej916.indreb.common.screen.progress.GuiProgressFill;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenFluidEnricher extends BetterScreen<ContainerFluidEnricher> {
   public ScreenFluidEnricher(ContainerFluidEnricher container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      BlockEntityFluidEnricher be = (BlockEntityFluidEnricher)this.getBlockEntity();
      this.addRenderableOnlyComponent(new GuiProgressArrow(this, 76, 35, be.progress));
      this.addRenderableOnlyComponent(new GuiFluidBarVertical(this, 52, 18, be.fluidInputStorage));
      this.addRenderableOnlyComponent(new GuiFluidBarVertical(this, 108, 18, be.fluidOutputStorage));
      this.addRenderableOnlyComponent(new GuiProgressFill(this, 128, 39, be.progressDrain));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/fluid_enricher.png");
   }
}
