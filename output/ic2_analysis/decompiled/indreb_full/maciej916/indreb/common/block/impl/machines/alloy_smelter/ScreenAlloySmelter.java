package com.maciej916.indreb.common.block.impl.machines.alloy_smelter;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.progress.GuiProgressArrow;
import com.maciej916.indreb.common.screen.progress.GuiProgressFuel;
import com.maciej916.indreb.common.screen.text.GuiTextHeat;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenAlloySmelter extends BetterScreen<ContainerAlloySmelter> {
   public ScreenAlloySmelter(ContainerAlloySmelter container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      BlockEntityAlloySmelter be = (BlockEntityAlloySmelter)this.getBlockEntity();
      this.addRenderableOnlyComponent(new GuiProgressFuel(this, 37, 41, be.heatLevel));
      this.addRenderableOnlyComponent(new GuiProgressArrow(this, 81, 33, be.progress));
      this.addRenderableOnlyComponent(new GuiTextHeat(this, 20, 10, 20, 60, be.heatLevel));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/alloy_smelter.png");
   }
}
