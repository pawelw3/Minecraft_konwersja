package com.maciej916.indreb.common.block.impl.machines.canning_machine;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.progress.GuiProgressArrow;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenCanningMachine extends BetterScreen<ContainerCanningMachine> {
   public ScreenCanningMachine(ContainerCanningMachine container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      BlockEntityCanningMachine be = (BlockEntityCanningMachine)this.getBlockEntity();
      this.addRenderableOnlyComponent(new GuiProgressArrow(this, 76, 35, be.progress));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/canning_machine.png");
   }
}
