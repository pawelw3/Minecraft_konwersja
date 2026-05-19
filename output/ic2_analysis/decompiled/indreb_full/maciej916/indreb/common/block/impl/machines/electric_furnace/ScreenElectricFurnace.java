package com.maciej916.indreb.common.block.impl.machines.electric_furnace;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.progress.GuiProgressArrow;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenElectricFurnace extends BetterScreen<ContainerElectricFurnace> {
   public ScreenElectricFurnace(ContainerElectricFurnace container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      this.addRenderableOnlyComponent(new GuiProgressArrow(this, 71, 35, ((BlockEntityElectricFurnace)this.getBlockEntity()).progress));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/electric_furnace.png");
   }
}
