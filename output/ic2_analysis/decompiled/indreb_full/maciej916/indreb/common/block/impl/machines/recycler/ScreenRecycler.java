package com.maciej916.indreb.common.block.impl.machines.recycler;

import com.maciej916.indreb.common.screen.BetterScreen;
import com.maciej916.indreb.common.screen.progress.GuiProgressRecycler;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

public class ScreenRecycler extends BetterScreen<ContainerRecycler> {
   public ScreenRecycler(ContainerRecycler container, Inventory inv, Component name) {
      super(container, inv, name);
   }

   public void m_7856_() {
      super.m_7856_();
      this.addRenderableOnlyComponent(new GuiProgressRecycler(this, 71, 35, ((BlockEntityRecycler)this.getBlockEntity()).progress));
      this.drawComponents(true);
   }

   public ResourceLocation getGuiLocation() {
      return new ResourceLocation("indreb", "textures/gui/container/recycler.png");
   }
}
