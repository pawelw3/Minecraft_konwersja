package com.maciej916.indreb.common.block.impl.machines.fermenter;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.bar.GuiFertilizerBar;
import com.maciej916.indreb.common.screen.bar.GuiFluidBarVertical;
import com.maciej916.indreb.common.screen.bar.GuiFluidBarVerticalLarge;
import com.maciej916.indreb.common.screen.progress.GuiProgressArrow;
import com.maciej916.indreb.common.screen.progress.GuiProgressFill;
import com.maciej916.indreb.common.screen.text.GuiTextHeat;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenFermenter extends BetterScreen<ContainerFermenter> {
   public ScreenFermenter(ContainerFermenter container, Inventory inv, Component name) {
      super(container, inv, name);
      this.f_97727_ = 256;
      this.f_97731_ = 94;
   }

   public void m_7856_() {
      super.m_7856_();
      BlockEntityFermenter be = (BlockEntityFermenter)this.getBlockEntity();
      this.addRenderableOnlyComponent(new GuiProgressFill(this, 128, 39, be.progressDrain));
      this.addRenderableOnlyComponent(new GuiFluidBarVertical(this, 108, 18, be.fluidOutputStorage));
      this.addRenderableOnlyComponent(new GuiProgressArrow(this, 76, 35, be.progress));
      this.addRenderableOnlyComponent(new GuiFertilizerBar(this, 12, 74, be.progressWaste));
      this.addRenderableOnlyComponent(new GuiProgressFill(this, 14, 39, be.progressFill));
      this.addRenderableOnlyComponent(new GuiFluidBarVerticalLarge(this, 32, 18, be.fluidInputStorage));
      this.addRenderableOnlyComponent(new GuiTextHeat(this, 20, 10, 88, 82, be.heatLevel));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/fermenter.png");
   }
}
