package com.maciej916.indreb.common.block.impl.machines.iron_furnace;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.progress.GuiProgressArrow;
import com.maciej916.indreb.common.screen.progress.GuiProgressFuel;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenIronFurnace extends BetterScreen<ContainerIronFurnace> {
   public ScreenIronFurnace(ContainerIronFurnace container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      this.addRenderableOnlyComponent(new GuiProgressArrow(this, 79, 35, ((BlockEntityIronFurnace)this.getBlockEntity()).smelting));
      this.addRenderableOnlyComponent(new GuiProgressFuel(this, 56, 35, ((BlockEntityIronFurnace)this.getBlockEntity()).fuel));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/iron_furnace.png");
   }
}
